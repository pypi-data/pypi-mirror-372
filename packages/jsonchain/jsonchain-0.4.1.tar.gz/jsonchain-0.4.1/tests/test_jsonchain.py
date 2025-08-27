from jsonchain import load_json, dump_json, extract_keys
import pathlib

here = pathlib.Path.cwd()
if here.name != "tests" and here.name == "jsonchain":
    here = here / "tests"


def test_load_json():
    a_dict = load_json(here / "a.json")
    assert a_dict['aa'] == 1
    assert a_dict['ab'] == 2
    assert a_dict['bc'] == 3


def test_extract_keys():
    a_dict = load_json(here / "a.json")
    loks = extract_keys(a_dict, key_name="group")
    assert loks == [
        {"group": "aa"},
        {"group": "ab"},
        {"group": "bc"}
    ]
    loks_a = extract_keys(a_dict, key_name="group", include_startswith="a")
    assert loks_a == [
        {"group": "aa"},
        {"group": "ab"}
    ]
    loks_b = extract_keys(a_dict, key_name="group", exclude_startswith="b")
    assert loks_b == [
        {"group": "aa"},
        {"group": "ab"},
    ]
    