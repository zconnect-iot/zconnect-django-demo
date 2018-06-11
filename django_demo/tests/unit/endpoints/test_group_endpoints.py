import pytest
import os

from zconnect.testutils.fixtures import *
from zconnect.testutils.helpers import paginated_body
from zconnect.testutils.util import model_to_dict
from zconnect.testutils.factories import OrganizationLogoFactory
from zconnect.serializers import LocationSerializer
from zconnect.models import Location

from django_demo.serializers import SiteSerializer, CompanySerializer, DistributorSerializer
from django_demo.models import CompanyGroup
from django_demo.testutils.factories import CompanyFactory, DistributorFactory, SiteFactory


AUTH_ERROR_RESP = {
    "status_code": 401,
    "body": {
        "detail": "Authentication credentials were not provided."
    }
}

RED_LOGO = "/files/download/?name=zconnect.LogoImage%2Fbytes%2Ffilename%2Fmimetype%2Fred_logo.png"

class TestSiteEndpoint:
    route = "/api/v3/sites/"

    def test_get_site(self, testclient, fake_site, fakedevice, joeseed_login):
        """Get site as expected"""

        fakedevice.orgs.add(fake_site)
        joeseed_login.add_org(fake_site)

        # model_to_dict will return a lot of fields we don't care or want in the
        # response - get the response the same way that
        returned = SiteSerializer(fake_site).data
        returned['dashboards'] = ["loneworker_site_dashboard"]

        expected = {
            "status_code": 200,
            "body": paginated_body([
                returned
            ]),
        }

        assert returned["devices"][0] == {
            "name": fakedevice.name,
            "id": fakedevice.id
        }

        testclient.get_request_test_helper(expected)

    @pytest.mark.usefixtures("admin_login")
    def test_admin_gets_all_dashboards(self, testclient, fake_site):
        """Test an admin user sees all dashboards on a site"""

        returned = SiteSerializer(fake_site).data
        returned['dashboards'] = ["loneworker_site_dashboard", "default"]

        expected = {
            "status_code": 200,
            "body": paginated_body([
                returned
            ]),
        }

        testclient.get_request_test_helper(expected)

    def test_multiple_site(self, testclient, fake_site, fake_company, joeseed_login):
        """Get multiple sites"""
        joeseed_login.add_org(fake_company)

        fake_site_2 = SiteFactory(name="Another site", company=fake_company)
        returned = SiteSerializer(fake_site).data
        returned['dashboards'] = ["loneworker_site_dashboard"]
        returned_2 = SiteSerializer(fake_site_2).data
        returned_2['dashboards'] = ["loneworker_site_dashboard"]

        expected = {
            "status_code": 200,
            "body": paginated_body([
                returned,
                returned_2
            ]),
        }
        testclient.get_request_test_helper(expected)

    @pytest.mark.usefixtures("admin_login")
    def test_site_logo(self, testclient, fake_site, fakedevice, red_logo):
        """Test that a site with a logo includes said logo"""

        fakedevice.orgs.add(fake_site)

        OrganizationLogoFactory(organization=fake_site)

        returned = SiteSerializer(fake_site).data
        # Default dashboard added because we're logged in as admin
        returned['dashboards'] = ["loneworker_site_dashboard", "default"]
        returned['logo'] = RED_LOGO

        expected = {
            "status_code": 200,
            "body": paginated_body([
                returned
            ]),
        }

        assert returned["devices"][0] == {
            "name": fakedevice.name,
            "id": fakedevice.id
        }

        testclient.get_request_test_helper(expected)


class TestSiteAncestors:
    route = "/api/v3/sites/{site_id}/"

    def test_get_specific_site(self, testclient, fake_site, joeseed_login):
        """Make sure company is as expected

        This just tests the seed data so is a bit pointless
        """
        joeseed_login.add_org(fake_site)

        path_parameters = {
            "site_id": fake_site.id
        }

        returned = SiteSerializer(fake_site).data
        returned['dashboards'] = ["loneworker_site_dashboard"]

        expected = {
            "status_code": 200,
            "body": returned,
        }
        result = testclient.get_request_test_helper(expected, path_params=path_parameters)
        assert CompanyGroup.objects.get(id=result.json()["company"]["id"]) == fake_site.company


