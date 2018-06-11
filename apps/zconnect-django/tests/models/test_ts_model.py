import datetime

import django
import pytest

from zconnect.testutils.factories import DeviceSensorFactory
from zconnect.zc_timeseries.models import TimeSeriesData


class TestTSModel:

    def test_unique_same_sensor(self, fakesensor):
        """Same ts with same sensor raises an error"""
        now = datetime.datetime.utcnow()

        TimeSeriesData.objects.create(
            ts=now,
            sensor=fakesensor,
            value=1.0,
        )

        with pytest.raises(django.db.utils.IntegrityError):
            TimeSeriesData.objects.create(
                ts=now,
                sensor=fakesensor,
                value=1.0,
            )

    def test_unique_different_sensor(self, fakesensor):
        """Same ts but different sensors from different devices should be
        fine"""
        now = datetime.datetime.utcnow()

        TimeSeriesData.objects.create(
            ts=now,
            sensor=fakesensor,
            value=1.0,
        )

        extra_sensor = DeviceSensorFactory()

        TimeSeriesData.objects.create(
            ts=now,
            sensor=extra_sensor,
            value=1.0,
        )
