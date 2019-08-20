from json_filter import match
from json_filter.exception import VisitorException
import pytest
import json


@pytest.fixture()
def json_dict():
    src = r"""
{
    "eventType": "UpdateTrail",
    "sourceIPAddress": "111.111.111.111",
    "someInt": 123,
    "someFloat": 12.34,
    "someObject": {
    },
    "someEscaped": "error \\\"message\\\"",
    "someArray": []
}
    """
    return json.loads(src)


def test_quoted_escaped(json_dict):
    pattern = r'{ $.someEscaped = "error \"message\"" }'
    assert match(pattern, json_dict)


def test_quoted_eq(json_dict):
    pattern = '{ $.eventType = "UpdateTrail" }'
    assert match(pattern, json_dict)
    pattern = '{ $.eventType != "NoTrail" }'
    assert match(pattern, json_dict)


def test_quoted_not_existed(json_dict):
    pattern = '{ $.notExisted = "UpdateTrail" }'
    assert not match(pattern, json_dict)
    pattern = '{ $.notExisted != "UpdateTrail" }'
    assert not match(pattern, json_dict)


def test_quoted_not_string(json_dict):
    # for '=', type mismatch gives False
    pattern = '{ $.someInt = "123" }'
    assert not match(pattern, json_dict)
    pattern = '{ $.someFloat = "12.34" }'
    assert not match(pattern, json_dict)
    pattern = '{ $.someObject = "someString" }'
    assert not match(pattern, json_dict)
    pattern = '{ $.someArray = "someString" }'
    assert not match(pattern, json_dict)

    # for '!=', type mismatch gives True
    pattern = '{ $.someInt != "123" }'
    assert match(pattern, json_dict)
    pattern = '{ $.someFloat != "12.34" }'
    assert match(pattern, json_dict)
    pattern = '{ $.someObject != "someString" }'
    assert match(pattern, json_dict)
    pattern = '{ $.someArray != "someString" }'
    assert match(pattern, json_dict)


def test_quoted_numeric_op_raise(json_dict):
    with pytest.raises(VisitorException):
        pattern = '{ $.eventType > "UpdateTrail" }'
        match(pattern, json_dict)

    with pytest.raises(VisitorException):
        pattern = '{ $.eventType >= "UpdateTrail" }'
        match(pattern, json_dict)

    with pytest.raises(VisitorException):
        pattern = '{ $.eventType < "UpdateTrail" }'
        match(pattern, json_dict)

    with pytest.raises(VisitorException):
        pattern = '{ $.eventType <= "UpdateTrail" }'
        match(pattern, json_dict)


def test_quoted_wildcard_end(json_dict):
    pattern = '{ $.sourceIPAddress = "111.111.*" }'
    assert match(pattern, json_dict)


def test_quoted_wildcard_end_fail(json_dict):
    pattern = '{ $.sourceIPAddress != "123.123.*" }'
    assert match(pattern, json_dict)


def test_quoted_wildcard_begin(json_dict):
    pattern = '{ $.sourceIPAddress = "*111.111" }'
    assert match(pattern, json_dict)


def test_quoted_wildcard_begin_fail(json_dict):
    pattern = '{ $.sourceIPAddress != "*123.123" }'
    assert match(pattern, json_dict)


def test_quoted_wildcard(json_dict):
    pattern = '{ $.sourceIPAddress = "*111*" }'
    assert match(pattern, json_dict)


def test_quoted_wildcard_useless(json_dict):
    pattern = '{ $.sourceIPAddress = "11*1" }'
    assert not match(pattern, json_dict)


def test_simple_eq(json_dict):
    pattern = '{ $.eventType = UpdateTrail }'
    assert match(pattern, json_dict)
    pattern = '{ $.eventType != NoTrail }'
    assert match(pattern, json_dict)


def test_simple_not_existed(json_dict):
    pattern = '{ $.notExisted = UpdateTrail }'
    assert not match(pattern, json_dict)
    pattern = '{ $.notExisted != UpdateTrail }'
    assert not match(pattern, json_dict)


def test_simple_not_string(json_dict):
    # for '=', a pattern can be interpreted as a number.
    pattern = '{ $.someInt = 123 }'
    assert match(pattern, json_dict)
    pattern = '{ $.someFloat = 12.34 }'
    assert match(pattern, json_dict)
    # False for matching non-number field
    pattern = '{ $.someObject = someString }'
    assert not match(pattern, json_dict)
    pattern = '{ $.someArray = someString }'
    assert not match(pattern, json_dict)

    # for '!=', a pattern can be interpreted as a number.
    pattern = '{ $.someInt != 123 }'
    assert not match(pattern, json_dict)
    pattern = '{ $.someFloat != 12.34 }'
    assert not match(pattern, json_dict)
    # True for matching non-number field
    pattern = '{ $.someObject != someString }'
    assert match(pattern, json_dict)
    pattern = '{ $.someArray != someString }'
    assert match(pattern, json_dict)


def test_simple_numeric_op_raise(json_dict):
    with pytest.raises(VisitorException):
        pattern = '{ $.eventType > UpdateTrail }'
        match(pattern, json_dict)

    with pytest.raises(VisitorException):
        pattern = '{ $.eventType >= UpdateTrail }'
        match(pattern, json_dict)

    with pytest.raises(VisitorException):
        pattern = '{ $.eventType < UpdateTrail }'
        match(pattern, json_dict)

    with pytest.raises(VisitorException):
        pattern = '{ $.eventType <= UpdateTrail }'
        match(pattern, json_dict)


def test_simple_wildcard_end(json_dict):
    pattern = '{ $.sourceIPAddress = 111.111.* }'
    assert match(pattern, json_dict)


def test_simple_wildcard_end_fail(json_dict):
   pattern = '{ $.sourceIPAddress != 123.123.* }'
   assert match(pattern, json_dict)


def test_simple_wildcard_begin(json_dict):
    pattern = '{ $.sourceIPAddress = *111.111 }'
    assert match(pattern, json_dict)


def test_simple_wildcard_begin_fail(json_dict):
    pattern = '{ $.sourceIPAddress != *123.123 }'
    assert match(pattern, json_dict)


def test_simple_wildcard(json_dict):
    pattern = '{ $.sourceIPAddress = *111* }'
    assert match(pattern, json_dict)


def test_simple_wildcard_useless(json_dict):
    pattern = '{ $.sourceIPAddress = 11*1 }'
    assert not match(pattern, json_dict)


