import logging

from django.db import models

from zconnect.models import AbstractDevice

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
        sim_number (str): The SIM ICCID (number up to 22 digits)
    """

    sim_number = models.CharField(max_length=25, blank=True)

    class Meta:
        ordering = ["product"]
        default_permissions = ["view", "change", "add", "delete"]
