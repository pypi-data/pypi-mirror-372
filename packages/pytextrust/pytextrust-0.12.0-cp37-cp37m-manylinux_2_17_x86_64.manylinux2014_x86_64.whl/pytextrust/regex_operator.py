from pydantic import BaseModel
from pytextrust import pytextrust
from typing import List, Dict, Union, Optional
import regex as re
from pytextrust.constants import get_logger
from enum import Enum

logger = get_logger()

DEFAULT_REGEX_CHUNKSIZE = 30
DEFAULT_PYTHON_REGEX_FLAG = 0x0


def check_regex_compile(pattern: str, verbose=False) -> (bool, bool, bool):
    base_nonunicode_compiles, base_compiles, fancy_compiles = pytextrust.wrap_check_regex_compile(
        pattern)
    try:
        re.compile(pattern)
        python_compiles = True
    except Exception as e:
        if verbose:
            logger.warning(
                f"Failed python compilation on {pattern} with {str(e)}")
        python_compiles = False

    return base_nonunicode_compiles, base_compiles,  fancy_compiles, python_compiles


class ParallelismConfig(Enum):
    ByPatternChunks = "ByPatternChunks"
    ByTextChunks = "ByTextChunks"


class RegexProcessDefinition(BaseModel):
    text_n_char: Optional[List[int]] = None
    text_indexes: Optional[List[str]] = None
    pattern_indexes: Optional[List[str]] = None
    substitute_bound: bool = True
    case_insensitive: bool = True
    unicode: bool = False
    substitute_latin_char: bool = False
    regexset_size_limit: int = int(3e8)
    regexset_dfa_size_limit: int = int(3e8)
    regexset_chunk_size: int = DEFAULT_REGEX_CHUNKSIZE
    n_threads: int = 0
    parallelism_config: ParallelismConfig = ParallelismConfig.ByPatternChunks
    result_grouped_by_pattern: bool = False

    def perform_rust_regex(self, patterns: List[str], texts: List[str]):
        if self.text_n_char is None:
            self.text_n_char = [len(val) for val in texts]
        match_results, invalid_pattern_indexes, n_pair_matches, n_total_matches = \
            pytextrust.wrap_regex_full_find(
                patterns=patterns,
                texts=texts,
                regex_process_definition=self.model_dump_json())
        results_dict = {'match_results': match_results,
                        'invalid_pattern_indexes': invalid_pattern_indexes,
                        'n_pair_matches': n_pair_matches,
                        'n_total_matches': n_total_matches}

        return results_dict


