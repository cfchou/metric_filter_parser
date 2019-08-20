import pytest
import json


@pytest.fixture()
def json_data():
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
    # validation
    json.loads(src)
    return src


def test_patterns_matched(json_data, client):
    patterns = [
        '{ $.someInt = 123 }',
        '{ $.someInt != 111 }',
        '{ $.someInt > 1 }',
        '{ $.someInt >= 1 }',
        '{ $.someInt < 1000 }',
        '{ $.someInt <= 1000 }',
        '{ $.someFloat = 12.34 }',
        '{ $.someFloat != 11.1 }',
        '{ $.someFloat > 1.0 }',
        '{ $.someFloat   >= 1.0 }',
        '{ $.someFloat <       100.0 }',
        '{ $.someFloat      <=     100.0 }',
        '{ $.arrayKey[0] = "value" }',
        '{ $.objectList[1].id    = 2 }',
        '{ $.SomeObject IS NULL }',
        '{ $.SomeOtherObject NOT EXISTS         }',
    ]
    for p in patterns:
        resp = client.test_metric_filter(filterPattern=p, logEventMessages=[json_data])
        matches = resp.get('matches', [])
        assert matches and len(matches) == 1
        assert matches[0]['eventMessage'] == json_data


def test_patterns_not_matched(json_data, client):
    patterns = [
        '{ $.ThisFlag[0] = "value" }',
        '{ $.objectList[1].number = 2 }',
    ]
    for p in patterns:
        resp = client.test_metric_filter(filterPattern=p, logEventMessages=[json_data])
        matches = resp.get('matches', [])
        assert not matches


def test_patterns_invalid(json_data, client):
    patterns = [
        ' {$.ThisFlag IS TRUE} ',
    ]
    for p in patterns:
        try:
            client.test_metric_filter(filterPattern=p, logEventMessages=[json_data])
        except client.exceptions.InvalidParameterException as e:
            assert e.args[0].find('Invalid metric filter pattern') != -1
        else:
            assert False
