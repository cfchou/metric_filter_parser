import pytest
import json

@pytest.fixture()
def json_data():
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
    # validation
    json.loads(src)
    return src


def test_patterns_matched(json_data, client):
    patterns = [
        '{ ($.user.id = 1) && ($.users[0].email = "John.Doe@example.com") }',
        '{ $.user.email = "John.Stiles@example.com" || $.coordinates[0][1] = nonmatch && $.actions[2] = nomatch }',
    ]
    for p in patterns:
        resp = client.test_metric_filter(filterPattern=p, logEventMessages=[json_data])
        matches = resp.get('matches', [])
        assert matches and len(matches) == 1
        assert matches[0]['eventMessage'] == json_data


def test_patterns_not_matched(json_data, client):
    patterns = [
        '{ ($.user.id = 2 && $.users[0].email = "nonmatch") || $.actions[2] = "GET" }',
        '{ ($.user.email = "John.Stiles@example.com" || $.coordinates[0][1] = nonmatch) && $.actions[2] = nomatch }',
    ]
    for p in patterns:
        resp = client.test_metric_filter(filterPattern=p, logEventMessages=[json_data])
        matches = resp.get('matches', [])
        assert not matches


