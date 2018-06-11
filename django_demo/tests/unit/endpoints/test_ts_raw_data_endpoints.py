import pytest
from django_demo.testutils.fixtures import *
from zconnect.testutils.util import model_to_dict
from django_demo._models.ts_raw_data import TSRawData


class TestTSRawDataEndpoint:
    route = "/api/v3/devices/{device_id}/ts_raw_data/"

    def test_post_raw_data(self, testclient, fakedevice, fake_ts_raw_data, timeseries_user_login):
        raw_data = model_to_dict(fake_ts_raw_data)

        del raw_data['updated_at']
        del raw_data['created_at']
        del raw_data['id']

        post_body = raw_data

        expected = {
            "status_code": 201,
            "body": raw_data
        }

        path_params = {
            "device_id": fakedevice.id
        }

        testclient.post_request_test_helper(post_body, expected, path_params=path_params)

