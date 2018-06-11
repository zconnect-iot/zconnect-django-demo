import pytest
import django

import datetime
from dateutil.relativedelta import relativedelta
from math import sin

from zconnect.zc_timeseries.models import TimeSeriesData
from zconnect.testutils.fixtures import *
from zconnect.testutils.factories import TimeSeriesDataFactory, SensorTypeFactory, DeviceSensorFactory
from zconnect._models.event import EventDefinition


class TestDeviceModel:

    def test_get_latest_data(self, fake_ts_data, fakedevice):
        extra_sensor_type = SensorTypeFactory(
            sensor_name="temperature sensor",
            unit="celsius",
        )
        TimeSeriesDataFactory(
            sensor__sensor_type=extra_sensor_type,
            sensor__device=fakedevice,
        )

        r = fakedevice.get_latest_ts_data()
        assert len(r) == 2

    def test_clear_settings(self, fake_device_event_definition, fakedevice):
        pre_clear = len(EventDefinition.objects.all())

        fakedevice.clear_settings()

        post_clear = len(EventDefinition.objects.all())

        assert post_clear < pre_clear
        assert not fakedevice.event_defs.all()


class TestInvalidDataFetch:

    def test_invalid_resolution_fetch(self, fakedevice, fake_ts_data):
        with pytest.raises(django.db.DataError):
            fakedevice.optimised_data_fetch(fake_ts_data, resolution=777)


@pytest.mark.parametrize("agg_impl", (
    "numpy",
    pytest.mark.xfail("sql"),
))
class TestFetchImplementations:

    @pytest.mark.xfail(reason="Bad test logic")
    @pytest.mark.parametrize("aggregation_type", (
        "sum",
        "median",
        "mean",
        "max",
        "min",
    ))
    def test_fetch_aggregated(self, fakedevice, aggregation_type, agg_impl, settings):
        """Note: the logic for this test is a bit wrong as it was originally
        written assuming there would be no missing data and that the way data
        was fetched was different.

        This needs fixing
        """
        extra_sensor_type = SensorTypeFactory(
            sensor_name="temperature sensor",
            unit="celsius",
            aggregation_type=aggregation_type,
        )
        new_sensor = DeviceSensorFactory(
            sensor_type=extra_sensor_type,
            device=fakedevice,
        )

        now = datetime.datetime.utcnow()

        n_samples = 48
        resolution = new_sensor.resolution*2
        hours_ago = 2

        created = TimeSeriesData.objects.bulk_create([
            TimeSeriesData(
                ts=now - relativedelta(minutes=2*i),
                sensor=new_sensor,
                value=sin(i),
            ) for i in range(n_samples)
        ])

        settings.ZCONNECT_TS_AGGREGATION_ENGINE = agg_impl

        result = fakedevice.optimised_data_fetch(
            now - relativedelta(hours=hours_ago),
            resolution=resolution
        )

        assert result["temperature sensor"][-1].ts == now

        values = [i.value for i in result["temperature sensor"]]
        aggregation_factor = int(resolution//new_sensor.resolution)

        # resolution = 2x sensor resolution
        assert len(values) == int((new_sensor.resolution/aggregation_factor)/hours_ago)

        # Similar to the aggregate_python, explicitly chunk + calculate
        def chunks():
            for i in range(0, len(created), aggregation_factor):
                yield [d.value for d in created[i:i+aggregation_factor]]

        if aggregation_type == "sum":
            expected = [sum(i) for i in chunks()]
            assert values == pytest.approx(expected)
        elif aggregation_type == "min":
            expected = [min(i) for i in chunks()]
            assert values == pytest.approx(expected)
        elif aggregation_type == "max":
            expected = [max(i) for i in chunks()]
            assert values == pytest.approx(expected)

    def test_fetch_values_one_day(self, fakedevice, fakesensor, agg_impl, settings):
        """Create data for a few days then try to fetch data for 1 day with a
        resolution of 1 hour - should return 24 values """
        now = datetime.datetime.utcnow()

        TimeSeriesData.objects.bulk_create([
            TimeSeriesData(
                ts=now - relativedelta(seconds=fakesensor.resolution*i),
                sensor=fakesensor,
                value=sin(i),
            ) for i in range(2000)
        ])

        day_ago = now - relativedelta(days=1)

        settings.ZCONNECT_TS_AGGREGATION_ENGINE = agg_impl

        data = fakedevice.optimised_data_fetch(
            data_start=day_ago,
            data_end=now,
            resolution=3600,
        )

        values = data["power_sensor"]

        assert len(values) == 24

    def test_missing_data(self, fakedevice, fakesensor, agg_impl, settings):
        """If there is missing data it should still return the same number of
        values, but some of them might just be wrong"""
        now = datetime.datetime.utcnow()

        # Create a chunk at the beginning of the day
        TimeSeriesData.objects.bulk_create([
            TimeSeriesData(
                ts=now - relativedelta(seconds=fakesensor.resolution*i),
                sensor=fakesensor,
                value=sin(i),
            ) for i in range(400, 800)
        ])

        # And some more recent - gap in between
        TimeSeriesData.objects.bulk_create([
            TimeSeriesData(
                ts=now - relativedelta(seconds=fakesensor.resolution*i),
                sensor=fakesensor,
                value=sin(i),
            ) for i in range(0, 300)
        ])

        day_ago = now - relativedelta(days=1)

        settings.ZCONNECT_TS_AGGREGATION_ENGINE = agg_impl

        data = fakedevice.optimised_data_fetch(
            data_start=day_ago,
            data_end=now,
            resolution=3600,
        )

        values = data["power_sensor"]

        assert len(values) == 24
        assert values[-1].ts == now - relativedelta(seconds=3600)
