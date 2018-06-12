import datetime
from datetime import timedelta
import logging
import os

from actstream import action as action_model
import django
from django.apps import apps
from django.conf import settings
from django.contrib.auth.hashers import make_password

logger = logging.getLogger(__name__)


def seed_data():
    from zconnect.zc_timeseries.models import TimeSeriesData
    from zconnect.testutils.factories import (
        UserFactory, DeviceSensorFactory, SensorTypeFactory,
        DeviceFactory, ProductPreprocessorsFactory, ProductTagsFactory,
        EventDefinitionFactory, BilledOrganizationFactory,
    )
    from django_demo.testutils.factories import FridgeFactory

    # Create RTR Product, ProductPreprocessors and ProductTags
    # See https://sqldbm.com/Project/MySQL/Share/qvOpUcDfTnwexCqKFXLgBg for schema
    product = FridgeFactory()

    ProductTagsFactory(
        tag="sliding-door",
        product=product,
    )

    # All sensors for RTR door product
    sensor1 = SensorTypeFactory(
        sensor_name="thermostat",
        unit="",
        product=product
    )
    sensor2 = SensorTypeFactory(
        sensor_name="box_temp",
        unit="°C",
        product=product
    )
    sensor3 = SensorTypeFactory(
        sensor_name="hot_coolant_temp",
        unit="°C",
        product=product
    )
    sensor4 = SensorTypeFactory(
        sensor_name="cold_coolant_temp",
        unit="°C",
        product=product
    )
    sensor5 = SensorTypeFactory(
        sensor_name="current_in",
        unit="Amps",
        product=product
    )

    fake_org = BilledOrganizationFactory(name="fake_org")

    device1 = DeviceFactory(
        product=product,
        name="Front Door",
        # no fw_version
        online=False,
        sim_number="8944538525004714414",
    )
    device1.orgs.add(fake_org)

    device1a = DeviceFactory(
        product=product,
        name="Back Door",
        # no fw_version
        online=False,
        sim_number="123456789",
    )
    device1a.orgs.add(fake_org)

    device2 = DeviceFactory(
        product=product,
        name="Front Door",
        # no fw_version
        online=False,
        sim_number="8944538525004715387",
    )
    device2.orgs.add(fake_org)

    devices = [device1, device1a, device2]
    sensor_types = [sensor1, sensor2, sensor3, sensor4, sensor5]
    device_sensor_map = {}
    # Loop over all devices and sensors to create 35 device_sensors
    for device in devices:
        for sensor_type in sensor_types:
            device_sensor = DeviceSensorFactory(
                device=device,
                resolution=900,
                sensor_type=sensor_type,
            )
            # This key should include the resolution for cases where resolution is not constant
            # across all data, but for this case is it
            device_sensor_map["{}:{}".format(device.id, sensor_type.sensor_name)] = device_sensor

    reading_map = {
        "thermostat": 1,
        "box_temp": 5,
        "hot_coolant_temp": 40,
        "cold_coolant_temp":4,
        "current_in":1
    }

    now = datetime.datetime.utcnow()
    # Create a TimeSeriesData entries, attaching it to the appropriate device_sensor
    ts_data_to_save = []
    for device in devices:
        for sensor_type in sensor_types:
            for i in range(100):
                ds_map_key = "{}:{}".format(device.id, sensor_type.sensor_name)
                name = sensor_type.sensor_name
                value = reading_map.get(name, 1)
                ts_data_to_save.append(TimeSeriesData(
                    ts=now - timedelta(minutes=15*i),
                    sensor=device_sensor_map[ds_map_key],
                    #value=sin(i),
                    value=value
                ))

    TimeSeriesData.objects.bulk_create(ts_data_to_save)

     # joe seed
    joe = UserFactory()
    # joe.orgs.add(site1)
    joe.add_org(fake_org)

    # admin user
    UserFactory(
        username="admin@zoetrope.io",
        email="admin@zoetrope.io",
        is_superuser=True,
        is_staff=True,
        password=make_password("SPITURSTUD"),
        first_name="bart",
        last_name="simpson",
    )


def seed_project():
    logger.debug("Started seeding data")
    User = apps.get_model(settings.AUTH_USER_MODEL)

    try:
        User.objects.filter(username="admin@zoetrope.io").get()
    except User.DoesNotExist:
        pass
    else:
        if os.getenv("DJANGO_SEED_PROJECT_ONCE"):
            logger.debug("Not seeding again")
            return
        else:
            logger.critical("Database has already been seeded - seeding again")

    seed_data()

    logger.debug("Finished seeding data")


if __name__ == "__main__":
    django.setup(set_prefix=False)
    seed_project()
