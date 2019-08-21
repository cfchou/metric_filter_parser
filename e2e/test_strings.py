import pytest
import json
from json_filter import match
from json_filter.exception import VisitorException

@pytest.fixture()
def json_data():
    src = r"""
{
    "eventType": "UpdateTrail",
    "sourceIPAddress": "111.111.111.111",
    "someString": "111.111.111.111",
    "emptyString": "",
    "someInt": 123,
    "someFloat": 12.34,
    "someFloat2": 12.0,
    "someEscaped": "error \\\"message\\\"",
    "someObject": {
    },
    "someArray": [],
    "someNull": null
}
    """
    # validation
    json.loads(src)
    return src


def test_equality_quoted(json_data, client):
    ## quoted term
    patterns = [
        # string
        '{ $.someString = "111.111.111.111" }',
        '{ $.someString != 111*111 }',
        '{ $.someString = "*" }',
        '{ $.emptyString = "*" }',

        # '{ $.someString = "*111.111.111" }',     // should be True, aws bug?
        '{ $.someString = "*.111.111.111" }',  # but this passed

        '{ $.someString = "111*" }',
        '{ $.someString != "222" }',
        '{ $.someString != "222*" }',
        '{ $.someString != "*222" }',

        # int
        '{ $.someInt = "123" }',
        '{ $.someInt != "123.0" }',     # different than unquoted
        '{ $.someInt = "*" }',
        #'{ $.someInt != "1*3" }',  // # [TODO] Should be True, aws bug?

        '{ $.someInt = "1*" }',
        '{ $.someInt = "12*" }',
        '{ $.someInt = "123*" }',
        '{ $.someInt = "*123" }',
        '{ $.someInt = "*23" }',
        '{ $.someInt = "*3" }',

        '{ $.someInt != "3*" }',
        '{ $.someInt != "32*" }',
        '{ $.someInt != "321*" }',
        '{ $.someInt != "*321" }',
        '{ $.someInt != "*32" }',
        '{ $.someInt != "*1" }',

        # float
        '{ $.someFloat = "12.34" }',
        '{ $.someFloat = "*"}',
        #'{ $.someFloat != "1*4" }',   # [TODO] Should be True, aws bug?
        '{ $.someFloat2 != "12" }',     # different than unquoted

        '{ $.someFloat = "1*" }',
        '{ $.someFloat = "12*" }',
        '{ $.someFloat = "12.*" }',
        '{ $.someFloat = "12.3*" }',
        '{ $.someFloat = "12.34*"}',

        '{ $.someFloat = "*12.34"}',
        '{ $.someFloat = "*2.34"}',
        '{ $.someFloat = "*.34" }',
        '{ $.someFloat = "*34" }',
        '{ $.someFloat = "*4" }',

        '{ $.someFloat != "43.21" }',
        '{ $.someFloat != "4*1" }',

        '{ $.someFloat != "4*" }',
        '{ $.someFloat != "43*" }',
        '{ $.someFloat != "43.*" }',
        '{ $.someFloat != "43.2*" }',
        '{ $.someFloat != "43.21*"}',

        '{ $.someFloat != "*43.21"}',
        '{ $.someFloat != "*3.21" }',
        '{ $.someFloat != "*.21" }',
        '{ $.someFloat != "*21" }',
        '{ $.someFloat != "*1" }',
    ]
    for p in patterns:
        resp = client.test_metric_filter(filterPattern=p, logEventMessages=[json_data])
        matches = resp.get('matches', [])
        assert matches and len(matches) == 1
        assert matches[0]['eventMessage'] == json_data
        assert match(p, json.loads(json_data))


