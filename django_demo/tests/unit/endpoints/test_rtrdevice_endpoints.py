import pytest
from zconnect.testutils.helpers import paginated_body, device_to_dict
from zconnect.testutils.factories import DeviceFactory
from django_demo.testutils.factories import SiteFactory


@pytest.mark.notavern
class TestIndividualDeviceSitePermissions:
    route = "/api/v3/devices/{device_id}/"

    def test_get_device_as_user_in_group(self, testclient, fakedevice, fredbloggs, fake_site):
        """Assign a device to a specific site and make sure that a user in that
        group who is not the owner of that device can access it
        """

        # Using fakedevice
        fakedevice.orgs.add(fake_site)
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

        # Add fred to this site
        # fredbloggs.orgs.add(fake_site)
        fredbloggs.add_org(fake_site)
        fredbloggs.save()
        # Object permission granted - success
        expected = {
            "status_code": 200,
            "body": {
                "sensors_current": {},
                "site": None,
                **device_to_dict(fakedevice)
            }
        }
        testclient.get_request_test_helper(expected, path_params=path_params)

    def test_get_device_as_user_in_parent_company(self, testclient, fakedevice, fredbloggs, fake_site):
        """Same, but in company
        """

        # Using fakedevice
        fakedevice.orgs.add(fake_site)
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

        # Add fred to the site's company
        fredbloggs.add_org(fake_site.company)
        fredbloggs.save()
        # Object permission granted - success
        expected = {
            "status_code": 200,
            "body": {
                "sensors_current": {},
                "site": None,
                **device_to_dict(fakedevice)
            }
        }
        testclient.get_request_test_helper(expected, path_params=path_params)

    def test_get_device_as_user_in_parent_distributor(self, testclient, fakedevice, fredbloggs, fake_site):
        """Same, but in distributor
        """

        # Using fakedevice
        fakedevice.orgs.add(fake_site)
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

        # Add fred to this distributor
        fredbloggs.add_org(fake_site.company.distributor)
        # fredbloggs.orgs.add(fake_site.company.distributor)
        fredbloggs.save()
        # Object permission granted - success
        expected = {
            "status_code": 200,
            "body": {
                "sensors_current": {},
                "site": None,
            **device_to_dict(fakedevice)
            }
        }
        testclient.get_request_test_helper(expected, path_params=path_params)

    @pytest.mark.usefixtures("fredbloggs_login")
    def test_get_device_as_user_in_random_company(self, testclient, fakedevice, fredbloggs, fake_site):
        """It should check for the correct parents, not just any company
        """

        fakedevice.orgs.add(fake_site)
        fakedevice.save()
        path_params = {
            "device_id": fakedevice.id
        }

        # Note that this needs to create a site, not just the
        # company/distributor, otherwise it will just use the same site due to
        # the way the factories work
        other_site = SiteFactory(
            name="test other site",
            company__name="Company XyZ",
            company__distributor__name="Distributor DB",
        )

        # Add fred to the another random company
        fredbloggs.add_org(other_site.company)
        fredbloggs.save()

        # In another company, so should fail
        expected = {
            "status_code": 404,
            "body": {
                "detail": "Not found."
            }
        }
        testclient.get_request_test_helper(expected, path_params=path_params)

    @pytest.mark.usefixtures("fredbloggs_login")
    def test_get_device_as_user_in_company_same_distributor(self, testclient, fakedevice, fredbloggs, fake_site):
        """Similar to above, but they both have the same distributor. This
        should fail because the user is not in the 'tree' going
        site->company->distributor.
        """

        fakedevice.orgs.add(fake_site)
        fakedevice.save()
        path_params = {
            "device_id": fakedevice.id
        }

        other_site = SiteFactory(
            name="test other site",
            company__name="Company XyZ",
            company__distributor=fake_site.company.distributor
        )

        # Add fred to the another random company
        fredbloggs.add_org(other_site.company)
        fredbloggs.save()

        # In another company, so should fail
        expected = {
            "status_code": 404,
            "body": {
                "detail": "Not found."
            }
        }
        testclient.get_request_test_helper(expected, path_params=path_params)

    @pytest.mark.usefixtures("fredbloggs_login")
    def test_get_device_as_user_in_random_distributor(self, testclient, fakedevice, fredbloggs, fake_site):
        """Same but for a distributor
        """

        fakedevice.orgs.add(fake_site)
        fakedevice.save()
        path_params = {
            "device_id": fakedevice.id
        }

        other_site = SiteFactory(
            name="test other site",
            company__name="Company XyZ",
            company__distributor__name="Distributor DB",
        )

        # Add fred to the another random distributor
        fredbloggs.add_org(other_site.company.distributor)
        fredbloggs.save()

        expected = {
            "status_code": 404,
            "body": {
                "detail": "Not found."
            }
        }
        testclient.get_request_test_helper(expected, path_params=path_params)

    def test_get_device_in_wrong_org_fails(self, testclient, fakedevice, fredbloggs, fake_site):
        """ Trying to get a device in a different org fails """
        testclient.login(fredbloggs.username)

        # Using fakedevice
        fakedevice.orgs.add(fake_site)
        fakedevice.save()
        path_params = {
            "device_id": fakedevice.id
        }

        fake_site_2 = SiteFactory(name="Another Site")

        # Add joeseed to different site
        fredbloggs.add_org(fake_site_2)
        fredbloggs.save()
        # Object permission not granted as user part of different org
        expected = {
            "status_code": 404,
            "body": {
                "detail": "Not found."
            }
        }
        testclient.get_request_test_helper(expected, path_params=path_params)

    def test_patch_device_to_change_site(self, testclient, fakedevice, admin_login, fake_site):
        """ Test that admin can update the site on a device """
        fakedevice.orgs.add(fake_site)
        fakedevice.save()
        path_params = {
            "device_id": fakedevice.id
        }

        fake_site_2 = SiteFactory(name="Another site")
        # Change the device's site
        post_body = {
            "site": {
                "id": fake_site_2.id,
                "name": fake_site_2.name,
                "r_number": fake_site_2.r_number,
            }
        }

        expected = {
            "status_code": 200,
            "body": {
                **device_to_dict(fakedevice),
                **post_body,
                "sensors_current": {},
                "updated_at": None,
                "orgs": [5, 1], # The orgs now includes new site 5
            }
        }
        testclient.patch_request_test_helper(post_body, expected, path_params=path_params)

    def test_unassign_device_site(self, testclient, fakedevice, admin_login, fake_site):
        """ Test that admin can unassign the site on a device """
        fakedevice.orgs.add(fake_site)
        fakedevice.save()
        path_params = {
            "device_id": fakedevice.id
        }

        post_body = {"site": None}

        expected = {
            "status_code": 200,
            "body": {
                **device_to_dict(fakedevice),
                **post_body,
                "sensors_current": {},
                "updated_at": None,
                "orgs": [1], # The orgs now does not include site 4
            }
        }
        testclient.patch_request_test_helper(post_body, expected, path_params=path_params)

    def test_add_site_to_device_without_one(self, testclient, fakedevice, admin_login, fake_site):
        """ Test that admin can assign a site to a device without one initially """
        path_params = {
            "device_id": fakedevice.id
        }

        post_body = {
            "site": {
                "id": fake_site.id,
                "name": fake_site.name,
                "r_number": fake_site.r_number,
            }
        }

        expected = {
            "status_code": 200,
            "body": {
                **post_body,
                **device_to_dict(fakedevice),
                "sensors_current": {},
                "updated_at": None,
                "orgs": [4, 1], # The orgs now includes site 4
            }
        }
        testclient.patch_request_test_helper(post_body, expected, path_params=path_params)

    def test_patch_no_id(self, testclient, fakedevice, admin_login, fake_site):
        """ Test that admin cannot update the site on a device without an id """
        fakedevice.orgs.add(fake_site)
        fakedevice.save()
        path_params = {
            "device_id": fakedevice.id
        }

        # Do not provide id, which will result in failed response
        post_body = {
            "site": {
                "name": "test",
                "r_number": "number",
            }
        }

        expected = {
            "status_code": 400,
            "body": {
                "code": "no_site_id",
                "detail": "When updating a site `id` must be provided"
            }
        }
        testclient.patch_request_test_helper(post_body, expected, path_params=path_params)

    def test_patch_site_does_not_exist(self, testclient, fakedevice, admin_login, fake_site):
        """ Test that admin cannot update when the site id does not exist """
        fakedevice.orgs.add(fake_site)
        fakedevice.save()
        path_params = {
            "device_id": fakedevice.id
        }

        # Provide site id that does not exist in the DB
        post_body = {
            "site": {
                "id": 999,
            }
        }

        expected = {
            "status_code": 400,
            "body": {
                "code": "site_not_found",
                "detail": "Site with id `{}` cannot be found".format(
                    post_body["site"]["id"])
            }
        }
        testclient.patch_request_test_helper(post_body, expected, path_params=path_params)


