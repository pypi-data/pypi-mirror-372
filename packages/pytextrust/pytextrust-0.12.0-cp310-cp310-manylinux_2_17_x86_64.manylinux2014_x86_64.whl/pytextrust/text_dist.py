from pytextrust.pytextrust import wrap_dist_needleman_wunsch, wrap_compute_overlaping_zone
from typing import List


def dist_needleman_wunsch(seq_a: List[str], seq_b: List[str],
                          mismatch_penalty: float = None, gap_penalty: float = 1.0):
    """
    Computes Needleman-Wunsch distance between two sequences of tokens.
    If missmatch_penalty is None, then levenshtein distancebetween substitution tokens is computed on mismatch,
    if it is not None it can be a non negative f64 indicating missmatch penalty"""
    val = wrap_dist_needleman_wunsch(seq_a=seq_a, seq_b=seq_b,
                                     mismatch_penalty=mismatch_penalty, gap_penalty=gap_penalty)
    return val


def compute_overlaping_zone(seq_a: List[str], seq_b: List[str],
                            min_overlap: int,
                            max_length_diff: int,
                            mismatch_penalty: float = 1.0, gap_penalty: float = 1.0):
    """
    Computes overlaping zone between two sequences, based on the minimization of the distances pair Needleman-Wunsch distance 
    and Tversky.
    If missmatch_penalty is None, then levenshtein distancebetween substitution tokens is computed on mismatch,
    if it is not None it can be a non negative f64 indicating missmatch penalty"""
    best_seq_a_len, best_seq_b_len, best_needleman_wunsch_dist, best_tversky_dist = \
        wrap_compute_overlaping_zone(seq_a=seq_a, seq_b=seq_b,
                                     min_overlap=min_overlap, max_length_diff=max_length_diff,
                                     mismatch_penalty=mismatch_penalty, gap_penalty=gap_penalty)

    return best_seq_a_len, best_seq_b_len, best_needleman_wunsch_dist, best_tversky_dist