def test_equality_unquoted(json_data, client):
    patterns = [
        # unquoted term
        '{ $.someString = 111.111.111.111 }',
        '{ $.someString != 111*111 }',
        '{ $.someString = * }',

        #'{ $.someString = *111.111.111 }',     # [TODO] Should be True, aws bug?
        '{ $.someString = *.111.111.111 }',     # but this passed

        '{ $.someString = 111* }',
        '{ $.someString != 222 }',
        '{ $.someString != 222* }',
        '{ $.someString != *222 }',

        '{ $.someInt = 123 }',
        '{ $.someInt = 123.0 }',
        '{ $.someInt = * }',
        #'{ $.someInt != 1*3 }',   # [TODO] Should be True, aws bug?

        '{ $.someInt = 1* }',
        '{ $.someInt = 12* }',
        '{ $.someInt = 123* }',
        '{ $.someInt = *123 }',
        '{ $.someInt = *23 }',
        '{ $.someInt = *3 }',

        '{ $.someInt != 3* }',
        '{ $.someInt != 32* }',
        '{ $.someInt != 321* }',
        '{ $.someInt != *321 }',
        '{ $.someInt != *32 }',
        '{ $.someInt != *1 }',

        # float
        '{ $.someFloat = 12.34 }',
        '{ $.someFloat = *}',
        #'{ $.someFloat != 1*4 }',   # [TODO] Should be True, aws bug?
        '{ $.someFloat2 = 12 }',

        '{ $.someFloat = 1* }',
        '{ $.someFloat = 12* }',
        '{ $.someFloat = 12.* }',
        '{ $.someFloat = 12.3* }',
        '{ $.someFloat = 12.34*}',

        '{ $.someFloat = *12.34}',
        '{ $.someFloat = *2.34}',
        '{ $.someFloat = *.34 }',
        '{ $.someFloat = *34 }',
        '{ $.someFloat = *4 }',

        '{ $.someFloat != 43.21 }',

        '{ $.someFloat != 4* }',
        '{ $.someFloat != 43* }',
        '{ $.someFloat != 43.* }',
        '{ $.someFloat != 43.2* }',
        '{ $.someFloat != 43.21*}',

        '{ $.someFloat != *43.21}',
        '{ $.someFloat != *3.21 }',
        '{ $.someFloat != *.21 }',
        '{ $.someFloat != *21 }',
        '{ $.someFloat != *1 }',
    ]
    for p in patterns:
        resp = client.test_metric_filter(filterPattern=p, logEventMessages=[json_data])
        matches = resp.get('matches', [])
        assert matches and len(matches) == 1
        assert matches[0]['eventMessage'] == json_data
        assert match(p, json.loads(json_data))


def test_numeric_unquoted_unmatched(json_data, client):
    patterns = [
        '{ $.someString != 111 }',
    ]

def test_numeric_unquoted_matched(json_data, client):
    patterns = [
        '{ $.someString != 111 }',

        # '{ $.eventType >= 123 }',   # len(matches)==0

        # '{ $.someInt != 111 }',
        # '{ $.someInt != 111.0 }',
        # '{ $.someInt != "111" }',
        # '{ $.someInt != "abc" }',
        # '{ $.someInt >= 123.0 }',

        # '{ $.someInt >= someString }', # InvalidParameterException: Invalid
        # character(s) in term '"someString"'
        # '{ $.someInt >= "someString" }', # InvalidParameterException:
        # Invalid character(s) in term '"someString"'
        # '{ $.someInt >= "123" }', # InvalidParameterException: Invalid
        # character(s) in term '"someString"'
        # '{ $.someInt >= "123.0" }', # InvalidParameterException: Invalid
        # character(s) in term '"someString"'

        # len(matches) == 0
        # '{ $.someArray != "someString" }',
        # '{ $.someArray = "someString" }',
        # '{ $.someObject != "someString" }',
        # '{ $.someObject = "someString" }',

        # '{ $.someInt = "123.00" }', # len(matches) == 0
        # '{ $.someInt != 111 }',
        # '{ $.someInt != 123 }', # len(matches) == 0
        # '{ $.someInt != "123" }', # len(matches) == 0

        # r'{ $.someEscaped = "error \"message\"" }',
        # '{ $.eventType = "UpdateTrail" }',
        # '{ $.eventType != "NoTrail" }',

        # '{ $.someFloat != "12.34" }',
        # '{ $.someObject != "someString" }',
        # '{ $.someArray != "someString" }',
        # '{ $.sourceIPAddress = "111.111.*" }',
        # '{ $.sourceIPAddress != "123.123.*" }',
        # '{ $.sourceIPAddress = "*111.111" }',
        # '{ $.sourceIPAddress != "*123.123" }',
        # '{ $.sourceIPAddress = "*111*" }',
        # '{ $.eventType = UpdateTrail }',
        # '{ $.eventType != NoTrail }',
        # '{ $.someObject != someString }',
        # '{ $.someArray != someString }',
        # '{ $.sourceIPAddress = 111.111.* }',
        # '{ $.sourceIPAddress != 123.123.* }',
        # '{ $.sourceIPAddress = *111.111 }',
        # '{ $.sourceIPAddress != *123.123 }',
        # '{ $.sourceIPAddress = *111* }',
    ]
    for p in patterns:
        resp = client.test_metric_filter(filterPattern=p, logEventMessages=[json_data])
        matches = resp.get('matches', [])
        assert matches and len(matches) == 1
        assert matches[0]['eventMessage'] == json_data
        assert match(p, json.loads(json_data))


