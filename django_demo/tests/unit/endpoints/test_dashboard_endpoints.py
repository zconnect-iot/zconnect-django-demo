import datetime

import pytest

from zconnect.testutils.fixtures import *
from zconnect.testutils.helpers import paginated_body
from django_demo.testutils.factories import SiteFactory
from django_demo.testutils.fixtures import *
from django_demo.serializers import SiteSerializer
from django_demo.models import CompanyGroup

PRODUCT = {
    "name":"ECO3",
    "id": 1
}

FRONT_DOOR_GC = {
    "name":"Front Door",
    "product": PRODUCT,
    "id": 1
}

BACK_DOOR_GC = {
    "name":"Back Door",
    "product": PRODUCT,
    "id": 2
}

FRONT_DOOR_BW = {
    "name":"Front Door",
    "product": PRODUCT,
    "id": 3
}

GUYS_CLIFFE = {
    "name": "BP Guys Cliffe",
    "id": 3
}

BARNWOOD = {
    "name":"BP Barnwood",
    "id": 4
}

COMPANY_STATS = {
    "active":3,
    "closed_time":202500.0,
    "closed_time_percentage": 75.0,
    "panic_count": 2.0,
    "soft_close_count": 30.0,
    "total": 3,
    "total_operations": 1500.0,
    "total_time":90000.0,
}

class TestSiteDashboardEndpoint:
    route = "/api/v3/sites/{site_id}/dashboards/"

    @pytest.mark.usefixtures("joeseed_login")
    def test_dashboard(self, testclient, fix_Demo_ts_data):
        body = {
            "devices":[
                {
                    "soft_close_time": 50.0,
                    "closed_time": 67500.0,
                    "closed_time_percentage": 75.0,
                    "device": FRONT_DOOR_BW,
                    "site": BARNWOOD,
                    "panic_count": 0.0,
                    "total_operations": 500.0,
                    "soft_close_count": 10.0,
                    "active": True,
                    "r_number":"R14977"
                }
            ],
            "site_stats": {
                "active":1,
                "closed_time":67500.0,
                "closed_time_percentage": 75.0,
                "panic_count": 0.0,
                "soft_close_count": 10.0,
                "total": 1,
                "total_operations": 500.0,
                "total_time":90000.0,
            },
            "company_stats": COMPANY_STATS
        }
        expected = {
            "body": body,
            "status_code": 200
        }
        pp = {"site_id": 4}
        qp = {"dashboard_name": "loneworker_site_dashboard"}
        testclient.get_request_test_helper(expected, path_params=pp, query_params=qp)

    @pytest.mark.usefixtures("joeseed_login")
    def test_date_range(self, testclient, fix_Demo_ts_data):
        body = {
            "devices":[
                {
                    "soft_close_time": 5.0,
                    "closed_time": 2700.0,
                    "closed_time_percentage": 75.0,
                    "device": FRONT_DOOR_GC,
                    "site": GUYS_CLIFFE,
                    "panic_count": 1.0,
                    "total_operations": 20.0,
                    "soft_close_count": 1.0,
                    "active": True,
                    "r_number":"R10668"
                },
                {
                    "soft_close_time": 5.0,
                    "closed_time": 2700.0,
                    "closed_time_percentage": 75.0,
                    "device": BACK_DOOR_GC,
                    "site": GUYS_CLIFFE,
                    "panic_count": 0.0,
                    "total_operations": 20.0,
                    "soft_close_count": 1.0,
                    "active": True,
                    "r_number":"R10668"
                }
            ],
            "site_stats": {
                "active": 2,
                "closed_time": 5400.0,
                "closed_time_percentage": 75.0,
                "panic_count": 1.0,
                "soft_close_count": 2.0,
                "total": 2,
                "total_operations": 40.0,
                "total_time":3600.0,
            },
            "company_stats": {
                "active": 3,
                "closed_time": 8100.0,
                "closed_time_percentage": 75.0,
                "panic_count": 1.0,
                "soft_close_count": 3.0,
                "total": 3,
                "total_operations": 60.0,
                "total_time":3600.0,
            }
        }
        expected = {
            "body": body,
            "status_code": 200
        }
        pp = {"site_id": 3}
        now = datetime.datetime.now()
        start = (now - datetime.timedelta(hours=1)).timestamp()
        end = (now - datetime.timedelta(hours=0)).timestamp()
        query_params = {
            "start": str(int(start*1000)),
            "end": str(int(end*1000)),
            "dashboard_name": "loneworker_site_dashboard"
        }
        testclient.get_request_test_helper(
            expected,
            path_params=pp,
            query_params=query_params
        )

    @pytest.mark.usefixtures("joeseed_login")
    def test_incorrect_date_range(self, testclient, fix_Demo_ts_data):
        expected = {
            "body": {
                "start": "Start must be a unix timestamp",
                "end": "End must be a unix timestamp"
            },
            "status_code": 400
        }
        pp = {
            "site_id": 3
        }
        query_params = {
            "start": "hello",
            "end": "goodbye",
            "dashboard_name": "loneworker_site_dashboard"
        }
        testclient.get_request_test_helper(expected, path_params=pp, query_params=query_params)

    @pytest.mark.usefixtures("joeseed_login")
    def test_missing_type(self, testclient, fix_Demo_ts_data):
        expected = {
            "body": {
                "dashboard_name": "Dashboard name is required"
            },
            "status_code": 400
        }
        pp = {
            "site_id": 3
        }
        testclient.get_request_test_helper(expected, path_params=pp)

    @pytest.mark.usefixtures("joeseed_login")
    def test_wrong_type(self, testclient, fix_Demo_ts_data):
        expected = {
            "body": {
                "dashboard_name": "Dashboard name does not match known dashboards"
            },
            "status_code": 400
        }
        pp = {
            "site_id": 3
        }
        qp = {"dashboard_name": "dashboard_schmashboard"}
        testclient.get_request_test_helper(expected, path_params=pp, query_params=qp)

    @pytest.mark.usefixtures("joeseed_login")
    def test_company_dashboard(self, testclient, fix_Demo_ts_data):
        expected = {
            "body": {
                "dashboard_name": "The requested dashboard is only available for companies"
            },
            "status_code": 400
        }
        pp = {
            "site_id": 3
        }
        qp = {"dashboard_name": "loneworker_company_dashboard"}
        testclient.get_request_test_helper(expected, path_params=pp, query_params=qp)

    @pytest.mark.usefixtures("joeseed_login")
    def test_dataless_date_range(self, testclient, fix_Demo_ts_data):
        body = {
            "devices":[
                {
                    "soft_close_time": 0.0,
                    "closed_time": 0.0,
                    "closed_time_percentage": 0.0,
                    "device": FRONT_DOOR_BW,
                    "site": BARNWOOD,
                    "panic_count": 0.0,
                    "total_operations": 0.0,
                    "soft_close_count": 0.0,
                    "active": False,
                    "r_number":"R14977"
                }
            ],
            "site_stats": {
                "active": 0,
                "closed_time": 0.0,
                "closed_time_percentage": 0.0,
                "panic_count": 0.0,
                "soft_close_count": 0.0,
                "total": 1,
                "total_operations": 0.0,
                "total_time": 0.0,
            },
            "company_stats": {
                "active": 0,
                "closed_time": 0.0,
                "closed_time_percentage": 0.0,
                "panic_count": 0.0,
                "soft_close_count": 0.0,
                "total": 3,
                "total_operations": 0.0,
                "total_time": 0.0,
            }

        }
        expected = {
            "body": body,
            "status_code": 200
        }
        pp = {
            "site_id": 4
        }
        now = datetime.datetime.now()
        query_params = {
            "start": str(int((now - datetime.timedelta(weeks=2)).timestamp())),
            "end": str(int((now - datetime.timedelta(weeks=1)).timestamp())),
            "dashboard_name": "loneworker_site_dashboard"
        }
        testclient.get_request_test_helper(
            expected,
            path_params=pp,
            query_params=query_params
        )