def apply_patterns_to_texts(patterns: List[str], texts: List[str],
                            text_indexes: Optional[List[str]] = None,
                            pattern_indexes: Optional[List[str]] = None,
                            substitute_bound: bool = True,
                            unicode: bool = False, substitute_latin_char: bool = True,
                            case_insensitive: bool = True,
                            regexset_size_mb_limit: int = int(3e2),
                            regexset_dfa_size_mb_limit: int = int(3e2),
                            regexset_chunk_size: int = DEFAULT_REGEX_CHUNKSIZE,
                            n_threads: int = 0,
                            parallelism_config: ParallelismConfig = ParallelismConfig.ByPatternChunks,
                            verbose: bool = True, skip_rust_invalid: bool = False,
                            result_grouped_by_pattern: bool = False):
    """
    This function applies regex matching giving back locations of matches between patterns and texts provided. The result
    is a dictionary where in the root level there are as keys the text indexes where matches have been found, and at the values
    of those keys there are nested dictionaries with pattern indexes as keys and values list of matches represented as tuples: (start, end).

    - Optionally, it can be set pattern_indexes or text_indexes, if not provided, default integer as strings are used as indexes.
    - Optionally, it can be set to get results grouped by patterns in root level instead of indexes by setting the bool result_grouped_by_pattern.
    - regexset_size_mb_limit, regexset_dfa_size_mb_limit are parameters about rust RegexSet build limits, they can be tweaked to allow more or less
    memory usage.
    - regexset_chunk_size can be also tweaked to group more or less patterns on grouped match phase.
    - n_threads and parallelism_config are used to specify threading behaviour. ByPatternChunks is usually more efficient than ByTextChunks.
    - case_insensitive is standard regex pattern parameter to allow case insensitive matching.

    Parameters unicode, substitute_bound and substitute_latin_char are specially designed to optimize certain cases:
    - If your patterns and text only contain [a-zA-Z0-9 ñç] plus accented vocals (any accent), but you do not care
    about accents taken into account in pattern matching, then setting unicode as False, substitute_latin_char as True 
    and substitute_bound as True, will result in a peformance improvement about x10-20.
    - In any other case proceed with more standard unicode as True, substitute_latin_char as False and substitute_bound as False.
    """
    assert (not unicode) or (unicode and (not substitute_latin_char)
                             ),    "substitute_latin_char has only sense when unicode is False"

    if text_indexes is not None:
        assert len(text_indexes) == len(
            texts), \
            f"Missmatch between lengths at provided texts list {len(texts)} and text " \
            f"indexes list {len(text_indexes)}"
    if pattern_indexes is not None:
        assert len(pattern_indexes) == len(
            patterns), f"Missmatch between lengths provided patterns list {len(patterns)} "\
            f"and patterns indexes list {len(pattern_indexes)}"

    if verbose:
        logger.info(
            f"Performing regex match and find over: \n - Patterns: {len(patterns)}\n - Texts: {len(texts)}"
            f"\n - Regex compile max size: {regexset_size_mb_limit} MBs"
            f"\n - Regex DFA max size: {regexset_dfa_size_mb_limit} MBs"
            f"\n - Number of threads: {n_threads}"
        )

    jan = RegexProcessDefinition(text_indexes=text_indexes,
                                 pattern_indexes=pattern_indexes,
                                 unicode=unicode,
                                 case_insensitive=case_insensitive,
                                 substitute_bound=substitute_bound,
                                 substitute_latin_char=substitute_latin_char,
                                 regexset_size_limit=int(
                                     regexset_size_mb_limit * 1e6),
                                 regexset_dfa_size_limit=int(
                                     regexset_dfa_size_mb_limit * 1e6),
                                 regexset_chunk_size=regexset_chunk_size,
                                 n_threads=n_threads,
                                 parallelism_config=parallelism_config,
                                 result_grouped_by_pattern=result_grouped_by_pattern)

    results_dict = jan.perform_rust_regex(patterns=patterns, texts=texts)
    n_invalid_regex = len(results_dict['invalid_pattern_indexes'])
    if n_invalid_regex > 0 and not skip_rust_invalid:
        logger.info(
            f"Applying python regex package with {n_invalid_regex} patterns")
        results_dict = apply_python_regex(patterns=results_dict['invalid_pattern_indexes'],
                                          texts=texts,
                                          pattern_indexes=pattern_indexes,
                                          text_indexes=text_indexes,
                                          prev_results=results_dict,
                                          case_insensitive=case_insensitive,
                                          result_grouped_by_pattern=result_grouped_by_pattern)

    return results_dict


def apply_python_regex(patterns: Union[List, Dict], texts: List[str], text_indexes: Optional[List[str]] = None,
                       pattern_indexes: Optional[List[str]] = None, prev_results: Optional[Dict] = None,
                       case_insensitive: bool = True, result_grouped_by_pattern: bool = False):
    """ Apply python regex over previous dictionary results with "match_results" field
    """
    if prev_results is None:
        prev_results = {'match_results': {}}
    if 'n_pair_matches' not in prev_results:
        prev_results['n_pair_matches'] = 0
    if 'n_total_matches' not in prev_results:
        prev_results['n_total_matches'] = 0

    if isinstance(patterns, list):
        if pattern_indexes is not None:
            patterns = {pattern_indexes[k]: (
                patterns[k], ) for k in range(len(patterns))}
        else:
            patterns = {str(k): (patterns[k], ) for k in range(len(patterns))}

    for pattern_index in patterns:
        pattern = patterns[pattern_index][0]
        flags_to_apply = (DEFAULT_PYTHON_REGEX_FLAG |
                          re.IGNORECASE) if case_insensitive else DEFAULT_PYTHON_REGEX_FLAG
        compiled_pattern = re.compile(pattern, flags=flags_to_apply)

        for text_pos_index, text in enumerate(texts):
            if text_indexes is not None:
                text_index = text_indexes[text_pos_index]
            else:
                text_index = str(text_pos_index)
            match_gen = compiled_pattern.finditer(text)
            matches_list = [val.span() for val in match_gen]
            if len(matches_list) > 0:
                if not result_grouped_by_pattern:
                    if text_index not in prev_results['match_results']:
                        prev_results['match_results'][text_index] = {}
                    if pattern_index not in prev_results['match_results'][text_index]:
                        prev_results['n_pair_matches'] += 1
                    prev_results['match_results'][text_index][pattern_index] = matches_list
                else:
                    if pattern_index not in prev_results['match_results']:
                        prev_results['match_results'][pattern_index] = {}
                    if text_index not in prev_results['match_results'][pattern_index]:
                        prev_results['n_pair_matches'] += 1
                    prev_results['match_results'][pattern_index][text_index] = matches_list
                prev_results['n_total_matches'] += len(matches_list)

    return prev_results


