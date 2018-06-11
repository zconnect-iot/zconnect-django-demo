import uuid
from unittest.mock import patch, Mock
import pytest

from django.contrib.auth.models import Group
from rest_auth.utils import import_callable
from django_demo.models import DistributorGroup, CompanyGroup, SiteGroup


class TestExtraFields:
    route = "/api/v3/auth/login/"

    @pytest.mark.parametrize("add_demo_org", (
        ("site"),
        ("company"),
        ("distributor"),
    ))
    def test_jwt_claims(self, testclient, joeseed, settings, add_demo_org, fake_site):
        """Make sure claims are as expected"""
        post_body = {
            "username": joeseed.username,
            "password": "test_password",
        }

        if add_demo_org == "site":
            fake_org = fake_site
        elif add_demo_org == "company":
            fake_org = fake_site.company
        elif add_demo_org == "distributor":
            fake_org = fake_site.company.distributor

        joeseed.add_org(fake_org)
        joeseed.save()

        expected = {
            "status_code": 200,
            "body": {
                "token": None,
                "token_type": "sliding",
            }
        }
        result = testclient.post_request_test_helper(post_body, expected)

        # This might be monkey patched - dynamically import like in the library
        from rest_framework_simplejwt.state import token_backend
        decoded = token_backend.decode(result.json()["token"])

        serializer = import_callable(settings.ZCONNECT_JWT_SERIALIZER)
        expected_serialized = serializer(joeseed).data

        # These two are added manually by us in the serializer
        assert decoded["email"] == expected_serialized["email"] == joeseed.email
        # Groups (perhaps they should be renamed?) is now a list of the companies associated with a user, as strings
        assert len(decoded["company_slugs"]) == len(expected_serialized["company_slugs"]) == (0 if add_demo_org == "distributor" else 1)
        # name is the primary key, so this should check correctly
        # assert decoded["groups"][0]["name"] == expected_serialized["groups"][0]["name"] == list(joeseed.groups.all())[0].name

        assert decoded["token_type"] == "sliding"
        assert decoded["user_id"] == joeseed.id

        assert decoded["orgs"][0]["type"] == add_demo_org
