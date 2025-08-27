from pytextrust.token import get_match_from_token_range, get_token_range_from_match, \
    map_match_by_tokens, tokenize


def test_tokenize():
    text = "  a\nb   c\rd \te  "
    assert ["a", "b", "c", "d", "e"] == tokenize(text)


def test_get_token_range_from_match():

    text = "hacer haber evento múltiple"

    assert (0, 2) == get_token_range_from_match(text, 0, 11)


def test_get_match_from_token_range():

    text = "  Ñ  ha habido eventos multiples  "

    assert (2, 3) == get_match_from_token_range(text, 0, 1)


def test_map_match_by_tokens():
    source = "  Ñ  ha habido eventos multiples  "
    matched = " Ç  hacer haber evento multiple "

    assert (5, 7) == map_match_by_tokens(source=source,
                                         matched=matched, match_start=2, match_end=7)