def _get_site_response(fake_site):
    """This is what should be returned from the FULL serializer
    """
    return {
        "location": model_to_dict(fake_site.location),
        "name": fake_site.name,
        "company": {
            "name": fake_site.company.name,
            "id": fake_site.company.id,
        },
        "id": fake_site.id,
        "r_number": fake_site.r_number,
        "dashboards": ["loneworker_site_dashboard"],
        "devices": [],
        "logo": None
    }


def _get_stubbed_site_response(fake_site):
    """This is what should be returned from the STUB serializer
    """
    return {
        "name": fake_site.name,
        "id": fake_site.id,
        "r_number": fake_site.r_number,
    }


class TestSitesEndpoint:
    route = "/api/v3/sites/"

    def test_sites_denied(self, testclient):
        """Check non-logged in users can't see sites"""
        expected = AUTH_ERROR_RESP.copy()
        testclient.get_request_test_helper(expected)

    def test_get_multiple_sites_stubbed_company(self, testclient, joeseed_login, fake_site):
        """It won't return the stuff from model_to_dict - only a subset of the
        site fields are returned, and the company reference should be stubbed
        """
        joeseed_login.add_org(fake_site)

        returned = _get_site_response(fake_site)

        expected = {
            "status_code": 200,
            "body": paginated_body([returned])
        }
        testclient.get_request_test_helper(expected)

    def test_query_param_not_stubbed(self, testclient, joeseed_login, fake_site):
        """passing stub as 'false' should not return a stubbed response
        """
        joeseed_login.add_org(fake_site)

        returned = _get_site_response(fake_site)

        query_params = {
            "stub": False,
        }
        expected = {
            "status_code": 200,
            "body": paginated_body([returned])
        }
        testclient.get_request_test_helper(expected, query_params=query_params)

    def test_get_stubbed_sites(self, testclient, joeseed_login, fake_site):
        """when passing stub=true, only returns id/name"""
        joeseed_login.add_org(fake_site)

        returned = _get_stubbed_site_response(fake_site)

        query_params = {
            "stub": True,
        }
        expected = {
            "status_code": 200,
            "body": paginated_body([returned])
        }
        testclient.get_request_test_helper(expected, query_params=query_params)

    @pytest.mark.usefixtures("admin_login")
    def test_post_creates_site_location(self, testclient, fake_site):
        """ Test that a post created a new location object in DB """
        location_count = Location.objects.count()

        post_body = SiteSerializer(fake_site).data
        post_body["id"] = None
        post_body["location"] = LocationSerializer(fake_site.location).data
        post_body["location"]["id"] = None
        post_body["location"]["updated_at"] = None
        post_body["location"]["created_at"] = None

        expected_body = post_body
        expected_body['dashboards'] = ['loneworker_site_dashboard', 'default']

        # This also tests that Company is set on the new Site as well
        expected = {
            "status_code": 201,
            "body": expected_body
        }

        testclient.post_request_test_helper(post_body, expected)

        assert Location.objects.count() == location_count + 1


