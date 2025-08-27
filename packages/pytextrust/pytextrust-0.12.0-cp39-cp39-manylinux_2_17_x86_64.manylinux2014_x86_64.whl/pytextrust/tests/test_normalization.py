from pytextrust.normalization import normalize_text


def test_normalization_base():
    text_list = [" agüa éééé. j, w: !?    SdWWW 123"]
    result = normalize_text(text_list=text_list,
                            reduce_accents=True,
                            reduce_multi_whitespaces=True,
                            reduce_punctuation=True,
                            transform_to_lower_case=True)
    expected_result = ['agua eeee j w sdwww 123']
    assert result == expected_result