@pytest.mark.notavern
class TestDeviceSitePermissions:
    route = "/api/v3/devices/"

    def test_get_multiple_devices_as_user_in_group(self, testclient, fakedevice, fredbloggs, fake_site):
        """Same as above but for 'all' devices
        """

        # Using fakedevice
        fakedevice.orgs.add(fake_site)
        fakedevice.save()

        # No auth - failure
        expected = {
            "status_code": 401,
            "body": {
                "detail": "Authentication credentials were not provided."
            }
        }
        testclient.get_request_test_helper(expected)

        # Authenticate as this user
        testclient.login(fredbloggs.username)
        # No permissions - failure
        expected = {
            "status_code": 200,
            "body": paginated_body([])
        }
        testclient.get_request_test_helper(expected)

        # Add fred to this site
        # fredbloggs.orgs.add(fake_site)
        fredbloggs.add_org(fake_site)
        fredbloggs.save()
        # Object permission granted - success
        expected = {
            "status_code": 200,
            "body": paginated_body([
                {
                    "sensors_current": {},
                    "site": None,
                    **device_to_dict(fakedevice)
                }
            ])
        }
        testclient.get_request_test_helper(expected)


@pytest.mark.usefixtures("admin_login")
class TestDeviceEndpointLoggedInAdmin:
    route = "/api/v3/devices/"

    def test_create_device(self, testclient, fakeproduct):
        device = DeviceFactory(product=fakeproduct)

        device_as_dict = device_to_dict(device)

        unwanted = ["created_at", "updated_at", "last_seen", "id", "product", "sensors_current"]
        for key in unwanted:
            del device_as_dict[key]

        device_as_dict["product"] = fakeproduct.id

        body = device_as_dict.copy()

        device_as_dict.update({
            "id": 2,
            "created_at": None,
            "updated_at": None,
            "last_seen": None,
        })

        assert "site" in device_as_dict

        expected = {
            "status_code": 201,
            "body": device_as_dict,
        }

        testclient.post_request_test_helper(body, expected)
