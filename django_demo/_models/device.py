import logging

from django.core.exceptions import FieldError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from zconnect.models import AbstractDevice
from zconnect.util.general import nested_getattr

logger = logging.getLogger(__name__)


class DemoDevice(AbstractDevice):
    """ Represents an Demo Device

    Note:
        This uses multi table inheritance:
        https://docs.djangoproject.com/en/2.0/topics/db/models/#multi-table-inheritance
        This means there is a zconnect_device table as well as a
        djangodemo_demodevice table, which has a FK to the device table. This is
        mainly because the fixtures defined for seed data and tests in the
        zconnect-django module only load into the zconnect_device table and we
        can't easily dynamically change it. This shouldn't really be an issue.

    Attributes:
        site (StringField): SiteGroup the device belongs to
        sim_number (str): The SIM ICCID (number up to 22 digits)
        email_site_emergency_close (bool): Whether to send email to site on emergency close
        email_company_emergency_close (bool): Whether to send email to company on emergency close
        email_distributor_emergency_close (bool): Whether to send email to distributor on emergency
                                                  close
    """

    sim_number = models.CharField(max_length=25, blank=True)
    email_site_emergency_close = models.BooleanField(default=False)
    email_company_emergency_close = models.BooleanField(default=False)
    email_distributor_emergency_close = models.BooleanField(default=False)
    wiring_mapping = models.ForeignKey("WiringMapping", models.PROTECT, blank=True, null=True)

    class Meta:
        ordering = ["product"]
        default_permissions = ["view", "change", "add", "delete"]

    def __get_site(self):
        """Actually retrieve the site

        This is fairly badly implemented at the moment, but it's the easiest way
        to find all sites give a list of groups

        Todo:

            Currently just logs a warning if there's more that one Site
            associated - needs to have validation as well
        """

        from .groups import SiteGroup
        query_sites = SiteGroup.objects.filter(pk__in=[i.id for i in self.orgs.all()])
        if query_sites.count() > 1:
            logger.warning("Device has more than 1 site associated with it")

        site = query_sites.first()
        return site

    def _get_site(self):
        return self.__get_site()

    def _set_site(self, new_site):
        from .groups import SiteGroup
        if not isinstance(new_site, SiteGroup):
            raise FieldError(_("Invalid site"))

        # remove the old one if it exists
        self._del_site()

        self.orgs.add(new_site)

    def _del_site(self):
        existing_site = self.__get_site()
        if existing_site:
            existing_site.devices.remove(self)

    site = property(_get_site, _set_site, _del_site)

    @classmethod
    def stats(cls, sites, start, end):
        """TODO"""
        raise NotImplementedError

    def get_canonical_mapping(self):
        """
        Runs up the reference field tree, starting from device and checks whether
        the mapping exists on each of the models it finds.

        Device has a reference to site, which has a ref to company which has a ref
        to distributor. We have to get the product off the device directly.

        """
        ordering = ['',     # This will check the device first. Note no '.'
                    'site.',
                    'site.company.',
                    'site.company.distributor.',
                    'product.']


        for entity in ordering:
            maybe_mapping = nested_getattr(self, entity + 'wiring_mapping')
            if maybe_mapping:
                if entity == '':
                    entity = 'device'
                logger.debug("Found matching Demo wiring mapping on %s, name: %s",
                             entity, maybe_mapping.name)
                return maybe_mapping

        return None

    @property
    def notify_organizations(self):
        """Site is supposed to be notified I guess?
        """
        site = self.site
        if site:
            return [site]
        else:
            return []
