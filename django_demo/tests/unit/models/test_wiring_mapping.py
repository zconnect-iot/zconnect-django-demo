
from django_demo.testutils.factories import WiringMappingFactory, SiteFactory


class TestMapping:

    def test_get_cascade_mapping(self, fakedevice):
        """
        Unfortunately, using fakedevice.site.blah doesn't work properly when
        settings things, so we just get a copy of the site and save that instead
        """

        fakedevice.site = SiteFactory()
        site = fakedevice.site

        wm1 = WiringMappingFactory(name="product wm")

        fakedevice.product.wiring_mapping = wm1
        fakedevice.product.save()

        assert fakedevice.get_canonical_mapping() == wm1

        wm4 = WiringMappingFactory(name="dist wm")

        site.company.distributor.wiring_mapping = wm4
        site.company.distributor.save()

        assert fakedevice.get_canonical_mapping() == wm4

        wm3 = WiringMappingFactory(name="company wm")

        site.company.wiring_mapping = wm3
        site.company.save()

        assert fakedevice.get_canonical_mapping() == wm3

        wm2 = WiringMappingFactory(name="site wm")

        site.wiring_mapping = wm2
        site.save()

        assert fakedevice.get_canonical_mapping() == wm2

    def test_get_distributor_mapping(self, fakedevice, fake_site):
        fakedevice.site = fake_site
        fakedevice.save()

        wm2 = WiringMappingFactory(name="distributor wm")
        fake_site.company.distributor.wiring_mapping = wm2
        fake_site.company.distributor.save()

        assert fakedevice.get_canonical_mapping() == wm2

        wm1 = WiringMappingFactory(name="device wm")

        fakedevice.wiring_mapping = wm1
        fakedevice.save()

        assert fakedevice.get_canonical_mapping() == wm1

    def test_get_product_mapping(self, fakedevice):
        wm2 = WiringMappingFactory(name="product wm")

        fakedevice.product.wiring_mapping = wm2
        fakedevice.product.save()

        assert fakedevice.get_canonical_mapping() == wm2

        wm1 = WiringMappingFactory(name="device wm")

        fakedevice.wiring_mapping = wm1
        fakedevice.save()

        assert fakedevice.get_canonical_mapping() == wm1

    def test_no_mapping_returns_none(self, fakedevice):
        assert fakedevice.get_canonical_mapping() is None
