from pytextrust.regex_operator import apply_patterns_to_texts, apply_python_regex, reduce_result, match_patterns_to_texts
from pytextrust.constants import get_test_data_dir
from pytextrust.misc import load_json
import os
import pytextrust


TEST_DATA_DIR = get_test_data_dir(pytextrust)
NON_UNICODE_JSON_PATH = os.path.join(TEST_DATA_DIR, "non_unicode_test.json")


def test_base_0():
    patterns_list = [r"\bni\W{1}q\b", "\\bni\\W{1}q\\b"]
    text_list = ["ni q me parece mal"]
    results_dict = apply_patterns_to_texts(
        patterns=patterns_list, texts=text_list)
    assert (results_dict['match_results']['0']['0'] == [(0, 4)])
    assert (results_dict['match_results']['0']['1'] == [(0, 4)])

    patterns_dict = {str(k): (patterns_list[k],)
                     for k in range(len(patterns_list))}
    python_results = apply_python_regex(
        patterns=patterns_dict, texts=text_list)
    assert python_results['match_results'] == results_dict['match_results']


def test_base_match_0():
    patterns_list = [r"\bni\W{1}q\b", "\\bni\\W{1}q\\b"]
    text_list = ["ni q me parece mal"]
    matches, _ = match_patterns_to_texts(
        patterns=patterns_list, texts=text_list)
    matches.sort()
    assert (matches == [(0, 0), (0, 1)])


def test_base_1():
    patterns_list = ["\\b(?<!(no|nunca|ni|nada))(\\s|^)me parece (\\w*\\s){0,3}mal\\b",
                     r"\b(?<!(no|nunca|ni|nada))(\s|^)me parece (\w*\s){0,3}mal\b"]
    text_list = ["ni q me parece mal"]
    results_dict = apply_patterns_to_texts(
        patterns=patterns_list, texts=text_list)
    assert (results_dict['match_results']['0']['0'] == [(4, 18)])
    assert (results_dict['match_results']['0']['1'] == [(4, 18)])

    patterns_dict = {str(k): (patterns_list[k],)
                     for k in range(len(patterns_list))}
    python_results = apply_python_regex(
        patterns=patterns_dict, texts=text_list)
    assert python_results['match_results'] == results_dict['match_results']


def test_base_match_1():
    patterns_list = ["\\b(?<!(no|nunca|ni|nada))(\\s|^)me parece (\\w*\\s){0,3}mal\\b",
                     r"\b(?<!(no|nunca|ni|nada))(\s|^)me parece (\w*\s){0,3}mal\b"]
    text_list = ["ni q me parece mal"]
    matches, _ = match_patterns_to_texts(
        patterns=patterns_list, texts=text_list)
    matches.sort()
    assert (matches == [(0, 0), (0, 1)])


def test_base_match_2():
    patterns_list = [r"(\S+\s+){0,3}porciento",
                     "\\bmandato (\\S+\\s+){0,3}sepa\\b"]
    text_list = ["veintitres veinticuatro porciento",
                 "mandato veinticuatro sepa"]
    matches, _ = match_patterns_to_texts(
        patterns=patterns_list, texts=text_list)
    matches.sort()
    assert (matches == [(0, 0), (1, 1)])


def test_non_unicode():
    patterns_list = ["ña qwe ça"]
    text_list = ["ni ña qwe ça pa"]
    results_dict = apply_patterns_to_texts(
        patterns=patterns_list, texts=text_list, unicode=False, substitute_bound=True)
    assert (results_dict['match_results']['0']['0'] == [(3, 12)])

    results_dict = apply_patterns_to_texts(
        patterns=patterns_list, texts=text_list, unicode=True, substitute_bound=False, substitute_latin_char=False)
    assert (results_dict['match_results']['0']['0'] == [(3, 12)])

    patterns_dict = {str(k): (patterns_list[k],)
                     for k in range(len(patterns_list))}
    python_results = apply_python_regex(
        patterns=patterns_dict, texts=text_list)
    assert python_results['match_results'] == results_dict['match_results']


def test_non_unicode_match():
    patterns_list = ["ña qwe ça"]
    text_list = ["ni ña qwe ça pa"]
    matches, _ = match_patterns_to_texts(
        patterns=patterns_list, texts=text_list, unicode=False, substitute_bound=True, substitute_latin_char=True)
    matches.sort()
    assert (matches == [(0, 0)])

    matches, _ = match_patterns_to_texts(
        patterns=patterns_list, texts=text_list, unicode=True, substitute_bound=False, substitute_latin_char=False)
    matches.sort()
    assert (matches == [(0, 0)])


