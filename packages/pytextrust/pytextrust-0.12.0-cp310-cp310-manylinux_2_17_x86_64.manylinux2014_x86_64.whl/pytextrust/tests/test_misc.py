from pytextrust.constants import get_test_data_dir
import os
import pytextrust


def test_test_data_dir():
    test_data_dir = get_test_data_dir(pytextrust)
    assert "pytextrust" in test_data_dir, "Module dir does not contain module name"
    assert len(test_data_dir) > 0, "Test data dir empty"
    assert "non_unicode_test.json" in os.listdir(test_data_dir), "non_unicode_test.csv not in test data dir"