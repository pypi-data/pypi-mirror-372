#!/usr/bin/env python

"""Things to consider:
extensions for future (nugget) translation suggestions with learning capability"""

from __future__ import annotations
import argparse
from collections import defaultdict
import datetime
from enum import Enum
import json
import math
import os
from pathlib import Path
import regex
import sys
from typing import List, Set, TextIO, Tuple


class GreekRoom:
    def __init__(self, lang_code: str, ref_lcode: str | None = None):
        self.corpus = defaultdict(str)  # key: snt_id, value: snt
        self.ref_corpus = defaultdict(str)  # key: snt_id, value: snt
        self.spell_checker = SpellCheckModel(lang_code)
        self.wb = WildebeestAnalysis(args)
        self.usfm_check = UsfmCheck(directory=args.dir, user=args.user, doc_config=doc_config, lang_code=lang_code)

    def check_text(self, score, snt_id_spans, free_text, user, configs, options) -> dict:
        # corpus, ref_corpus, free_text
        # with suggestion_type, evidence, probability, report, suggestion
        # Joel: "chunk"  "paragraph", "line" has a list of IDs; link between IDs (JSON format)
        # [{chunk, id, metadata}, ...] output -> ...
        # record on file: user feedback ; morph info; Greek Room directory; by language; rarely by project
        # version of json
        pass


spell_checker_src_dir = os.path.dirname(os.path.abspath(__file__))
spell_checker_root_dir = os.path.dirname(spell_checker_src_dir)
spell_checker_data_dir = os.path.join(spell_checker_root_dir, "data")
spell_checker_test_dir = os.path.join(spell_checker_root_dir, "test")

greek_room_dir = os.path.dirname(spell_checker_root_dir)
wildebeest_src_dir = os.path.join(greek_room_dir, "wildebeest", "wildebeest")
uroman_src_dir = os.path.join(greek_room_dir, "uroman", "bin")
uroman_data_dir = os.path.join(greek_room_dir, "uroman", "data")
smart_edit_distance_dir = os.path.join(greek_room_dir, "smart_edit_distance")
smart_edit_distance_src_dir = os.path.join(smart_edit_distance_dir, "src")
smart_edit_distance_data_dir = os.path.join(smart_edit_distance_dir, "data")

for src_dir in (wildebeest_src_dir, uroman_src_dir, smart_edit_distance_src_dir):
    if src_dir not in sys.path:
        sys.path.append(src_dir)

# print('Greek Room dir:', greek_room_dir)
# print('wildebeest src dir:', wildebeest_src_dir)
# print('uroman src dir:', uroman_src_dir)
# print('smart-edit-distance src dir:', smart_edit_distance_src_dir)
# print(sys.path)

from uroman import Uroman
from smart_edit_distance import SmartEditDistance
# from wb_normalize import Wildebeest

MAX_SED_COST = 1.0


def slot_value_in_double_colon_del_list(line: str, slot: str, default: str | None = None) -> str | None:
    """For a given slot, e.g. 'cost', get its value from a line such as '::s1 of course ::s2 ::cost 0.3' -> 0.3
    The value can be an empty string, as for ::s2 in the example above."""
    m = regex.match(fr'(?:.*\s)?::{slot}(|\s+\S.*?)(?:\s+::\S.*|\s*)$', line)
    return m.group(1).strip() if m else default


def words_in_snt(snt: str, output_word_edges: bool = False) -> List[str | WordEdge]:
    """May include some multi-words"""
    result = []
    for pattern in [r'(?:\pL\pM*)+', r'(\pL\pM*)+(?:-(?:\pL\pM*)+)+']:
        for m in regex.finditer(pattern, snt):
            assert(isinstance(m, regex.Match))
            txt = m.group(0)
            if output_word_edges:
                result.append(WordEdge(txt, m.start(0), m.end(0)))
            else:
                result.append(txt)
    return result


class SimpleWordEdge:
    """Contiguous edge. Handles multi-word and sub-word expressions; handles different occurrences of the same word"""
    def __init__(self, word: str, offset_start: int | None = None, offset_end: int | None = None):
        self.txt = word
        self.start = offset_start
        self.end = offset_end

    def __str__(self):
        result = self.txt
        if self.start is None:
            if self.end is not None:
                result += f' [-{self.end}]'
        elif self.end is None:
            result += f' [{self.start}-]'
        else:
            result += f' [{self.start}-{self.end}]'
        return result

    def get_txt(self):
        return self.txt


