import json

import pytest
import pytest_check as ptc
import requests
import synmax.hyperion as sh


@pytest.fixture()
def swagger_json():
    # load the swagger json from the web
    with requests.get("https://hyperion.api.synmax.com/apispec_1.json") as response:
        return json.loads(response.text)


@pytest.mark.xfail(reason="swagger needs to implement the necessary property.")
def test_methods_coverage(swagger_json):
    # use the swagger json to test tht the clien has all the required methods
    # get a set of methods from the HyperionApiClient class and remove the dunder methods
    method_set = {method for method in dir(sh.HyperionApiClient) if not method.startswith("__")}

    # get a set of methods from the swagger json - in the custom field x-python-client-function under each path name
    swagger_set = {path.get("x-python-client-function", None) for path in swagger_json["paths"].values()}
    swagger_set.remove(None)

    # swagger_set = {n[4:] for n in swagger_json["paths"].keys() if n.startswith("/v3/")}

    missing_methods = swagger_set - method_set
    ptc.equal(len(missing_methods), 0, "following methods are in swagger, not in HyperionApiClient: " + str(missing_methods))

    extra_methods = method_set - swagger_set
    ptc.equal(len(extra_methods), 0, "following methods are in HyperionApiClient, not in swagger: " + str(extra_methods))