class TestSpecificSiteEndpoint:
    route = "/api/v3/sites/{site_id}/"

    def test_sites_denied(self, testclient, fake_site):
        """ Check non-logged in users can't see a single site """
        path_params = {
            "site_id": fake_site.id,
        }
        expected = AUTH_ERROR_RESP.copy()
        testclient.get_request_test_helper(expected, path_params=path_params)

    def test_get_site_stubbed_company(self, testclient, joeseed_login, fake_site):
        """ Check a site includes a company stub """
        joeseed_login.add_org(fake_site)

        returned = _get_site_response(fake_site)

        path_params = {
            "site_id": fake_site.id,
        }
        expected = {
            "status_code": 200,
            "body": returned,
        }
        testclient.get_request_test_helper(expected, path_params=path_params)

    def test_query_param_not_stubbed(self, testclient, joeseed_login, fake_site):
        """ Check that explicitly passing stub=False returns the full object """
        joeseed_login.add_org(fake_site)

        returned = _get_site_response(fake_site)

        path_params = {
            "site_id": fake_site.id,
        }
        query_params = {
            "stub": False,
        }
        expected = {
            "status_code": 200,
            "body": returned,
        }
        testclient.get_request_test_helper(expected, query_params=query_params, path_params=path_params)

    def test_get_stubbed_sites(self, testclient, joeseed_login, fake_site):
        """ Test passing stub=True returns a stub """
        joeseed_login.add_org(fake_site)

        returned = _get_stubbed_site_response(fake_site)

        path_params = {
            "site_id": fake_site.id,
        }
        query_params = {
            "stub": True,
        }
        expected = {
            "status_code": 200,
            "body": returned,
        }
        testclient.get_request_test_helper(expected, query_params=query_params, path_params=path_params)

    def test_user_in_wrong_org_fails(self, testclient, joeseed_login, fake_site):
        """ Check user who is not in the org parental chain cannot access site """
        fake_site_2 = SiteFactory(name="Another site")
        joeseed_login.add_org(fake_site_2)

        path_params = {
            "site_id": fake_site.id,
        }
        expected = {
            "status_code": 404,
            "body":   {
                "detail": "Not found."
              }
        }
        testclient.get_request_test_helper(expected, path_params=path_params)

    @pytest.mark.usefixtures("admin_login")
    def test_patch_updates_site_location(self, testclient, fake_site):
        """ Test that a patch updates the nested location field """
        pp = {
            "site_id": fake_site.id
        }

        # Change country
        post_body = SiteSerializer(fake_site).data
        post_body["location"] = LocationSerializer(fake_site.location).data
        post_body["location"]["country"] = "Bolivia"
        post_body["location"]["updated_at"] = None
        expected_body = post_body
        expected_body['dashboards'] = ['loneworker_site_dashboard', 'default']

        expected = {
            "status_code": 200,
            "body": expected_body,
        }
        testclient.patch_request_test_helper(post_body, expected, path_params=pp)

    @pytest.mark.usefixtures("admin_login")
    def test_patch_updates_site_company(self, testclient, fake_site, fake_distributor):
        """ Test that a patch updates parent company """
        pp = {
            "site_id": fake_site.id
        }
        new_company = CompanyFactory(
            name="New Company",
            distributor=fake_distributor,
        )

        post_body = {"company": {"id": new_company.id, "name": new_company.name}}

        expected = SiteSerializer(fake_site).data
        expected['dashboards'] = ['loneworker_site_dashboard', 'default']
        expected.update(post_body)

        expected = {
            "status_code": 200,
            "body": expected
        }

        testclient.patch_request_test_helper(post_body, expected, path_params=pp)

    @pytest.mark.usefixtures("admin_login")
    def test_patch_fails_without_location_id(self, testclient, fake_site):
        """ Test that a patch fails to update location without id field """
        pp = {
            "site_id": fake_site.id
        }

        payload = {"location": {"locality": "test"}}

        expected = {
            "status_code": 400,
            "body": {
                "code": "stub_viewset",
                "detail": "You need to provide an id to update a nested field"
            }
        }
        testclient.patch_request_test_helper(payload, expected, path_params=pp)

    @pytest.mark.usefixtures("admin_login")
    def test_patch_site_company_failure(self, testclient, fake_site):
        """ Test that a patch to sites company that does not exist fails"""
        pp = {
            "site_id": fake_site.id
        }

        # company with id 100 does not exist
        post_body = {"company": {"id": 100}}

        expected = SiteSerializer(fake_site).data
        expected.update(post_body)

        expected = {
            "status_code": 400,
            "body": {
                "code": "stub_serializer",
                "detail": "There is no CompanyGroup with id 100"
            }
        }

        testclient.patch_request_test_helper(post_body, expected, path_params=pp)


def _get_company_response(fake_company):
    """This is what should be returned from the FULL serializer
    """
    return {
        "location": model_to_dict(fake_company.location),
        "name": fake_company.name,
        "distributor": {
            "name": fake_company.distributor.name,
            "id": fake_company.distributor.id,
        },
        "sites": [
            _get_stubbed_site_response(site) for site in fake_company.sites.all()
        ],
        "id": fake_company.id,
        "dashboards": ["loneworker_company_dashboard"],
        "logo": None,
    }