class WordEdge:
    """List of SimpleWordEdge, which allows for non-contiguous word edges"""
    # Constructor alternative accepts list of SimpleWordEdge
    # or, as a shortcut, a string (for strings typically with offsets)
    def __init__(self, arg: List[SimpleWordEdge] | str,
                 offset_start: int | None = None, offset_end: int | None = None):
        if isinstance(arg, str):
            self.edges = [SimpleWordEdge(arg, offset_start, offset_end)]
        else:
            self.edges = arg

    def __str__(self):
        return ' '.join(map(str, self.edges))

    def get_txt(self):
        return ' '.join(map(SimpleWordEdge.get_txt, self.edges))


class SpellIndex:
    """internal; for speed"""
    # Models: (1) hashing (2) prefix (3) long substring (4) drop letter
    # Caching vs. dynamic
    # Caching of word to indexes (static)
    def __init__(self, spell_check_model: SpellCheckModel):
        self.sc_model = spell_check_model
        self.word_indexed = defaultdict(bool)
        self.hash_index = defaultdict(list)  # key: index (e.g. "cmptr") value: list of words
        self.prefix_index = defaultdict(list)  # key: index (e.g. "comp") value: list of words
        self.substr_index = defaultdict(list)  # key: index (e.g. "omput") value: list of words
        self.drop_index = defaultdict(list)  # key: index (e.g. "compuer") value: list of words
        self.prefix_hash_index = defaultdict(list)  # key: index (e.g. "cmp") value: list of words
        self.hash_cache = {}  # key: word (e.g. "cypher") value: list of indexes ['sfr', 'kfr', ...]

    def index_snt(self, snt: str):
        for word in words_in_snt(snt):
            if not self.word_indexed[word]:
                lc_word = word.lower()
                rom = self.sc_model.uroman.romanize_string(lc_word, lcode=self.sc_model.lcode)
                for index_s in self.str_to_hash_indexes(rom):
                    if word not in self.hash_index[index_s]:
                        self.hash_index[index_s].append(word)
                for index_s in self.str_to_drop_indexes(lc_word):
                    if word not in self.drop_index[index_s]:
                        self.drop_index[index_s].append(word)
                for index_s in self.str_to_prefix_indexes(lc_word):
                    if word not in self.prefix_index[index_s]:
                        self.prefix_index[index_s].append(word)
                for index_s in self.str_to_substr_indexes(lc_word):
                    if word not in self.substr_index[index_s]:
                        self.substr_index[index_s].append(word)
                for index_s in self.str_to_prefix_hash_indexes(rom):
                    if word not in self.prefix_hash_index[index_s]:
                        self.prefix_hash_index[index_s].append(word)
                self.word_indexed[word] = True

    def index_spell_checker_corpus(self, spell_check_model: SpellCheckModel):
        if spell_check_model.corpus:
            for snt in spell_check_model.corpus.values():
                self.index_snt(snt)

    def combine_pre_core_post_hash_indexes(self, m, core_indexes: List[str], lc: str, rc: str,
                                           orig: str, rec: bool) -> List[str]:
        # lc, rc: left/right context; rec: recursive call; orig: original romanization
        pre, core, post = m.group(1, 2, 3)
        pre_indexes = self.str_to_hash_indexes(pre, lc=lc, rc=core+rc, rec=True)
        post_indexes = self.str_to_hash_indexes(post, lc=lc+core, rc=rc, rec=True)
        result = []
        for pre_index in pre_indexes:
            for post_index in post_indexes:
                for core_index in core_indexes:
                    result.append(pre_index + core_index + post_index)
        if not rec:
            self.hash_cache[orig] = result
        return result

    # noinspection SpellCheckingInspection
    def str_to_hash_indexes(self, rom: str, lc: str = '', rc: str = '', rec: bool = False) -> List[str]:
        orig = rom
        if lc == '' and rc == '' and (result := self.hash_cache.get(rom, None)) is not None:
            return result
        # lc, rc: left/right context
        if lc == '':
            rom = regex.sub(r'^ch?r', 'kr', rom)
        if m := regex.match(r'(.*?)(c+h?)(.*)$', rom):
            return self.combine_pre_core_post_hash_indexes(m, ['k', 's'], lc=lc, rc=rc, orig=orig, rec=rec)
        if m := regex.match(r'(.*?)(ph)(.*)$', rom):
            return self.combine_pre_core_post_hash_indexes(m, ['f', 'p'], lc=lc, rc=rc, orig=orig, rec=rec)
        if (lc == '') and (m := regex.match(r'(.*?)(kn)(.*)$', rom)):
            return self.combine_pre_core_post_hash_indexes(m, ['kn', 'n'], lc=lc, rc=rc, orig=orig, rec=rec)
        if (lc == '') and (m := regex.match(r'(.*?)(wr)(.*)$', rom)):
            return self.combine_pre_core_post_hash_indexes(m, ['fr', 'r'], lc=lc, rc=rc, orig=orig, rec=rec)
        # noinspection SpellCheckingInspection
        if m := regex.match(r'(.*?)(ight)(.*)$', rom):
            return self.combine_pre_core_post_hash_indexes(m, ['kt', 't'], lc=lc, rc=rc, orig=orig, rec=rec)
        rom = rom.replace('b', 'p')
        rom = rom.replace('d', 't')
        rom = rom.replace('ck', 'k')
        rom = rom.replace('g', 'k')
        rom = rom.replace('q', 'k')
        rom = rom.replace('v', 'f')
        rom = rom.replace('z', 's')
        rom = rom.replace('x', 'ks')
        rom = regex.sub(r'([ckprstw])h', r'\1', rom)
        if m := regex.match(r'(.*?[aeiou])(w)(.*)$', rom):
            return self.combine_pre_core_post_hash_indexes(m, ['f', ''], lc=lc, rc=rc, orig=orig, rec=rec)
        rom = regex.sub(r'(.)\1+', r'\1', rom)
        rom = rom.replace('ts', 's')
        # more to be added
        if lc == '':
            rom = regex.sub('^[aeiouy]+', 'e', rom)
        else:
            rom = regex.sub('[aeiouy]+', '', rom)
        rom = regex.sub('(?<=.)[-aeiouy]+', '', rom)
        if not rec:
            self.hash_cache[orig] = [rom]
        return [rom]

    @staticmethod
    def str_to_drop_indexes(word: str) -> List[str]:
        result = []
        for i in range(len(word)):
            result.append(word[:i] + word[i+1:])
        return result

    @staticmethod
    def str_to_prefix_indexes(word: str, prefix_length: int = 4) -> List[str]:
        return [word[:prefix_length]]

    def str_to_prefix_hash_indexes(self, rom: str, prefix_length: int = 3) -> List[str]:
        result = []
        for hash_index in self.str_to_hash_indexes(rom):
            if len(hash_index) > prefix_length:
                hash_index_prefix = hash_index[:prefix_length]
                if hash_index_prefix not in result:
                    result.append(hash_index_prefix)
        return result

    @staticmethod
    def str_to_substr_indexes(word: str, substr_length: int = 6) -> List[str]:
        result = []
        for i in range(len(word) - substr_length + 1):
            result.append(word[i:i+substr_length])
        return result

    def test_indexes(self, word: str) -> str:
        result = f'Index {word}\n'
        lc_word = word.lower()
        rom = self.sc_model.uroman.romanize_string(lc_word, lcode=self.sc_model.lcode)
        result += f'  Hash: {", ".join(self.str_to_hash_indexes(rom))}\n'
        result += f'  Drop: {", ".join(self.str_to_drop_indexes(lc_word))}\n'
        result += f'  Prefix: {", ".join(self.str_to_prefix_indexes(lc_word))}\n'
        result += f'  Substr: {", ".join(self.str_to_substr_indexes(lc_word))}\n'
        result += f'  Prefix-hash: {", ".join(self.str_to_prefix_hash_indexes(rom))}\n'
        result += f'  Cand: {", ".join(self.get_variation_candidates(lc_word))}\n'
        return result.rstrip()

    def get_variation_candidates(self, word: str):
        rom = self.sc_model.uroman.romanize_string(word.lower(), lcode=self.sc_model.lcode)
        result = []
        for index_list, d in [(self.str_to_hash_indexes(rom), self.hash_index),
                              (self.str_to_drop_indexes(word), self.drop_index),
                              (self.str_to_prefix_indexes(word), self.prefix_index),
                              (self.str_to_substr_indexes(word), self.substr_index),
                              (self.str_to_prefix_hash_indexes(rom), self.prefix_hash_index)]:
            for index_s in index_list:
                for cand in d[index_s]:
                    if cand not in result:
                        result.append(cand)
        return result


