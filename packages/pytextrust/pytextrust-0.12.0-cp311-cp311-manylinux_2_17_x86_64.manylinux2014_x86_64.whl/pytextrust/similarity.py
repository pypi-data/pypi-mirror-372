from enum import Enum

from typing import List

from pytextrust.constants import get_logger
from pytextrust.pytextrust import wrap_single_similarity_search, wrap_parallel_calculate_similarity

logger = get_logger()


class Similarity(Enum):
    """ Kind of similarities available"""
    INTERSECTION = "intersection"
    COSINE = "cosine"
    JACCARD = "jaccard"
    COSINEJACCARDCOMBINED = "cosinejaccardcombined"
    PARTIALCOSINEJACCARDCOMBINED = "partialcosinejaccardcombined"


def single_similarity_search(haystack: str,
                             patterns: List[str],
                             step: int = 1,
                             similarity=Similarity.PARTIALCOSINEJACCARDCOMBINED.value):
    """ Search in single text"""
    val = wrap_single_similarity_search(haystack=haystack, patterns=patterns,
                                        step=step, similarity=similarity)
    return val


def parallel_calculate_similarity(haystack: List[str],
                                  patterns: List[str],
                                  step: int = 1,
                                  similarity=Similarity.PARTIALCOSINEJACCARDCOMBINED.value,
                                  par_chunk_size: int = 1000,
                                  n_threads: int = 0):
    """ Execute parallel semantic search improving greatly times"""
    val = wrap_parallel_calculate_similarity(haystack=haystack,
                                             patterns=patterns,
                                             step=step,
                                             similarity=similarity,
                                             par_chunk_size=par_chunk_size,
                                             n_threads=n_threads)
    return val
