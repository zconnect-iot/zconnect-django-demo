import datetime
from math import sin

from dateutil.relativedelta import relativedelta
import django
from django.apps import apps
from django.conf import settings
import pytest

from zconnect._models.event import EventDefinition
from zconnect.testutils.factories import (
    DeviceFactory, DeviceSensorFactory, SensorTypeFactory, TimeSeriesDataFactory)
from zconnect.zc_timeseries.models import TimeSeriesData

Device = apps.get_model(settings.ZCONNECT_DEVICE_MODEL)


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


@pytest.fixture(autouse=True)
def ft(settings):
    settings.DEBUG = True


class TestOptimisedLatestDataFetch:

    @pytest.fixture(name="empty_devices")
    def fix_spawn_devices(self, db):
        devices = [DeviceFactory() for i in range(3)]
        for dn, d in enumerate(devices):
            for i in range(3):
                DeviceSensorFactory(
                    device=d,
                    sensor_type__sensor_name="{}-{}".format(dn+1, i+1)
                )

        import functools
        self.check_return_values = functools.partial(self.__unbound_check_return_values, empty_devices=devices)
        return devices

    def __unbound_check_return_values(self, data, expect_data=True, *, empty_devices=None):
        # 3 devices
        assert len(data) == 3

        # extract data values for tests
        data = sum((list(i.values()) for i in data.values()), []) #data.values()

        if expect_data:
            # always 9 readings
            assert len(data) == 9

            # 1 reading per sensor per device
            assert len(set([(i.sensor, i.sensor.device) for i in data])) == 9
            # Make sure it's the last one
            last_readings = [(
                TimeSeriesData.objects
                    .filter(sensor=s)
                    .latest()
            ) for d in empty_devices for s in d.sensors.all()]
            assert all(i in last_readings for i in data)

    def test_get_latest_optimised_no_data(self, empty_devices):
        """Should return 9 values even if they are empty?"""
        data = Device.latest_ts_data_optimised(empty_devices)

        self.check_return_values(data, expect_data=False)

    def test_get_latest_optimised_with_data(self, empty_devices):
        """exactly 1 data point per sensor per device"""
        for d in empty_devices:
            for s in d.sensors.all():
                TimeSeriesDataFactory(
                    sensor=s,
                )

        data = Device.latest_ts_data_optimised(empty_devices)

        self.check_return_values(data)

    def test_get_latest_optimised_with_extra_data(self, empty_devices):
        """more than 1 data point per sensor per device"""
        for d in empty_devices:
            for s in d.sensors.all():
                for m in range(3):
                    TimeSeriesDataFactory(
                        sensor=s,
                        value=m,
                    )

        data = Device.latest_ts_data_optimised(empty_devices)

        self.check_return_values(data)

    def test_get_latest_optimised_with_extra_data_and_extra_device(self, empty_devices, fakedevice):
        """Extra device shouldn't interfere"""
        for d in empty_devices:
            for s in d.sensors.all():
                for m in range(3):
                    TimeSeriesDataFactory(
                        sensor=s,
                        value=m,
                    )

        data = Device.latest_ts_data_optimised(empty_devices)

        self.check_return_values(data)


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