class OpScope:
    """Describes the scope that an operation (such as update_word) should be applied to.
    Keywords might include: user-ids; datetime-ranges; corpus-ids, book-ids, chapter-ids, snt-ids
    For example, should a spell-check/update be applied to specific books, chapters, sentences:
    OperationScope('text-ids' = ['MAT 1', 'LUK 2:1-20'])
    Or should it just be applied to text written/edited by selected users in selected time frames:
    OperationScope('user-ids' = ['user1', 'user2'], 'datetime-ranges' = [('2024-01-01', '2024-03-31')])
    Additionally, exclusions might be defined explicitly.
    """
    """Better: list of snt_id pairs"""
    def __init__(self, **s_args):
        self.s_dict = {}
        for s_key in s_args:
            self.s_dict[s_key] = s_args[s_key]


class SpellCheckMedium(Enum):
    """Output format of romanization"""
    GREEK_ROOM_SPELL_CHECKER = 'gr_sc'
    CURATED = 'curated'
    MANUAL = 'manual'
    OTHER = 'other'

    def __str__(self):
        return self.value


class Evidence:
    """Includes provenance (user)"""
    def __init__(self, user_id: str | None = None, medium: Set[SpellCheckMedium] = None):
        self.user_id = user_id
        self.medium = set() if medium is None else medium
        self.e_dict = {}

    def add_evidence(self, _evidence_policy: dict, **e_args):
        for e_key in e_args:
            arg_value = e_args[e_key]
            if e_key in self.e_dict:
                old_value = self.e_dict[e_key]
                if isinstance(old_value, float) and isinstance(arg_value, float):
                    self.e_dict[e_key] += arg_value
            else:
                self.e_dict[e_key] = e_args[e_key]


