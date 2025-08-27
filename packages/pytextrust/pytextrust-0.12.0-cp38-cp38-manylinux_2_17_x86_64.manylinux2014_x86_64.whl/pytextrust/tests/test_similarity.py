from pytextrust.similarity import parallel_calculate_similarity


def test_parallel_calculate_similarity():
    haystack = ["hola que tal", "hola buenos dias", "que tal buenos dias"]
    patterns = ["hola", "que tal", "buenos dias"]
    result = parallel_calculate_similarity(haystack=haystack,
                                           patterns=patterns,
                                           step=1,
                                           n_threads=1)
    expected_result = [[1.0, 0.9999999999999999, 0.0],
                       [1.0, 0.0, 0.9999999999999999],
                       [0.0, 0.9999999999999999, 0.9999999999999999]]
    assert expected_result == result
