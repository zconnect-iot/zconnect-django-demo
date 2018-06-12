import pytest
from zconnect.testutils.helpers import paginated_body, device_to_dict
from zconnect.testutils.factories import DeviceFactory


@pytest.mark.notavern
class TestIndividualDevicePermissions:
    route = "/api/v3/devices/{device_id}/"

    def test_get_device_as_user_in_group(self, testclient, fakedevice, fredbloggs, fake_org):
        """Assign a device to a specific org and make sure that a user in that
        group who is not the owner of that device can access it
        """

        # Using fakedevice
        fakedevice.orgs.add(fake_org)
        fakedevice.save()
        path_params = {
            "device_id": fakedevice.id
        }

        # No auth - failure
        expected = {
            "status_code": 401,
            "body": {
                "detail": "Authentication credentials were not provided."
            }
        }
        testclient.get_request_test_helper(expected, path_params=path_params)

        # Authenticate as this user
        testclient.login(fredbloggs.username)
        # No permissions - failure
        expected = {
            "status_code": 404,
            "body": {
                "detail": "Not found."
            }
        }
        testclient.get_request_test_helper(expected, path_params=path_params)

        # Add fred to this org
        fredbloggs.add_org(fake_org)
        fredbloggs.save()
        # Object permission granted - success
        expected = {
            "status_code": 200,
            "body": {
                "sensors_current": {},
                **device_to_dict(fakedevice)
            }
        }
        testclient.get_request_test_helper(expected, path_params=path_params)