class SpellCheckAlternative:
    def __init__(self, txt: str, count: int, cost: float):
        self.txt = txt
        self.count = count
        self.cost = cost

    def __str__(self):
        return f"{self.txt} (n:{self.count} c:{round(self.cost, 2)})"


class VizClue(Enum):
    """For output style/color visualization"""
    KNOWN_DOMINANT = 'KD'  # dark green 0x007700
    KNOWN_MEDIUM = 'KM'    # medium green
    KNOWN_WEAK = 'KW'      # yellowish
    UNKNOWN_CLOSE = 'UC'   # red
    UNKNOWN_MEDIUM = 'UM'  # orange
    UNKNOWN_WEAK = 'UW'    # blue

    def __str__(self):
        return self.value


class SpellCheckSuggestion:
    """based on analysis, will offer up to multiple suggestions; later: glossing (e.g. for consultant)"""
    def __init__(self, word_edge: WordEdge, snt_id: str, lcode: str, sc_model: SpellCheckModel):
        self.lcode = lcode
        self.word_edge = word_edge
        self.word = word_edge.get_txt()
        self.anchor_count = sc_model.word_count.get((self.lcode, self.word), 0)
        self.snt_id = snt_id
        self.sc_model = sc_model
        self.alt_spellings = []  # list of SpellCheckAlternative
        for cand in sc_model.spell_index.get_variation_candidates(self.word):
            count = sc_model.word_count.get((self.lcode, cand), 0)
            cost, cost_log = sc_model.string_distance_cost(self.word, cand, max_cost=MAX_SED_COST)
            self.alt_spellings.append(SpellCheckAlternative(cand,
                                                            count=count,
                                                            cost=(99 if cost is None else round(cost, 2))))
        self.sort_sc_alternatives()
        self.prune_sc_alternatives()
        self.viz_clue = self.sc_txt_viz_clue()
        # self.support = {}  # spellings will include support

    def __str__(self):
        return f"{self.word} (n:{self.anchor_count} {self.viz_clue}): {' '.join(map(str, self.alt_spellings))}"

    def __repr__(self):
        return (f"{str(self.word_edge)} ({self.snt_id}, {self.lcode}) "
                f"spell-alts: {' '.join(map(str, self.alt_spellings))}")

    def sort_sc_alternatives(self, smooth: float = 0.01):
        self.alt_spellings = sorted(self.alt_spellings,
                                    key=lambda x: smooth / (x.cost + smooth) * math.log(x.count + 1),
                                    reverse=True)

    def sc_txt_viz_clue(self) -> VizClue:
        if self.alt_spellings:
            anchor_word = self.word
            lc_anchor_word = anchor_word.lower()
            best_lc_txt = self.alt_spellings[0].txt.lower()
            best_cost = self.alt_spellings[0].cost
            best_count = self.alt_spellings[0].count
            if lc_anchor_word == best_lc_txt and best_count >= 5:
                return VizClue.KNOWN_DOMINANT
            alt_pos = None
            for i, alt_spelling in enumerate(self.alt_spellings):
                if alt_spelling.txt.lower() == lc_anchor_word:
                    alt_pos = i
                    break
            if alt_pos is None:
                if best_cost <= 0.2 and best_count >= 5:
                    return VizClue.UNKNOWN_CLOSE
                else:
                    return VizClue.UNKNOWN_MEDIUM
            else:
                if best_cost <= 0.2 and best_count * 0.01 > self.alt_spellings[alt_pos].count:
                    return VizClue.KNOWN_WEAK
                else:
                    return VizClue.KNOWN_MEDIUM
        else:
            return VizClue.UNKNOWN_WEAK

    def prune_sc_alternatives(self, max_cost: float = 2.0):
        if self.alt_spellings:
            anchor_word = self.word
            lc_anchor_word = anchor_word.lower()
            best_count = self.alt_spellings[0].count
            best_cost = self.alt_spellings[0].cost
            best_lc_txt = self.alt_spellings[0].txt.lower()
            prev_lc_counts = defaultdict(int)
            result = []
            for alt_spelling in self.alt_spellings:
                count = alt_spelling.count
                cost = alt_spelling.cost
                txt = alt_spelling.txt
                lc_txt = txt.lower()
                if cost > max_cost:
                    continue
                elif txt == anchor_word:
                    pass
                elif (best_cost <= 0.1
                        and len(result) > 3
                        and count < best_count * 0.1
                        and cost - best_cost >= 0.4):
                    continue
                elif (best_cost <= 0.1
                        and len(result) > 5
                        and count < best_count * 0.01
                        and cost - best_cost >= 0.1):
                    continue
                elif count < prev_lc_counts[lc_txt] * 0.2 :
                    continue
                elif lc_txt in self.sc_model.exclusion_set[lc_anchor_word]:
                    continue
                elif best_lc_txt == lc_anchor_word and count < best_count * 0.02:
                    continue
                elif len(result) >= 10 and cost - best_cost >= 0.5:
                    continue
                elif len(result) >= 1 and cost - best_cost >= 0.6:
                    continue
                elif count < 0.5:
                    continue
                result.append(alt_spelling)
                prev_lc_counts[lc_txt] = max(count, prev_lc_counts[lc_txt])
            self.alt_spellings = result


