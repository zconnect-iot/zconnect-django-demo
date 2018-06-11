import pytest
from django.core.management import call_command
from django.conf import settings
from zconnect.testutils.fixtures import *
from django_demo.testutils.fixtures import *

# @pytest.fixture(name="load_groups")
# def fix_load_test_groups(db):
#     from django_demo.models import DistributorGroup, CompanyGroup, SiteGroup
#     d = DistributorGroup.objects.create(name="Cool distributor")
#     c = CompanyGroup.objects.create(name="OK company", distributor=d)
#     SiteGroup.objects.create(name="Bad site", company=c)
#
#
# @pytest.fixture(name="load_devices")
# def fix_load_devices(load_users, load_groups, db):
#     """Overload fixture to make tests work
#     """
#     call_command("loaddata", "device", app_label="zconnect")
#     call_command("loaddata", "device", app_label="django_demo")


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker, request):
    with django_db_blocker.unblock():
        pass
        # request.getfixturevalue("joeseedb")
        # request.getfixturevalue("adminb")

    # settings.DATABASES["default"] = {
    #     # 'default': {
    #         'ENGINE': 'django.db.backends.postgresql',
    #         "NAME": "demo",
    #         'HOST': 'localhost',
    #         "USER": "django",
    #         "PASSWORD": "shae6woifaeTah7Eipax",
    #     # }
    # }


@pytest.fixture(scope='session')
def django_db_modify_db_settings():
    pass
