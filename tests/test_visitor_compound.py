from json_filter import match
import pytest
import json


@pytest.fixture()
def json_dict():
    src = r"""
{
    "user": {
        "id": 1, 
        "email": "John.Stiles@example.com"
    },
    "users": [
        {
         "id": 2,
         "email": "John.Doe@example.com"
        },
        {
         "id": 3,
         "email": "Jane.Doe@example.com"
        }
    ],
    "actions": [
        "GET",
        "PUT",
        "DELETE"
    ],
    "coordinates": [
        [0, 1, 2],
        [4, 5, 6],
        [7, 8, 9]
    ]
}
    """
    return json.loads(src)


def test_match_pattern1(json_dict):
    pattern = '{ ($.user.id = 1) && ($.users[0].email = "John.Doe@example.com") }'
    assert match(pattern, json_dict)


def test_match_pattern2(json_dict):
    pattern = '{ ($.user.id = 2 && $.users[0].email = "nonmatch") || $.actions[2] = "GET" }'
    assert not match(pattern, json_dict)


def test_match_pattern3(json_dict):
    pattern = '{ $.user.email = "John.Stiles@example.com" || $.coordinates[0][1] = nonmatch && $.actions[2] = nomatch }'
    assert match(pattern, json_dict)


def test_match_pattern4(json_dict):
    pattern = '{ ($.user.email = "John.Stiles@example.com" || $.coordinates[0][1] = nonmatch) && $.actions[2] = nomatch }'
    assert not match(pattern, json_dict)



