import json
import logging
import math
import os
import pickle
from pathlib import Path

import pandas as pd
import pytest
import pytest_check as ptc
import requests
import responses as rs
import synmax.common.api_client as ac
from requests import Response as req_Response
from responses.registries import OrderedRegistry


def test_response_return(caplog):
    test_json_dict = {"test": "test"}
    response_to_test = req_Response()
    response_to_test.status_code = 200
    response_to_test._content = json.dumps(test_json_dict).encode("utf-8")

    ptc.is_(ac.ApiClientBase._return_response(response_to_test, return_json=False), response_to_test, "failed to return response object")
    ptc.equal(ac.ApiClientBase._return_response(response_to_test, return_json=True), test_json_dict, "failed to return json object")

    response_to_test.status_code = 404
    ptc.is_none(ac.ApiClientBase._return_response(response_to_test, return_json=False), "failed to return None for non-200 status code")
    ptc.is_none(ac.ApiClientBase._return_response(response_to_test, return_json=True), "failed to return None for non-200 status code")

    response_to_test.status_code = 200
    error_json_dict = {"error": "test error_text"}
    response_to_test._content = json.dumps(error_json_dict).encode("utf-8")
    with caplog.at_level(logging.ERROR):
        ptc.is_none(ac.ApiClientBase._return_response(response_to_test, return_json=True), "failed to return None for error json")
        ptc.is_in(error_json_dict["error"], caplog.text, "failed to log error message")

    caplog.clear()
    response_to_test.status_code = 404
    with caplog.at_level(logging.ERROR):
        ptc.is_none(ac.ApiClientBase._return_response(response_to_test, return_json=True), "failed to return None for error json")
        ptc.is_not_in(error_json_dict["error"], caplog.text, "logged error message for non-200 status code")


@pytest.fixture(scope="session")
def client(scope='session'):
    return ac.ApiClient(access_token=os.getenv("access_token"))


@pytest.fixture(scope="module")
def raw_response():
    with open(Path(__file__).parent / "test_data/get_resp.pkl", "rb") as file:
        return pickle.load(file)


@pytest.fixture(scope="module")
def headers(raw_response):
    hdrs = raw_response.headers
    hdrs.pop('Content-Length')
    return hdrs

# def test_post_reply():
#     client = ac.ApiClient()


@rs.activate(registry=OrderedRegistry)
def test_get_reply_normal(client, raw_response, headers):

    rs.add(rs.Response(method="GET", url=raw_response.url, headers=headers, json=raw_response.json(), status=200))
    ret_val = client.get(raw_response.url, return_json=True)

    # should be a pandas dataframe with XXX rows and YYY columns
    ptc.is_instance(ret_val, pd.DataFrame, "failed to convert to pandas dataframe")
    ptc.equal(ret_val.shape, (2272, 4), "failed to properly convert all data")


@rs.activate(registry=OrderedRegistry)
def test_get_under_limit_429(client, raw_response, headers):

    # test retry for 429
    for _ in range(min([math.floor(ac._retry_limit/2), 2])):
        rs.add(rs.Response(method="GET", url=raw_response.url, headers=headers, json={}, status=429))

    rs.add(rs.Response(method="GET", url=raw_response.url, headers=headers, json=raw_response.json(), status=200))

    with ptc.check("Returned error for under-limit 429s"):
        ret_val = client.get(raw_response.url, return_json=True)
        assert isinstance(ret_val, pd.DataFrame), "failed to convert to pandas dataframe"
        assert ret_val.shape == (2272, 4), "failed to properly convert all data"

@rs.activate(registry=OrderedRegistry)
def test_get_limit_429s(client, raw_response, headers):

    # limit-1 429s, then a 200 should result in a proper return
    for i in range(ac._retry_limit-1):
        rs.add(rs.Response(method="GET", url=raw_response.url, headers=headers, json={}, status=429))

    rs.add(rs.Response(method="GET", url=raw_response.url, headers=headers, json=raw_response.json(), status=200))

    with ptc.check("Returned error for at-limit failed 429s"):
        ret_val = client.get(raw_response.url, return_json=True)
        assert isinstance(ret_val, pd.DataFrame), "failed to convert to pandas dataframe"
        assert ret_val.shape == (2272, 4), "failed to properly convert all data"


@rs.activate(registry=OrderedRegistry)
def test_get_over_limit_429s(client, raw_response, headers):

    # 11 429s should result in an error
    for _ in range(ac._retry_limit):
        rs.add(rs.Response(method="GET", url=raw_response.url, headers=headers, json={}, status=429))

    with pytest.raises(requests.exceptions.HTTPError):
        _ = client.get(raw_response.url, return_json=True)
