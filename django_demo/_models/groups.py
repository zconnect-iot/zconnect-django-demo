from django.db import models

from zconnect.zc_billing.models import BilledOrganization


class OrgBase(BilledOrganization):

    class Meta:
        abstract = True

    location = models.ForeignKey("zconnect.Location", models.SET_NULL,
                                 blank=True, null=True)
    wiring_mapping = models.ForeignKey("WiringMapping", models.PROTECT,
                                       blank=True, null=True)


class DistributorGroup(OrgBase):
    """Demo DistributorGroup model

    Top level organization - each distributor serves multiple companies

    Attributes:
        location (Location): Where this distributor is
    """

    class Meta:
        ordering = ["location"]


class CompanyGroup(OrgBase):
    """Demo CompanyGroup model

    Middle level - each company has one distributor, but multiple sites

    Attributes:
        location (Location): Where this company is
        distributor (Boolean): The parent distributor of this compnay
    """

    distributor = models.ForeignKey(DistributorGroup, models.PROTECT, related_name="companies")

    # TODO
    # dashboards???

    class Meta:
        ordering = ["location"]

    @property
    def parent(self):
        return self.distributor


class SiteGroup(OrgBase):
    """Demo SiteGroup model

    Bottom level organization - each site is related to a single company

    Attributes:
        r_number (str): Arbitrary customer data used to identify this site
        location (Location): Where this site is
        company (CompanyGroup): parent company for site
    """

    r_number = models.CharField(max_length=50)

    company = models.ForeignKey(CompanyGroup, models.PROTECT, related_name="sites")

    # TODO
    # dashboards???

    class Meta:
        ordering = ["location"]

    @property
    def parent(self):
        return self.company
