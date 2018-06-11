from unittest.mock import patch

from mockredis import mock_strict_redis_client
import pytest

from zconnect.testutils.factories import ActivitySubscriptionFactory

from django_demo import seed

from .factories import SiteFactory, TSRawDataFactory, WiringMappingFactory


@pytest.fixture(name="fake_site")
def fix_fake_site(db):
    return SiteFactory()


@pytest.fixture(name="fake_company")
def fix_fake_company(db, fake_site):
    return fake_site.company


@pytest.fixture(name="fake_distributor")
def fix_fake_distributor(db, fake_site):
    return fake_site.company.distributor


@pytest.fixture(name="fake_site_subsription")
def fix_site_subsription(db, fake_site):
    return ActivitySubscriptionFactory(organization=fake_site)


@pytest.fixture(name="fake_wiring_mapping")
def fix_fake_wiring_mapping():
    return WiringMappingFactory()


@pytest.fixture(name="fake_ts_raw_data")
def fix_fake_ts_raw_data(fakedevice):
    return TSRawDataFactory(device=fakedevice)


@pytest.fixture(name="fix_Demo_ts_data")
def fix_Demo_ts_data():
    seed.seed_data()


# Always mock redis
@pytest.fixture(autouse=True)
def fake_get_redis():
    with patch("zconnect.tasks.get_redis", return_value=mock_strict_redis_client()):
        yield