def _get_stubbed_company_response(fake_company):
    """This is what should be returned from the STUB serializer
    """
    return {
        "name": fake_company.name,
        "id": fake_company.id,
    }


class TestCompaniesEndpoint:
    route = "/api/v3/companies/"

    def test_companies_denied(self, testclient):
        """ Check non-logged in users can't see companies """
        expected = AUTH_ERROR_RESP.copy()
        testclient.get_request_test_helper(expected)

    def test_get_multiple_companies_stubbed_company(self, testclient, joeseed_login, fake_company):
        """It won't return the stuff from model_to_dict - only a subset of the
        company fields are returned, and the company reference should be stubbed
        """
        joeseed_login.add_org(fake_company)

        returned = _get_company_response(fake_company)

        expected = {
            "status_code": 200,
            "body": paginated_body([returned])
        }
        testclient.get_request_test_helper(expected)

    def test_query_param_not_stubbed(self, testclient, joeseed_login, fake_company):
        """passing stub as 'false' should not return a stubbed response
        """
        joeseed_login.add_org(fake_company)

        returned = _get_company_response(fake_company)

        query_params = {
            "stub": False,
        }
        expected = {
            "status_code": 200,
            "body": paginated_body([returned])
        }
        testclient.get_request_test_helper(expected, query_params=query_params)

    def test_get_stubbed_companies(self, testclient, joeseed_login, fake_company):
        """when passing stub=true, only returns id/name"""
        joeseed_login.add_org(fake_company)

        returned = _get_stubbed_company_response(fake_company)

        query_params = {
            "stub": True,
        }
        expected = {
            "status_code": 200,
            "body": paginated_body([returned])
        }
        testclient.get_request_test_helper(expected, query_params=query_params)

    @pytest.mark.usefixtures("admin_login")
    def test_post_creates_company_location(self, testclient, fake_company):
        """ Test that a post created a new location object in DB """
        location_count = Location.objects.count()

        post_body = CompanySerializer(fake_company).data
        post_body["id"] = None
        post_body["location"] = LocationSerializer(fake_company.location).data
        post_body["location"]["id"] = None
        post_body["location"]["updated_at"] = None
        post_body["location"]["created_at"] = None
        post_body["sites"] = []

        expected_body = post_body
        expected_body['dashboards'] = ['loneworker_company_dashboard', 'default']

        # This also tests that Distributor is set on the new Company as well
        expected = {
            "status_code": 201,
            "body": expected_body
        }

        testclient.post_request_test_helper(post_body, expected)

        assert Location.objects.count() == location_count + 1


