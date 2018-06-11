import pytest
from django.core.exceptions import FieldError
from django_demo.testutils.factories import SiteFactory, CompanyFactory, WiringMappingFactory


class TestSite:
    """This might not look like its testing a lot but it is testing the
    properties work properly"""

    def test_no_site(self, fakedevice):
        assert not fakedevice.site

        fake_site_1 = SiteFactory()

        fakedevice.site = fake_site_1
        assert fakedevice.site == fake_site_1

        fake_site_2 = SiteFactory()

        fakedevice.site = fake_site_2
        assert fakedevice.site == fake_site_2

        del fakedevice.site

        assert not fakedevice.site

    def test_wrong_site_type(self, fakedevice):
        company = CompanyFactory()

        with pytest.raises(FieldError):
            fakedevice.site = company

    def test_del_no_site_works(self, fakedevice):
        """calling del should not raise an error if there's no site"""
        del fakedevice.site