class TestCompanyDashboardEndpoint:
    route = "/api/v3/companies/{company_id}/dashboards/"

    @pytest.mark.usefixtures("admin_login")
    def test_dashboard(self, testclient, fix_Demo_ts_data):
        body = {
            "devices":[
                {
                    "soft_close_time": 50.0,
                    "closed_time": 67500.0,
                    "closed_time_percentage": 75.0,
                    "device": FRONT_DOOR_GC,
                    "site": GUYS_CLIFFE,
                    "panic_count": 2.0,
                    "total_operations": 500.0,
                    "soft_close_count": 10.0,
                    "active": True,
                    "r_number":"R10668"
                },
                {
                    "soft_close_time": 50.0,
                    "closed_time": 67500.0,
                    "closed_time_percentage": 75.0,
                    "device": BACK_DOOR_GC,
                    "site": GUYS_CLIFFE,
                    "panic_count": 0.0,
                    "total_operations": 500.0,
                    "soft_close_count": 10.0,
                    "active": True,
                    "r_number":"R10668"
                },
                {
                    "soft_close_time": 50.0,
                    "closed_time": 67500.0,
                    "closed_time_percentage": 75.0,
                    "device": FRONT_DOOR_BW,
                    "site": BARNWOOD,
                    "panic_count": 0.0,
                    "total_operations": 500.0,
                    "soft_close_count": 10.0,
                    "active": True,
                    "r_number":"R14977"
                },
            ],
            "company_stats": COMPANY_STATS
        }
        expected = {
            "body": body,
            "status_code": 200
        }
        pp = {"company_id": 2}
        qp = {"dashboard_name": "loneworker_company_dashboard"}
        testclient.get_request_test_helper(expected, path_params=pp, query_params=qp)

    @pytest.mark.usefixtures("admin_login")
    def test_company_dashboard(self, testclient, fix_Demo_ts_data):
        expected = {
            "body": {
                "dashboard_name": "The requested dashboard is only available for sites"
            },
            "status_code": 400
        }
        pp = {"company_id": 2}
        qp = {"dashboard_name": "loneworker_site_dashboard"}
        testclient.get_request_test_helper(expected, path_params=pp, query_params=qp)