def reduce_result(match_results: Dict, result_grouped_by_pattern: bool = False):
    """ Reduce find result to a list of objects where each object is a single match
    with text_index, pattern_index, start and end
    """
    new_result = []
    for root_index in match_results:
        matches = match_results[root_index]

        for sub_index in matches:
            sub_matches = matches[sub_index]
            for match in sub_matches:
                value_dict = {'text_index': sub_index if result_grouped_by_pattern else root_index,
                              'pattern_index': root_index if result_grouped_by_pattern else sub_index,
                              'start': match[0],
                              'end': match[1]}
                new_result.append(value_dict)
    return new_result


def check_matches_eq(a_matches, b_matches, patterns_list, text_list):
    """ Checks equality between matches results"""

    text_indexes = set(a_matches['match_results'].keys()).union(
        set(b_matches['match_results'].keys()))
    for text_index in text_indexes:
        a_dict = a_matches['match_results'].get(text_index, {})
        b_dict = b_matches['match_results'].get(text_index, {})
        pattern_indexes = set(a_dict.keys()).union(set(b_dict.keys()))

        for pattern_index in pattern_indexes:

            a_pattern_matches = a_dict.get(pattern_index, [])
            b_pattern_matches = b_dict.get(pattern_index, [])
#             print(a_pattern_matches)
            if len(a_pattern_matches) != len(b_pattern_matches):
                print(
                    f"- Text: {text_list[int(text_index)]} \n- Pattern {patterns_list[int(pattern_index)]}")
                print(f"A matches: {a_pattern_matches}")
                print(f"B matches: {b_pattern_matches}")
                print("\n")


def match_patterns_to_texts(patterns: List[str], texts: List[str],
                            substitute_bound: bool = True,
                            unicode: bool = False,
                            substitute_latin_char: bool = True,
                            case_insensitive: bool = True,
                            regexset_chunk_size: int = DEFAULT_REGEX_CHUNKSIZE,
                            regexset_size_mb_limit: int = int(3e2),
                            regexset_dfa_size_mb_limit: int = int(3e2)):
    """
    Same than find but only matches.
    """
    matches, invalid_patterns = pytextrust.wrap_regex_match(patterns=patterns,
                                                            texts=texts,
                                                            unicode=unicode,
                                                            substitute_bound=substitute_bound,
                                                            substitute_latin_char=substitute_latin_char,
                                                            case_insensitive=case_insensitive,
                                                            regexset_chunk_size=regexset_chunk_size,
                                                            regexset_size_limit=int(
                                                                regexset_size_mb_limit * 1e6),
                                                            regexset_dfa_size_limit=int(
                                                                regexset_dfa_size_mb_limit * 1e6))

    if len(invalid_patterns) > 0:
        logger.info(
            f"Applying python regex package with {len(invalid_patterns)} patterns")
        more_matches = apply_python_match_regex(invalid_patterns=invalid_patterns,
                                                texts=texts,
                                                case_insensitive=case_insensitive)
        all_matches = matches + more_matches
    else:
        all_matches = matches

    return all_matches, invalid_patterns


def apply_python_match_regex(invalid_patterns, texts, case_insensitive):
    matches_list = []
    for pattern_index in invalid_patterns:
        pattern = invalid_patterns[pattern_index][0]
        pattern_index = int(pattern_index)
        flags_to_apply = (DEFAULT_PYTHON_REGEX_FLAG |
                          re.IGNORECASE) if case_insensitive else DEFAULT_PYTHON_REGEX_FLAG
        compiled_pattern = re.compile(pattern, flags=flags_to_apply)

        for text_index, text in enumerate(texts):
            matches = compiled_pattern.search(text)
            if matches is not None:
                res = (text_index, pattern_index)
                matches_list.append(res)
    return matches_list