class SpellCheckSuggestions:
    def __init__(self):
        self.d = {}

    def add(self, sc_suggestion: SpellCheckSuggestion):
        word_edge = sc_suggestion.word_edge
        self.d[word_edge] = sc_suggestion

    def __str__(self):
        result = 'Spell-check-suggestions:'
        for word_edge in self.d:
            result += f"\n    {self.d[word_edge]}"
        return result


class SpellCheckModel:
    """keeps stats for whole corpus"""
    # need to reliably read/write from/to file
    def __init__(self, lcode: str,
                 sed_cost_filename: str = f'{smart_edit_distance_data_dir}/string-distance-cost-rules.txt'):
        self.lcode = lcode
        self.sed = SmartEditDistance()
        self.sed.load_smart_edit_distance_data(sed_cost_filename, lcode, lcode)
        # active corpus (that might be edited)
        self.corpus = defaultdict(str)  # key: snt_id, value: snt
        self.snt_id = defaultdict(str)  # key: line_number, value: snt_id
        self.word_count = defaultdict(int)  # key: tuple(lcode, word)
        # many more stats attributes
        self.morph = {}
        self.exclusion_set = defaultdict(list)  # key: word
        self.load_spell_data_corpus(f'{spell_checker_data_dir}/spell_data.txt', lcode)
        # 2 ttable versions: static, dynamic
        # what else for suggestions
        self.ttable = {}  # key: tuple(lcode1, lcode2, s)  value: dict
        self.spell_index = SpellIndex(self)
        self.uroman = Uroman(Path(uroman_data_dir))

    def string_distance_cost(self, s1: str, s2: str, max_cost: float = None, partial: bool = False, min_len: int = 4) \
            -> Tuple[float | None, str] | Tuple[float | None, str, int | None, int | None]:
        s1 = self.uroman.romanize_string(s1.lower(), lcode=self.lcode)
        s2 = self.uroman.romanize_string(s2.lower(), lcode=self.lcode)
        return self.sed.string_distance_cost(s1, s2, max_cost=max_cost, partial=partial, min_len=min_len)

    def show_selected_word_counts(self, words: List[str]):
        result = "Word counts:"
        for word in words:
            result += f' {word} ({self.word_count[(self.lcode, word)]})'
        return result

    def load_text_corpus(self, text_filename: str,
                         _evidence: Evidence | None = None,
                         exclude: List[str] | None = None,
                         include: List[str] | None = None,
                         snt_id_data: list[str] | Path | None = None,
                         max_n_snt: int | None = None,
                         report_stats: bool = True) -> None:
        # print('INCLUDE:', include, 'EXCLUDE:', exclude)
        # snt_id_data can be a filename with snt_ids (one per line), a list of snt_ids, or None (default: L00001, ...)
        if isinstance(snt_id_data, Path) or isinstance(snt_id_data, str):
            snt_id_filename = snt_id_data
            try:
                with open(snt_id_filename) as f_snt_id:
                    for line_number, line in enumerate(f_snt_id, 1):
                        if snt_id := line.strip():
                            self.snt_id[line_number] = snt_id
            except OSError:
                sys.stderr.write(f"Cannot open snt-id file {snt_id_filename}\n")
        elif isinstance(snt_id_data, list):
            for line_number, snt_id in enumerate(snt_id_data, 1):
                if snt_id is not None:
                    self.snt_id[line_number] = snt_id
        n_non_empty_lines = 0
        n_excluded_lines = 0
        with open(text_filename) as f_text:
            for line_number, line in enumerate(f_text, 1):
                if (max_n_snt is not None) and (line_number > max_n_snt):
                    break
                if line := line.strip():
                    snt_id = self.snt_id.get(line_number, f'L{line_number:05d}')
                    exclude_line = False
                    include_line = False
                    if include:
                        for inclusion_snt_id_prefix in include:
                            if snt_id.startswith(inclusion_snt_id_prefix):
                                include_line = True
                                break
                        exclude_line = not include_line
                    if exclude:
                        for exclusion_snt_id_prefix in exclude:
                            if snt_id.startswith(exclusion_snt_id_prefix):
                                exclude_line = True
                                n_excluded_lines += 1
                                break
                    if not exclude_line:
                        n_non_empty_lines += 1
                        self.corpus[snt_id] = line
                        # Small examples for stats building (build word counts)
                        for word in words_in_snt(line):
                            self.word_count[(self.lcode, word)] += 1
        if report_stats:
            sys.stderr.write(f'Loaded {n_non_empty_lines} non-empty lines from {text_filename}\n')
            if n_non_empty_lines and include:
                sys.stderr.write(f'   Included only lines from {include}\n')
            if n_excluded_lines and exclude:
                sys.stderr.write(f'   Excluded {n_excluded_lines} lines from {exclude}\n')
        self.spell_index.index_spell_checker_corpus(self)

    def load_spell_data_corpus(self, filename: str, lcode: str, report_stats: bool = False) -> None:
        section_counts = {}
        n_non_empty_lines = 0
        spell_data_type = None
        local_lcode = None
        section_key = None
        with open(filename) as f:
            for line_number, line in enumerate(f, 1):
                if spell_data_type_cand := slot_value_in_double_colon_del_list(line, 'spell-data-type'):
                    spell_data_type = spell_data_type_cand
                    local_lcode = slot_value_in_double_colon_del_list(line, 'lcode')
                    section_key = (spell_data_type, local_lcode)
                    n_non_empty_lines += 1
                    if section_key not in section_counts:
                        section_counts[section_key] = 0
                elif line.startswith('::'):
                    spell_data_type = None
                    local_lcode = None
                    section_key = None
                    sys.stderr.write(f'Ignoring unrecognized meta line {line_number} in file {filename}:'
                                     f' {line.rstrip()}\n')
                elif line.startswith('#'):
                    pass
                elif line.isspace():
                    pass
                else:
                    if spell_data_type == 'exclusion-set' and local_lcode == lcode:
                        n_non_empty_lines += 1
                        section_counts[section_key] += 1
                        words = regex.split(r'[;,]\s*', line.strip())
                        words = [word.lower() for word in words]
                        for anchor_word in words:
                            for word in words:
                                if anchor_word != word:
                                    self.exclusion_set[anchor_word].append(word)
        if report_stats:
            sys.stderr.write(f'Loaded {n_non_empty_lines} non-empty lines from {filename}\n')
            if section_counts:
                sys.stderr.write(f'  with section counts: {section_counts}\n')

    def update_snt(self, new_snt: str, snt_id: str, _evidence: Evidence | None = None,
                   old_snt: str | None = None, _scope: OpScope | None = None, log: TextIO | None = None):
        """Update a sentence (which might have been created or edited manually).
        Providing an old_snt is only necessary if the spell_check_model does not include the (full) corpus texts."""
        lcode = self.lcode
        if (old_snt is None) and (snt_id is not None) and (snt_id in self.corpus):
            old_snt = self.corpus[snt_id]
        if old_snt:
            if old_snt == new_snt:
                return
            for word in words_in_snt(old_snt):
                self.word_count[(lcode, word)] -= 1
        for word in words_in_snt(new_snt):
            self.word_count[(lcode, word)] += 1
        self.spell_index.index_snt(new_snt)
        if snt_id is not None:
            self.corpus[snt_id] = new_snt
        if log:
            log.write(f'Updated snt from "{old_snt}" to "{new_snt}"\n')

    # evidence will include user-id, based-on-spell-checker
    def update_word(self, word_edge: WordEdge, new_word: str, snt_id: str, scope: OpScope | None = None,
                    evidence: Evidence | None = None):
        pass

    # Joel
    def update_by_user_selection(self, spell_check_analysis: SpellCheckSuggestion, selection_id: str,
                                 scope: OpScope | None = None, evidence: Evidence | None = None):
        pass

    @staticmethod
    def load_knowledge_base(filename: str) -> None:
        """KB of typically human-annotated material
        File can contain material of diverse types, e.g. morph, alignment, spell-checker exclusion lists.
            Examples for exclusion list: ['son', 'sun'], ['there', 'their', "they're"]
        Material could as simple as a word list.
        Willing annotator might offer to hand-align pairs of text.
        We expect that most KB files will include data for only one language.
        But the KB should include lcode just in case.
        Preferred format: JSONL (one json object per line)."""
        with open(filename) as f:
            for line in f:
                kb_item = json.loads(line)
                _lcode2e = kb_item.get('lcode', None)
                _info_type = kb_item.get('type', None)

    def spell_check_snt(self, snt: str, snt_id: str) -> SpellCheckSuggestions:
        """Method will generate spell-checking suggestions"""
        d = SpellCheckSuggestions()  # keys: word_edge, value: SpellCheckSuggestion
        for word_edge in words_in_snt(snt, output_word_edges=True):
            d.add(SpellCheckSuggestion(word_edge, snt_id, self.lcode, self))
        return d

    @staticmethod
    def spell_check_scope(_scope: OpScope) -> dict:
        """Method will generate spell-checking suggestions"""
        return {}

    def spell_check_word(self, word):
        result = f'  {word}:'
        for cand in self.spell_index.get_variation_candidates(word):
            count = self.word_count.get((self.lcode, cand), 0)
            cost, cost_log = self.string_distance_cost(word, cand, max_cost=MAX_SED_COST)
            result += f' {cand} (n:{count} c:{round(cost, 2)})'
        print(result)

    def test_spell_checker(self, exclude: List[str] | None, include: List[str] | None, max_n_snt: int | None = None):
        bible_version, alt_exclude = 'en-NRSV.txt', None
        # bible_version, alt_exclude = 'en-berean.txt', 'TIT, MAT'
        self.load_text_corpus(f'{spell_checker_test_dir}/{bible_version}',
                              snt_id_data=Path(f'{spell_checker_test_dir}/vref.txt'),
                              exclude=(alt_exclude if exclude is None else exclude),
                              include=include,
                              max_n_snt=max_n_snt)
        for i in (1, 2, 23214):
            if snt_id := self.snt_id[i]:
                print(snt_id, self.corpus.get(snt_id))
        for test_text, test_lcode in [('Игорь', 'rus')]:
            print(f"Test uroman ({test_lcode}): {test_text} → "
                  f"{self.uroman.romanize_string(test_text, lcode=test_lcode)}")
        for word in []:
            print(self.spell_index.test_indexes(word))
        # noinspection SpellCheckingInspection
        for word1, word2 in [('conviction', 'convikshan'), ('California', 'Kalifornien'), ('weight', 'wait')]:
            lc_word1 = word1.lower()
            lc_word2 = word2.lower()
            cost, cost_log = self.sed.string_distance_cost(lc_word1, lc_word2)
            ioc = (' ✓' if (set(self.spell_index.get_variation_candidates(lc_word1))
                            & set(self.spell_index.get_variation_candidates(lc_word2)))
                   else '')
            print(f'sed({word1}, {word2}) = {round(cost, 3)} ({cost_log}){ioc}')
        # noinspection SpellCheckingInspection
        test_snt1 = 'advisor advisors heven blesing son Beersheba'
        test_snt2 = 'adviser advisers heaven blessing son California'
        sc_suggestions = self.spell_check_snt(test_snt1, 'test')
        print(sc_suggestions)
        # noinspection SpellCheckingInspection
        wc_words = ['the', 'heven', 'advisers', 'advisors', 'California']
        print(self.show_selected_word_counts(wc_words))
        self.update_snt(test_snt1, 'test', log=sys.stdout)
        print(self.show_selected_word_counts(wc_words))
        self.update_snt(test_snt2, 'test', log=sys.stdout)  #
        print(self.show_selected_word_counts(wc_words))
        # noinspection SpellCheckingInspection
        print(self.spell_check_snt('Californie', 'test'))
        while snt := input('Another sentence? '):
            print(self.spell_check_snt(snt, 'test'))
            self.update_snt(snt, 'test', log=sys.stdout)


