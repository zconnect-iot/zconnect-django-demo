import pytest

from actstream.models import Action

from zconnect.testutils.fixtures import *
from django_demo.testutils.fixtures import *
from zconnect.activity_stream import device_activity
from zconnect.testutils.helpers import paginated_body
from zconnect.serializers import ActivitySubscriptionSerializer


class TestUserSubscriptions:
    route = "/api/v3/users/{user_id}/subscriptions"

    def test_user_site_subscriptions(self, testclient, joeseed_login, fake_site_subsription):
        """ Test a users site specific subscription is returned """
        pp = {
            "user_id": joeseed_login.id,
        }
        activity_subscription = ActivitySubscriptionSerializer(fake_site_subsription).data

        expected = {
            "status_code": 200,
            "body": [activity_subscription],
        }
        testclient.get_request_test_helper(expected, path_params=pp)
