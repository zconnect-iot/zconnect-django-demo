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

    product = FridgeFactory()

    ProductTagsFactory(
        tag="fridge",
        product=product,
    )

    EventDefinitionFactory(
        product=product,
        scheduled=True
    )

    EventDefinitionFactory(
        product=product,
        ref="fridge temp",
        condition="avg_600_box_temp<4",
        actions={
            "activity" : {
                "verb": "reported",
                "description": "Fridge temp is too cold. Average temp "
                               "over the past 10 minutes "
                               "was {avg_600_box_temp} °C",
                "severity": 20,
                "category": "business metrics",
                "notify": True
            },
        },
        debounce_window=300, # very short debounce!
    )

    sensor_types = []

    # All sensors for fridge product
    sensor_types.append(SensorTypeFactory(
        sensor_name="property_ambient_temp",
        unit="",
        product=product,
        aggregation_type="mean"
    ))
    sensor_types.append(SensorTypeFactory(
        sensor_name="process_box_temp",
        unit="°C",
        product=product,
        aggregation_type="mean"
    ))
    sensor_types.append(SensorTypeFactory(
        sensor_name="process_hot_coolant_temp",
        unit="°C",
        product=product,
        aggregation_type="mean"
    ))
    sensor_types.append(SensorTypeFactory(
        sensor_name="process_cold_coolant_temp",
        unit="°C",
        product=product,
        aggregation_type="mean"
    ))
    sensor_types.append(SensorTypeFactory(
        sensor_name="process_current_in",
        unit="Amps",
        product=product,
        aggregation_type="mean"
    ))
    sensor_types.append(SensorTypeFactory(
        sensor_name="property_set_point",
        unit="°C",
        product=product,
        aggregation_type="mean"
    ))
    sensor_types.append(SensorTypeFactory(
        sensor_name="property_door_opened",
        unit="",
        product=product
    ))
    sensor_types.append(SensorTypeFactory(
        sensor_name="property_hot_pipe_leak",
        unit="",
        product=product
    ))
    sensor_types.append(SensorTypeFactory(
        sensor_name="property_cold_pipe_leak",
        unit="",
        product=product
    ))
    sensor_types.append(SensorTypeFactory(
        sensor_name="process_thermostat",
        unit="°C",
        product=product,
        aggregation_type="mean"
    ))

    fake_org = BilledOrganizationFactory(name="fake_org")

    device = DeviceFactory(
        id=123,
        product=product,
        name="Front Door",
        # no fw_version
        online=False,
        sim_number="8944538525004714414",
    )
    device.orgs.add(fake_org)

    device_sensor_map = {}
    # Loop over all devices and sensors to create 35 device_sensors
    for sensor_type in sensor_types:
        device_sensor = DeviceSensorFactory(
            device=device,
            resolution=900,
            sensor_type=sensor_type,
        )
        # This key should include the resolution for cases where resolution is not constant
        # across all data, but for this case is it
        device_sensor_map["{}:{}".format(device.id, sensor_type.sensor_name)] = device_sensor

    activities = [
        {
            "verb": "reported",
            "description": "Box temp was less than 5",
            "severity": 20,
            "category": "business metric",
            "notify": False
        },
        {
            "verb": "reported",
            "description": "Box temp was less than 4",
            "severity": 30,
            "category": "maintenance",
            "notify": False
        },
        {
            "verb": "reported",
            "description": "Box temp was less than 3",
            "severity": 40,
            "category": "system",
            "notify": True
        }
    ]

    reading_map = {
        "thermostat": 1,
        "box_temp": 5,
        "hot_coolant_temp": 40,
        "cold_coolant_temp":4,
        "current_in":1
    }

    now = datetime.datetime.utcnow()

    # Populate an activity stream for each device
    for activity in activities:
        action_model.send(device, target=device, **activity)

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
