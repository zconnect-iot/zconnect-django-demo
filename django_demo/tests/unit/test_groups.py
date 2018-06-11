
class TestGroupModels:

    def test_parents(self, fake_site):
        assert fake_site.company
        assert fake_site.company.distributor
