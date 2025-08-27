from pytextrust.pytextrust import wrap_literal_replacer, wrap_literal_replacer_from_lookup, \
    wrap_lookup_write, wrap_lookup_load, wrap_map_lookup_load, FastOnlineReplacer, OnlineLiteralReplacer
from typing import List
from enum import Enum
from pytextrust.constants import get_logger
import pickle

logger = get_logger()


class MatchKind(Enum):
    LeftmostLongest = "LeftmostLongest"
    Standard = "Standard"
    LeftmostFirst = "LeftmostFirst"


class AhoCorasickKind(Enum):
    NoncontiguousNFA = "NoncontiguousNFA"
    ContiguousNFA = "ContiguousNFA"
    DFA = "DFA"
    Auto = "Auto"


def replace_literal_patterns(literal_patterns: List[str], replacements: List[str], text_to_replace: List[str],
                             is_bounded: bool = True, case_insensitive: bool = True,
                             match_kind: MatchKind = MatchKind.LeftmostLongest, n_jobs: int = 1,
                             aho_corasick_kind: AhoCorasickKind = AhoCorasickKind.Auto):
    """
    Function to replace literal patterns in texts. A literal pattern consists only in unicode characters, without
    anchors, repetitions, groups or any regex specific symbol, just literals.

    The list literal_patterns is searched and found over the provided text_to_replace list, substituting each
    literal in literal_patterns by its corresponding replacement in replacements list.

    Options:
    - is_bounded: if True, it forces the literal pattern to be bounded by non-words/numbers to be replaced
    - case_insensitive: if True, ignores case.
    - match_kind corresponds to different matching possibilities described here 
        https://docs.rs/aho-corasick/latest/aho_corasick/enum.MatchKind.html
    - n_jobs: -1 means to use all paralellization available, 1 just one thread, N to set to exactly N threads

    It returns the replaced texts and the numbers of total replacements on all texts provided.
    """
    text_list, n_reps = wrap_literal_replacer(patterns=literal_patterns,
                                              replacements=replacements,
                                              texts=text_to_replace,
                                              is_bounded=is_bounded,
                                              case_insensitive=case_insensitive,
                                              match_kind=match_kind.value,
                                              n_jobs=n_jobs,
                                              aho_corasick_kind=aho_corasick_kind.value)

    return text_list, n_reps


def replace_literal_patterns_from_lookup(lookup_path: str, text_to_replace: List[str],
                                         is_bounded: bool = True, case_insensitive: bool = True,
                                         match_kind: MatchKind = MatchKind.LeftmostLongest, n_jobs: int = 1,
                                         aho_corasick_kind: AhoCorasickKind = AhoCorasickKind.Auto):
    """
    Same than function before but uses local lookup saved data to perform substitutions
    """
    text_list, n_reps = wrap_literal_replacer_from_lookup(path=lookup_path,
                                                          texts=text_to_replace,
                                                          is_bounded=is_bounded,
                                                          case_insensitive=case_insensitive,
                                                          match_kind=match_kind.value,
                                                          n_jobs=n_jobs,
                                                          aho_corasick_kind=aho_corasick_kind.value)

    return text_list, n_reps


def load_lookup(path: str):
    src, dst = wrap_lookup_load(path)
    return src, dst


def write_lookup(src_list: List[str], dst_list: List[str], path: str):
    wrap_lookup_write(source=src_list, destination=dst_list, path=path)


def load_map_lookup(path: str):
    lookup_dict = wrap_map_lookup_load(path)
    return lookup_dict


class LookUpReplacer:
    AC_MATCH_KIND = MatchKind.LeftmostLongest
    AC_ALGORITHM = AhoCorasickKind.Auto
    AC_IS_BOUNDED = True
    AC_CASE_SENSITIVE = True

    def __init__(self,
                 online_lookup_path=None,
                 bulk_lookup_path=None,
                 online_load_pickle=True,
                 provided_lookup_dict=None,
                 bulk_n_threads=1,
                 keep_online_ahocorasick=False):
        self.online_lookup_path = online_lookup_path
        self.bulk_lookup_path = bulk_lookup_path

        self.online_load_pickle = online_load_pickle
        self.bulk_n_threads = bulk_n_threads
        self.keep_online_ahocorasick = keep_online_ahocorasick

        # LOAD ONLINE DICTIONARY TOKEN REPLACER IF REQUIRED
        if online_lookup_path is not None and provided_lookup_dict is None:
            self.load_online_map_lookup()
        elif provided_lookup_dict is not None:
            self.set_lookup_dict(provided_lookup_dict)
        else:
            self.lookup_dict = None
        # LOAD ONLINE AHO CORASICK IF REQUIRED
        if keep_online_ahocorasick and bulk_lookup_path is not None:
            self.online_ac_replacer = OnlineLiteralReplacer(
                patterns=[],
                replacements=[],
                is_bounded=self.AC_IS_BOUNDED,
                case_insensitive=self.AC_CASE_SENSITIVE,
                match_kind=self.AC_MATCH_KIND.value,
                aho_corasick_kind=self.AC_ALGORITHM.value,
                n_jobs=bulk_n_threads)
            self.online_ac_replacer.load_from_lookup_path(bulk_lookup_path)
        else:
            self.online_ac_replacer = None

    def set_lookup_dict(self, lookup_dict):
        self.lookup_dict = lookup_dict

    def load_online_map_lookup(self):
        if self.online_load_pickle:
            with open(self.online_lookup_path, mode='rb') as file:
                self.lookup_dict = pickle.load(file)
        else:
            self.lookup_dict = load_map_lookup(self.online_lookup_path)

    @classmethod
    def write_pickle_online_map_lookup(cls, lookup_dict, pickle_path):
        with open(pickle_path, mode='wb') as file:
            pickle.dump(lookup_dict, file)

    @classmethod
    def write_lookup(cls, lookup_dict, lookup_path):
        items = lookup_dict.items()
        src = [val[0] for val in items]
        dst = [val[1] for val in items]
        write_lookup(src_list=src, dst_list=dst, path=lookup_path)

    def replace_token(self, token):
        """ Online replacing one token"""
        return self.lookup_dict.get(token, token)

    def replace_texts(self, texts, case_insensitive=True):
        """ Bulk replace using disk lookup together with Aho Corasick
        all the literals in texts.

        WARNING: case_insensitive argument only is usable when not online_ac_replacer available, in this case is 
        hardcoded into case_insensitive=True"""
        if self.online_ac_replacer is not None:
            result, _ = self.online_ac_replacer.replace_all(texts=texts)
        else:
            result, _ = replace_literal_patterns_from_lookup(
                lookup_path=self.bulk_lookup_path,
                text_to_replace=texts,
                is_bounded=self.AC_IS_BOUNDED,
                case_insensitive=case_insensitive,
                match_kind=self.AC_MATCH_KIND,
                n_jobs=self.bulk_n_threads
            )
        return result