class TestSpecificCompanyEndpoint:
    route = "/api/v3/companies/{company_id}/"

    def test_companies_denied(self, testclient, fake_company):
        """ Check non-logged in users can't see a single company """
        path_params = {
            "company_id": fake_company.id,
        }
        expected = AUTH_ERROR_RESP.copy()
        testclient.get_request_test_helper(expected, path_params=path_params)

    def test_get_company_stubbed_company(self, testclient, joeseed_login, fake_company):
        """ Check that getting a company returns the full object """
        joeseed_login.add_org(fake_company)

        returned = _get_company_response(fake_company)

        path_params = {
            "company_id": fake_company.id,
        }
        expected = {
            "status_code": 200,
            "body": returned,
        }
        testclient.get_request_test_helper(expected, path_params=path_params)

    def test_query_param_not_stubbed(self, testclient, joeseed_login, fake_company):
        """ Check that passing stub=False is the same as not passing it """
        joeseed_login.add_org(fake_company)

        returned = _get_company_response(fake_company)

        path_params = {
            "company_id": fake_company.id,
        }
        query_params = {
            "stub": False,
        }
        expected = {
            "status_code": 200,
            "body": returned,
        }
        testclient.get_request_test_helper(expected, query_params=query_params, path_params=path_params)

    def test_get_stubbed_companies(self, testclient, joeseed_login, fake_company):
        """ Check that passing stub=True gives a stub """
        joeseed_login.add_org(fake_company)

        returned = _get_stubbed_company_response(fake_company)

        path_params = {
            "company_id": fake_company.id,
        }
        query_params = {
            "stub": True,
        }
        expected = {
            "status_code": 200,
            "body": returned,
        }
        testclient.get_request_test_helper(expected, query_params=query_params, path_params=path_params)

    def test_user_in_wrong_org_fails(self, testclient, joeseed_login, fake_company):
        """ Check user who is not in the org parental chain cannot access company """
        fake_company_2 = CompanyFactory(name="Another company")
        joeseed_login.add_org(fake_company_2)

        path_params = {
            "company_id": fake_company.id,
        }
        expected = {
            "status_code": 404,
            "body":   {
                "detail": "Not found."
              }
        }
        testclient.get_request_test_helper(expected, path_params=path_params)

    @pytest.mark.usefixtures("admin_login")
    def test_patch_updates_company_location(self, testclient, fake_company):
        """ Test that a patch updates the nested location field """
        pp = {
            "company_id": fake_company.id
        }

        # Change country
        post_body = CompanySerializer(fake_company).data
        post_body["location"] = LocationSerializer(fake_company.location).data
        post_body["location"]["country"] = "Bolivia"
        post_body["location"]["updated_at"] = None

        expected_body = post_body
        expected_body['dashboards'] = ['loneworker_company_dashboard', 'default']

        expected = {
            "status_code": 200,
            "body": expected_body
        }
        testclient.patch_request_test_helper(post_body, expected, path_params=pp)

    @pytest.mark.usefixtures("admin_login")
    def test_patch_fails_without_location_id(self, testclient, fake_company):
        """ Test that a patch fails to update location without id field """
        pp = {
            "company_id": fake_company.id
        }

        payload = {"location": {"locality": "test"}}

        expected = {
            "status_code": 400,
            "body": {
                "code": "stub_viewset",
                "detail": "You need to provide an id to update a nested field"
            }
        }
        testclient.patch_request_test_helper(payload, expected, path_params=pp)

    @pytest.mark.usefixtures("admin_login")
    def test_patch_updates_company_distributor(self, testclient, fake_company):
        """ Test that a patch updates parent distributor """
        pp = {
            "company_id": fake_company.id
        }
        new_distributor = DistributorFactory(
            name="New Distributor",
        )

        post_body = {"distributor": {"id": new_distributor.id, "name": new_distributor.name}}

        expected = CompanySerializer(fake_company).data
        expected['dashboards'] = ['loneworker_company_dashboard', 'default']
        expected.update(post_body)

        expected = {
            "status_code": 200,
            "body": expected
        }

        testclient.patch_request_test_helper(post_body, expected, path_params=pp)

    @pytest.mark.usefixtures("admin_login")
    def test_patch_does_not_update_company_sites(self, testclient, fake_company):
        """ Test that a patch does not update child sites """
        pp = {
            "company_id": fake_company.id
        }
        new_company = CompanyFactory(
            name="New Company",
        )
        new_site = SiteFactory(
            name="New Site",
            company=new_company,
        )

        post_body = {"sites": [{"id": new_site.id, "name": new_site.name}]}

        # Note that sites is not updated in expected results
        expected = CompanySerializer(fake_company).data
        expected['dashboards'] = ['loneworker_company_dashboard', 'default']

        expected = {
            "status_code": 200,
            "body": expected
        }

        testclient.patch_request_test_helper(post_body, expected, path_params=pp)

    @pytest.mark.usefixtures("admin_login")
    def test_patch_company_distributor_failure(self, testclient, fake_company):
        """ Test that a patch to company's distributor that does not exist fails"""
        pp = {
            "company_id": fake_company.id
        }

        # company with id 100 does not exist
        post_body = {"distributor": {"id": 100}}

        expected = CompanySerializer(fake_company).data

        expected.update(post_body)

        expected = {
            "status_code": 400,
            "body": {
                "code": "stub_serializer",
                "detail": "There is no DistributorGroup with id 100"
            }
        }

        testclient.patch_request_test_helper(post_body, expected, path_params=pp)

    @pytest.mark.usefixtures("admin_login")
    def test_company_logo(self, testclient, fake_company, fakedevice, red_logo):
        """Test that getting a company with a logo includes said logo"""

        OrganizationLogoFactory(organization=fake_company)

        returned = _get_company_response(fake_company)
        returned["logo"] = RED_LOGO
        returned["dashboards"] = ['loneworker_company_dashboard', 'default']

        path_params = {
            "company_id": fake_company.id,
        }
        expected = {
            "status_code": 200,
            "body": returned,
        }
        testclient.get_request_test_helper(expected, path_params=path_params)


