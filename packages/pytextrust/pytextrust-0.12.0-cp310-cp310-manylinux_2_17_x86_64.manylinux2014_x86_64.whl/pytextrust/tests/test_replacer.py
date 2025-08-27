from pytextrust.replacer import replace_literal_patterns, LookUpReplacer

BULK_LOOKUP_PATH = '/tmp/example_bulk_lookup.bin'
ONLINE_LOOKUP_PATH = '/tmp/example_online_lookup.bin'
PROVIDED_LOOKUP = {'mandaste': 'mandar',
                   'prestamos': 'prestamo'}


def test_basic_replacer():
    literal_patterns = ["uno", "dos"]
    replacements = ["1", "2"]
    text_to_replace = ["es el numero uno o el dos yo soy el -uno #uno puno"]
    text_list, n_reps = replace_literal_patterns(literal_patterns=literal_patterns,
                                                 replacements=replacements,
                                                 text_to_replace=text_to_replace,
                                                 is_bounded=True,
                                                 case_insensitive=True)
    assert n_reps == 4, "Number of replacements is not OK"
    assert text_list == [
        "es el numero 1 o el 2 yo soy el -1 #1 puno"], "Replaced text is not OK"


def test_lookup_replacer_online_provided():
    # TEST PROVIDED LOOKUP DICT
    lookup_replacer = LookUpReplacer(online_lookup_path=ONLINE_LOOKUP_PATH,
                                     provided_lookup_dict=PROVIDED_LOOKUP)
    assert lookup_replacer.replace_token('prestamos') == 'prestamo'
    assert lookup_replacer.replace_token('ayer') == 'ayer'


def test_lookup_replacer_online_load_pickle():
    # TEST PROVIDED LOOKUP DICT
    LookUpReplacer.write_pickle_online_map_lookup(
        lookup_dict=PROVIDED_LOOKUP, pickle_path=ONLINE_LOOKUP_PATH)
    lookup_replacer = LookUpReplacer(online_lookup_path=ONLINE_LOOKUP_PATH)
    assert lookup_replacer.replace_token('prestamos') == 'prestamo'
    assert lookup_replacer.replace_token('ayer') == 'ayer'


def test_lookup_replacer_bulk():
    # ONLY BULK
    LookUpReplacer.write_lookup(
        lookup_dict=PROVIDED_LOOKUP, lookup_path=BULK_LOOKUP_PATH)

    lookup_replacer = LookUpReplacer(
        bulk_lookup_path=BULK_LOOKUP_PATH, keep_online_ahocorasick=False)
    input_texts = ["mandasteir mandaste",
                   "$prestamos o prestamosa éprestamos Öprestamos !mandaste#"]
    replaced_texts = lookup_replacer.replace_texts(input_texts)
    assert replaced_texts == ["mandasteir mandar",
                              "$prestamo o prestamosa éprestamos Öprestamos !mandar#"]

    lookup_replacer = LookUpReplacer(
        bulk_lookup_path=BULK_LOOKUP_PATH, keep_online_ahocorasick=True)
    replaced_texts = lookup_replacer.replace_texts(input_texts)
    assert replaced_texts == ["mandasteir mandar",
                              "$prestamo o prestamosa éprestamos Öprestamos !mandar#"]
