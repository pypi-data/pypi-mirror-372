#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2024

import json

import pytest
from requests import Response

from streamsets.sdk import sdc_api, st_api

INSTANCE_ID = 'x'


class MockSdcApiTunneling(sdc_api.ApiClient):
    # behaves as sdc_api.APIClient, except does _register_with_aster_and_login
    # also mocks calls via _get

    def _register_with_aster_and_login(self):
        # doing nothing is treated as valid login
        pass

    def get_sdc_info(self):
        return {'version': 1}

    def _get(self, endpoint, params={}, absolute_endpoint=False):
        r = Response()
        r.status_code = 200
        r._content = bytes(json.dumps({'instanceId': INSTANCE_ID}), encoding='utf-8')
        return r


class MockStApiTunneling(st_api.ApiClient):
    # behaves as st_api.APIClient, except does _register_with_aster_and_login
    # also mocks calls via _get

    def _register_with_aster_and_login(self):
        # doing nothing is treated as valid login
        pass

    def get_st_info(self):
        return {'version': 1}

    def _get(self, endpoint, params={}, absolute_endpoint=False):
        r = Response()
        r.status_code = 200
        r._content = bytes(json.dumps({'instanceId': INSTANCE_ID}), encoding='utf-8')
        return r


@pytest.mark.parametrize("api_class", [MockSdcApiTunneling, MockStApiTunneling])
@pytest.mark.parametrize(
    "server_url",
    [
        "https://dev.hub.streamsets.com/tunneling/rest/engine1",
        "https://something.random.com/streamsets/main/tunneling/rest/engine1",
    ],
)
def test_tunneling_uses_correct_sch_url(api_class, server_url):
    client = api_class(server_url=server_url)

    assert client._tunneling_instance_id == INSTANCE_ID