def _get_distributor_response(fake_distributor):
    """This is what should be returned from the FULL serializer
    """
    return {
        "location": model_to_dict(fake_distributor.location),
        "name": fake_distributor.name,
        "companies": [
            {
                "name": company.name,
                "id": company.id,
            } for company in fake_distributor.companies.all()
        ],
        "id": fake_distributor.id,
        "dashboards": ["default"],
        "logo": None
    }


def _get_stubbed_distributor_response(fake_distributor):
    """This is what should be returned from the STUB serializer
    """
    return {
        "name": fake_distributor.name,
        "id": fake_distributor.id,
    }


class TestDistributorsEndpoint:
    route = "/api/v3/distributors/"

    def test_distributors_denied(self, testclient):
        expected = AUTH_ERROR_RESP.copy()
        testclient.get_request_test_helper(expected)

    def test_get_multiple_distributors_stubbed_distributor(self, testclient, joeseed_login, fake_distributor):
        """It won't return the stuff from model_to_dict - only a subset of the
        distributor fields are returned, and the distributor reference should be stubbed
        """
        joeseed_login.add_org(fake_distributor)

        returned = _get_distributor_response(fake_distributor)

        expected = {
            "status_code": 200,
            "body": paginated_body([returned])
        }
        testclient.get_request_test_helper(expected)

    def test_query_param_not_stubbed(self, testclient, joeseed_login, fake_distributor):
        """passing stub as 'false' should not return a stubbed response
        """
        joeseed_login.add_org(fake_distributor)

        returned = _get_distributor_response(fake_distributor)

        query_params = {
            "stub": False,
        }
        expected = {
            "status_code": 200,
            "body": paginated_body([returned])
        }
        testclient.get_request_test_helper(expected, query_params=query_params)

    def test_get_stubbed_distributors(self, testclient, joeseed_login, fake_distributor):
        """when passing stub=true, only returns id/name"""
        joeseed_login.add_org(fake_distributor)

        returned = _get_stubbed_distributor_response(fake_distributor)

        query_params = {
            "stub": True,
        }
        expected = {
            "status_code": 200,
            "body": paginated_body([returned])
        }
        testclient.get_request_test_helper(expected, query_params=query_params)

    @pytest.mark.usefixtures("admin_login")
    def test_post_creates_distributor_location(self, testclient, fake_distributor):
        """ Test that a post created a new location object in DB """
        location_count = Location.objects.count()

        post_body = DistributorSerializer(fake_distributor).data
        post_body["id"] = None
        post_body["location"] = LocationSerializer(fake_distributor.location).data
        post_body["location"]["id"] = None
        post_body["location"]["updated_at"] = None
        post_body["location"]["created_at"] = None
        post_body["companies"] = []

        expected = {
            "status_code": 201,
            "body": post_body
        }

        testclient.post_request_test_helper(post_body, expected)

        assert Location.objects.count() == location_count + 1


