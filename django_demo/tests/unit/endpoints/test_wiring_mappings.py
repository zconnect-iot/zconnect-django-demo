import pytest
from django_demo.testutils.fixtures import *
from zconnect.testutils.util import model_to_dict
from django_demo._models.wiring_mapping import Mapping, WiringMapping


class TestIndividualWiringMappingEndpoint:
    route = "/api/v3/wiring_mappings/{wiringmappingid}/"

    @pytest.mark.usefixtures("admin_login")
    def test_get_wiring_mapping(self, testclient, fake_wiring_mapping):
        wiring_map = model_to_dict(fake_wiring_mapping)
        # Add latest sensor data to expected results
        maps = Mapping.objects.all()

        map_whitelist = ['sensor_key', 'input_key', 'transform_function', 'id']

        apply_whitelist = lambda inp: {x: inp[x] for x in map_whitelist}

        # Convert each of the map models to a dict and remove keys that we don't expose
        wiring_map['mappings'] = [apply_whitelist(model_to_dict(m)) for m in maps]

        wiring_map['mappings'][0]['updated_at'] = None
        wiring_map['mappings'][0]['created_at'] = None

        expected = {
            "status_code": 200,
            "body": wiring_map
        }

        path_params = {
            "wiringmappingid": fake_wiring_mapping.id
        }
        testclient.get_request_test_helper(expected, path_params=path_params)

    def test_put_wiring_mapping(self, testclient, fake_wiring_mapping, admin_login):
        full_body = model_to_dict(fake_wiring_mapping)
        full_body["mappings"] = [model_to_dict(m, exclude=["mapping"]) for m in fake_wiring_mapping.mappings.all()]

        put_body = full_body
        put_body["mappings"][0]["input_key"] = "digital_input_16"

        expected_body = put_body
        expected_body.update({"updated_at": None})
        expected_body["mappings"][0]["updated_at"] = None

        expected = {
            "status_code": 200,
            "body": expected_body,
        }

        path_params = {
            "wiringmappingid": fake_wiring_mapping.id,
        }

        testclient.put_request_test_helper(put_body, expected=expected, path_params=path_params)

    def test_patch_wiring_mapping(self, testclient, fake_wiring_mapping, admin_login):
        full_body = model_to_dict(fake_wiring_mapping)
        full_body["mappings"] = [model_to_dict(m, exclude=["mapping"]) for m in fake_wiring_mapping.mappings.all()]

        patch_body = {
            "mappings": [
                {
                    "input_key": "digital_input_19",
                    "id": 1,
                }
            ]
        }

        expected_body = full_body
        expected_body.update({"updated_at": None})
        expected_body["mappings"][0]["input_key"] = patch_body["mappings"][0]["input_key"]
        expected_body["mappings"][0]["updated_at"] = None

        expected = {
            "status_code": 200,
            "body": expected_body,
        }

        path_params = {
            "wiringmappingid": fake_wiring_mapping.id,
        }

        testclient.patch_request_test_helper(patch_body, expected=expected, path_params=path_params)
