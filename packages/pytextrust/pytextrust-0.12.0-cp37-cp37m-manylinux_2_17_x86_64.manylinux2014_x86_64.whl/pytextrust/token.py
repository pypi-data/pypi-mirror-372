from pytextrust.constants import get_logger
from pytextrust.pytextrust import wrap_get_match_from_token_range, \
    wrap_get_token_range_from_match, wrap_map_match_by_tokens, wrap_tokenize, wrap_compute_vocabulary
from typing import List


logger = get_logger()


def tokenize(text: str):
    """ Tokenize text by ASCII whitespaces"""
    val = wrap_tokenize(text=text)

    return val


def get_match_from_token_range(text: str, token_start: int, token_end: int):
    """ Get start and end of a string from token start and end positions, 
    where tokens are separated by whitespace exclusively"""
    val = wrap_get_match_from_token_range(
        text=text, token_start=token_start, token_end=token_end)
    return val


def get_token_range_from_match(text: str, start: int, end: int):
    """ Get token start and end positions, of tokens that are intersected by string start and end, 
    where tokens are separated by whitespaces exclusively"""
    val = wrap_get_token_range_from_match(
        text=text, start=start, end=end)
    return val


def map_match_by_tokens(source: str, matched: str, match_start: int, match_end: int):
    """ Get matches on source string that relate to matched string in such a way the token positions in both strings are 
    related. NOTE: ideally the number of tokens linked to both strings and their positions must make sense as a mapping"""
    val = wrap_map_match_by_tokens(
        source=source, matched=matched, match_start=match_start, match_end=match_end)
    return val


def compute_vocabulary(text_list: List[str], n_threads: int = 1):
    """ Computes vocabulary by ascii whitespace returning a dictionary 
    of token and counts"""
    result = wrap_compute_vocabulary(haystack=text_list, n_threads=n_threads)
    return result
