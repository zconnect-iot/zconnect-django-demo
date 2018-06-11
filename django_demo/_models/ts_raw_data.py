from django.conf import settings
from django.db import models

from zconnect.models import ModelBase


class TSRawData(ModelBase):
    """
    A model to store any raw timeseries data. This is essentially write only
    storage at the moment, there is no mechanism for interpreting it.

    It is used to ensure that any future changes to the data interpretation are
    not impossible because we haven't stored the original data packet.

    We are only going to store a device reference, a timestamp and a data packet
    string.
    """

    timestamp = models.DateTimeField()
    raw_data = models.CharField(max_length=500)
    device = models.ForeignKey(
        settings.ZCONNECT_DEVICE_MODEL,
        models.CASCADE,
        related_name="ts_raw_data",
        blank=False
    )