class TestSpecificDistributorEndpoint:
    route = "/api/v3/distributors/{distributor_id}/"

    def test_distributors_denied(self, testclient, fake_distributor):
        path_params = {
            "distributor_id": fake_distributor.id,
        }
        expected = AUTH_ERROR_RESP.copy()
        testclient.get_request_test_helper(expected, path_params=path_params)

    def test_get_distributor_stubbed_distributor(self, testclient, joeseed_login, fake_distributor):
        """ Check that getting a distributor returns the full object """
        joeseed_login.add_org(fake_distributor)

        returned = _get_distributor_response(fake_distributor)

        path_params = {
            "distributor_id": fake_distributor.id,
        }
        expected = {
            "status_code": 200,
            "body": returned,
        }
        testclient.get_request_test_helper(expected, path_params=path_params)

    def test_query_param_not_stubbed(self, testclient, joeseed_login, fake_distributor):
        """ Check that passing stub=False returns the full object """
        joeseed_login.add_org(fake_distributor)

        returned = _get_distributor_response(fake_distributor)

        path_params = {
            "distributor_id": fake_distributor.id,
        }
        query_params = {
            "stub": False,
        }
        expected = {
            "status_code": 200,
            "body": returned,
        }
        testclient.get_request_test_helper(expected, query_params=query_params, path_params=path_params)

    def test_get_stubbed_distributors(self, testclient, joeseed_login, fake_distributor):
        """ Check that passing stub=True returns a stub """
        joeseed_login.add_org(fake_distributor)

        returned = _get_stubbed_distributor_response(fake_distributor)

        path_params = {
            "distributor_id": fake_distributor.id,
        }
        query_params = {
            "stub": True,
        }
        expected = {
            "status_code": 200,
            "body": returned,
        }
        testclient.get_request_test_helper(expected, query_params=query_params, path_params=path_params)

    def test_user_in_wrong_org_fails(self, testclient, joeseed_login, fake_distributor):
        """ Check user who is not in the org parental chain cannot access company """
        fake_distributor_2 = DistributorFactory(name="Another distributor")
        joeseed_login.add_org(fake_distributor_2)

        path_params = {
            "distributor_id": fake_distributor.id,
        }
        expected = {
            "status_code": 404,
            "body":   {
                "detail": "Not found."
              }
        }
        testclient.get_request_test_helper(expected, path_params=path_params)

    @pytest.mark.usefixtures("admin_login")
    def test_patch_updates_distributor_location(self, testclient, fake_distributor):
        """ Test that a patch updates the nested location field """
        pp = {
            "distributor_id": fake_distributor.id
        }

        # Change country
        post_body = DistributorSerializer(fake_distributor).data
        post_body["location"] = LocationSerializer(fake_distributor.location).data
        post_body["location"]["country"] = "Bolivia"
        post_body["location"]["updated_at"] = None

        expected = {
            "status_code": 200,
            "body": post_body
        }
        testclient.patch_request_test_helper(post_body, expected, path_params=pp)

    @pytest.mark.usefixtures("admin_login")
    def test_patch_fails_without_location_id(self, testclient, fake_distributor):
        """ Test that a patch fails to update location without id field """
        pp = {
            "distributor_id": fake_distributor.id
        }

        payload = {"location": {"locality": "test"}}

        expected = {
            "status_code": 400,
            "body": {
                "code": "stub_viewset",
                "detail":  "You need to provide an id to update a nested field"
            }
        }
        testclient.patch_request_test_helper(payload, expected, path_params=pp)

    @pytest.mark.usefixtures("admin_login")
    def test_patch_does_not_update_distributor_companies(self, testclient, fake_distributor):
        """ Test that a patch does not update child companies """
        pp = {
            "distributor_id": fake_distributor.id
        }
        new_distributor = DistributorFactory(
            name="New Distributor",
        )
        new_company = CompanyFactory(
            name="New Company",
            distributor=new_distributor,
        )

        post_body = {"companies": [{"id": new_company.id, "name": new_company.name}]}

        # Note that companies is not updated in expected results
        expected = DistributorSerializer(fake_distributor).data

        expected = {
            "status_code": 200,
            "body": expected
        }

        testclient.patch_request_test_helper(post_body, expected, path_params=pp)

    @pytest.mark.usefixtures("admin_login")
    def test_distributor_logo(self, testclient, fake_distributor, fakedevice,
                              red_logo):
        """Get a distributor with a logo and test that said logo is included"""

        OrganizationLogoFactory(organization=fake_distributor)

        returned = _get_distributor_response(fake_distributor)
        returned["logo"] = RED_LOGO

        path_params = {
            "distributor_id": fake_distributor.id,
        }
        expected = {
            "status_code": 200,
            "body": returned,
        }
        testclient.get_request_test_helper(expected, path_params=path_params)