def test_unicode():
    patterns_list = ["ña qwe ça", "pr él su párü", "l su p"]
    text_list = ["ni ña qwe ça pa", "qwe pr él su párü"]
    results_dict = apply_patterns_to_texts(
        patterns=patterns_list, texts=text_list, unicode=True, substitute_bound=False, substitute_latin_char=False)
    assert (results_dict['match_results']['0']['0'] == [(3, 12)])
    assert (results_dict['match_results']['1']['1'] == [(4, 17)])
    assert (results_dict['match_results']['1']['2'] == [(8, 14)])

    patterns_dict = {str(k): (patterns_list[k],)
                     for k in range(len(patterns_list))}
    python_results = apply_python_regex(
        patterns=patterns_dict, texts=text_list)
    assert python_results['match_results'] == results_dict['match_results']


def test_n_threads():
    patterns = [
        r"ni\W{1}q",
        "ni\\W{1}q",
        "\\b(?<!(no|nunca|ni|nada))(\\s|^)me parece (\\w*\\s){0,3}mal\\b",
        r"\b(?<!(no|nunca|ni|nada))(\s|^)me parece (\w*\s){0,3}mal\b",
        r"ña"]
    text_list = ["ni q me parece mal", "hola ña"] * 20
    sing_results_dict = apply_patterns_to_texts(
        patterns=patterns, texts=text_list, n_threads=1)
    par_results_dict = apply_patterns_to_texts(
        patterns=patterns, texts=text_list, n_threads=4)

    assert (sing_results_dict == par_results_dict)

    patterns_dict = {str(k): (patterns[k],) for k in range(len(patterns))}
    python_results = apply_python_regex(
        patterns=patterns_dict, texts=text_list)
    assert python_results['match_results'] == par_results_dict['match_results']


def test_non_unicode_match_with_python():
    test_data = load_json(NON_UNICODE_JSON_PATH)
    patterns = test_data["patterns"]
    texts = test_data["texts"]
    assert len(patterns) > 0 and len(
        texts) > 0, "There are no tests for nonunicode"

    # PERFORM PYTEXTRUST MATCHING AND VERIFY THAT RESULTS ARE EQUAL TO PURE PYTHON
    results_dict = apply_patterns_to_texts(
        patterns=patterns, texts=texts, unicode=False, substitute_bound=True, substitute_latin_char=True, result_grouped_by_pattern=True)
    python_results = apply_python_regex(
        patterns=patterns, texts=texts, result_grouped_by_pattern=True)
    assert python_results['match_results'] == results_dict['match_results']

    reduced_result = reduce_result(match_results=results_dict['match_results'])
    assert len(
        reduced_result) == results_dict['n_total_matches'], "Reduced result should be ok"


def test_reduce_result():
    match_results = {'0': {'1': [(0, 1), (1, 2)], '3': [(5, 6)]},
                     '4': {'0': [(3, 7)]}}
    red_result = reduce_result(
        match_results=match_results, result_grouped_by_pattern=False)
    expected_result = [{'text_index': '0', 'pattern_index': '1', 'start': 0, 'end': 1},
                       {'text_index': '0', 'pattern_index': '1',
                           'start': 1, 'end': 2},
                       {'text_index': '0', 'pattern_index': '3',
                           'start': 5, 'end': 6},
                       {'text_index': '4', 'pattern_index': '0', 'start': 3, 'end': 7}]
    assert red_result == expected_result

    match_results = {'0': {'1': [(0, 1), (1, 2)], '3': [(5, 6)]},
                     '4': {'0': [(3, 7)]}}
    red_result = reduce_result(
        match_results=match_results, result_grouped_by_pattern=True)
    expected_result = [{'text_index': '1', 'pattern_index': '0', 'start': 0, 'end': 1},
                       {'text_index': '1', 'pattern_index': '0',
                           'start': 1, 'end': 2},
                       {'text_index': '3', 'pattern_index': '0',
                           'start': 5, 'end': 6},
                       {'text_index': '0', 'pattern_index': '4', 'start': 3, 'end': 7}]
    assert red_result == expected_result
