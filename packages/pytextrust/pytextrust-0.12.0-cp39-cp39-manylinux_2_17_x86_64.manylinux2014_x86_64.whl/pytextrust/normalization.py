import string

from pytextrust.pytextrust import wrap_reduce_multiwhitespace
from pytextrust.replacer import replace_literal_patterns, MatchKind


AUX_REDUCTION_ACCENT_CHARS_TO_REPLACE = ['à', 'á', 'ä', 'â', 'è', 'é', 'ë', 'ê', 'ì',
                                         'í', 'ï', 'î', 'ò', 'ó', 'ö', 'ô',
                                         'ù', 'ú', 'ü', 'û', 'œ']
AUX_REDUCTION_ACCENT_CHARS_REPLACEMENT = ['a', 'a', 'a', 'a', 'e', 'e', 'e', 'e', 'i',
                                          'i', 'i', 'i', 'o', 'o', 'o',
                                          'o', 'u', 'u', 'u', 'u', 'oe']
ACCENT_REDUCTION_CHARS_TO_REPLACE = AUX_REDUCTION_ACCENT_CHARS_TO_REPLACE + \
    [val.upper() for val in AUX_REDUCTION_ACCENT_CHARS_TO_REPLACE]

ACCENT_REDUCTION_CHARS_REPLACEMENT = AUX_REDUCTION_ACCENT_CHARS_REPLACEMENT + \
    [val.upper() for val in AUX_REDUCTION_ACCENT_CHARS_REPLACEMENT]

REGEX_SYMBOLS = [".", "*", "+", "?", "|",
                 "(", ")", "[", "]", "{", "}", "\\", "^", "$"]
STANDARD_PUNCTUATION = list(string.punctuation)

INCLUDE_ACCENTS_PATTERNS = ["a", "A", "e", "E", "i", "I", "o", "O", "u", "U"]
INCLUDE_ACCENTS_SUBS = ["[aáàâä]", "[AÁÀÂÄ]", "[eéèêë]", "[EÉÈÊË]", "[iíìîï]", "[IÍÌÎÏ]",
                        "[oóòôö]", "[OÓÒÔÖ]", "[uúùûü]", "[UÚÙÛÜ]"]


def normalize_text(text_list,
                   reduce_accents=False,
                   reduce_punctuation=False,
                   reduce_multi_whitespaces=False,
                   transform_to_lower_case=False):
    """Normalize text with options:
        - reduce_accents: transforms accents into non accents
        - reduce_punctuation: transforms punctuation into whitespaces (use always 
          together with reduce_multi_whitespaces)
        - reduce_multi_whitespaces: reduces consecutive whitespaces or \n or \t into one 
          whitespace, and also strips the string
    """
    patterns_list = []
    replacement_list = []
    if reduce_accents:
        patterns_list += ACCENT_REDUCTION_CHARS_TO_REPLACE
        replacement_list += ACCENT_REDUCTION_CHARS_REPLACEMENT
    if reduce_punctuation:
        patterns_list += STANDARD_PUNCTUATION
        replacement_list += [" "] * len(STANDARD_PUNCTUATION)
        reduce_multi_whitespaces = True

    result, _ = replace_literal_patterns(
        literal_patterns=patterns_list,
        replacements=replacement_list,
        text_to_replace=text_list,
        is_bounded=False,
        case_insensitive=False,
        match_kind=MatchKind.LeftmostLongest)

    if reduce_multi_whitespaces:
        result = wrap_reduce_multiwhitespace(haystack=result, strip=True)

    if transform_to_lower_case:
        result = [val.lower() for val in result]

    return result