def main():
    start_time = datetime.datetime.now()
    sys.stderr.write(f"Start time: {start_time:%A, %B %d, %Y at %H:%M}\n")
    parser = argparse.ArgumentParser()
    parser.add_argument('direct_sentences', nargs='*', type=str)
    parser.add_argument('-l', '--lcode', type=str, help='ISO 639-3 language code, e.g. eng')
    parser.add_argument('--text_corpus_filename', type=Path)
    parser.add_argument('--kb_filename', type=Path)
    parser.add_argument('--test', action='count', default=0)
    parser.add_argument('--max_n_snt', type=int, default=None)
    parser.add_argument('--exclude', type=str, default=None,
                        help="List of books to be excluded when reading in text corpus")
    parser.add_argument('--include', type=str, default=None,
                        help="List of books to be included when reading in text corpus")
    args = parser.parse_args()

    if args.test:
        lcode = 'eng'
        exclusion_list = regex.split(r'[;,]\s*', args.exclude) if args.exclude else None
        inclusion_list = regex.split(r'[;,]\s*', args.include) if args.include else None
        spell_checker = SpellCheckModel(lcode)
        spell_checker.test_spell_checker(max_n_snt=args.max_n_snt, exclude=exclusion_list, include=inclusion_list)


if __name__ == "__main__":
    main()