def test_unmatched(json_data, client):
    patterns = [
        # number-like unquoted strings are valid but the matching result would be unmatched whatever.
        '{ $.someString > 123 }',
        '{ $.someString >= 123 }',
        '{ $.someString < 123 }',
        '{ $.someString <= 123 }',

        # number-like strings can do equality ops
        '{ $.someString = 123 }',
        '{ $.someString = "123" }',

        # if target is not string or number return unmatched
        '{ $.someObject = 123 }',
        '{ $.someObject != 123 }',
        '{ $.someObject > 123 }',
        '{ $.someObject >= 123 }',
        '{ $.someObject < 123 }',
        '{ $.someObject <= 123 }',

        '{ $.someObject = "123" }',
        '{ $.someObject != "123" }',
        '{ $.someObject = "non-number-like" }',
        '{ $.someObject != "non-number-like" }',
    ]
    for p in patterns:
        resp = client.test_metric_filter(filterPattern=p, logEventMessages=[json_data])
        matches = resp.get('matches', [])
        assert not matches
        assert not match(p, json.loads(json_data))


def test_invalid(json_data, client):
    patterns = [
        # non number-like strings can't do numeric ops
        '{ $.someString > unquoted_string }',
        '{ $.someString >= unquoted_string }',
        '{ $.someString < unquoted_string }',
        '{ $.someString <= unquoted_string }',

        '{ $.someString > "quoted_string" }',
        '{ $.someString >= "quoted_string" }',
        '{ $.someString < "quoted_string" }',
        '{ $.someString <= "quoted_string" }',

        # number-like quoted strings can't do numeric ops either
        '{ $.someString > "123" }',
        '{ $.someString >= "123" }',
        '{ $.someString < "123" }',
        '{ $.someString <= "123" }',

        #'{ $.eventType > "UpdateTrail" }',
        #'{ $.eventType >= "UpdateTrail" }',
        #'{ $.eventType < "UpdateTrail" }',
        #'{ $.eventType <= "UpdateTrail" }',
        #'{ $.eventType > UpdateTrail }',
        #'{ $.eventType >= UpdateTrail }',
        #'{ $.eventType < UpdateTrail }',
        #'{ $.eventType <= UpdateTrail }',
    ]
    for p in patterns:
        try:
            client.test_metric_filter(filterPattern=p, logEventMessages=[json_data])
        except client.exceptions.InvalidParameterException as e:
            with pytest.raises(VisitorException):
                match(p, json.loads(json_data))
        else:
            assert False

# TODO
@pytest.mark.skip('')
def test_patterns_not_matched(json_data, client):
    patterns = [
        '{ $.notExisted = "UpdateTrail" }',
        '{ $.notExisted != "UpdateTrail" }',
        '{ $.someInt = "123" }',
        '{ $.someFloat = "12.34" }',
        '{ $.someObject = "someString" }',
        '{ $.someArray = "someString" }',
        '{ $.sourceIPAddress = "11*1" }',
        '{ $.notExisted = UpdateTrail }',
        '{ $.notExisted != UpdateTrail }',
        '{ $.someInt != 123 }',
        '{ $.someFloat != 12.34 }',
        '{ $.sourceIPAddress = 11*1 }',
    ]
    for p in patterns:
        resp = client.test_metric_filter(filterPattern=p, logEventMessages=[json_data])
        matches = resp.get('matches', [])
        assert not matches


