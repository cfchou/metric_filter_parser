from json_filter import match
import pytest
import json


@pytest.fixture()
def json_dict():
    src = r"""
{
    "eventType": "UpdateTrail",
    "sourceIPAddress": "111.111.111.111",
    "arrayKey": [
        "value",
        "another value"
    ],
    "objectList": [
       {
         "name": "a",
         "id": 1
       },
       {
         "name": "b",
         "id": 2
       }
    ],
    "SomeObject": null,
    "someInt": 123, 
    "someFloat": 12.34, 
    "ThisFlag": true
}
    """
    return json.loads(src)


def test_int(json_dict):
    pattern = '{ $.someInt = 123 }'
    assert match(pattern, json_dict)
    pattern = '{ $.someInt != 111 }'
    assert match(pattern, json_dict)
    pattern = '{ $.someInt > 1 }'
    assert match(pattern, json_dict)
    pattern = '{ $.someInt >= 1 }'
    assert match(pattern, json_dict)
    pattern = '{ $.someInt < 1000 }'
    assert match(pattern, json_dict)
    pattern = '{ $.someInt <= 1000 }'
    assert match(pattern, json_dict)


def test_float(json_dict):
    pattern = '{ $.someFloat = 12.34 }'
    assert match(pattern, json_dict)
    pattern = '{ $.someFloat != 11.1 }'
    assert match(pattern, json_dict)
    pattern = '{ $.someFloat > 1.0 }'
    assert match(pattern, json_dict)
    pattern = '{ $.someFloat >= 1.0 }'
    assert match(pattern, json_dict)
    pattern = '{ $.someFloat < 100.0 }'
    assert match(pattern, json_dict)
    pattern = '{ $.someFloat <= 100.0 }'
    assert match(pattern, json_dict)


def test_match_pattern4(json_dict):
    pattern = '{ $.arrayKey[0] = "value" }'
    assert match(pattern, json_dict)


def test_match_pattern5(json_dict):
   # ThisFlag is not an array
   pattern = '{ $.ThisFlag[0] = "value" }'
   assert not match(pattern, json_dict)


def test_match_pattern6(json_dict):
    pattern = '{ $.objectList[1].id = 2 }'
    assert match(pattern, json_dict)


def test_match_pattern7(json_dict):
    #  If objectList is not an array this will be false. If the items in
    #  objectList are not objects or do not have an number property,
    #  this will be false
    pattern = '{ $.objectList[1].number = 2 }'
    assert not match(pattern, json_dict)


def test_match_pattern8(json_dict):
    pattern = '{ $.SomeObject IS NULL }'
    assert match(pattern, json_dict)


def test_match_pattern9(json_dict):
    pattern = '{ $.SomeOtherObject NOT EXISTS}'
    assert match(pattern, json_dict)


def test_match_pattern10(json_dict):
    pattern = '{$.ThisFlag IS TRUE}'
    assert match(pattern, json_dict)


