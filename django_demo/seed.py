import logging
import os

import django
from django.apps import apps
from django.conf import settings
from django.contrib.auth.hashers import make_password

logger = logging.getLogger(__name__)


def seed_data():
    from zconnect.testutils.factories import (
        UserFactory, DeviceSensorFactory, SensorTypeFactory,
        DeviceFactory, ProductTagsFactory,
        EventDefinitionFactory, BilledOrganizationFactory,
    )
    from django_demo.testutils.factories import FridgeFactory

    product = FridgeFactory()

    ProductTagsFactory(
        tag="fridge",
        product=product,
    )

    low_temp_boundary = 4
    EventDefinitionFactory(
        product=product,
        ref="low box temp",
        condition="process_box_temp<{}".format(low_temp_boundary),
        actions={
            "activity" : {
                "verb": "reported",
                "description": "Fridge temp is too cold. Less than {}°C".format(low_temp_boundary),
                "severity": 20,
                "category": "business metrics",
                "notify": True
            },
        },
        debounce_window=1, # very short debounce!
    )
    EventDefinitionFactory(
        product=product,
        ref="door opened",
        condition="property_door_opened==1",
        actions={
            "activity" : {
                "verb": "reported",
                "description": "Fridge door has been opened",
                "severity": 20,
                "category": "business metrics",
                "notify": True
            },
        },
        debounce_window=1, # very short debounce!
    )
    EventDefinitionFactory(
        product=product,
        ref="door opened",
        condition="property_cold_pipe_leak==1",
        actions={
            "activity" : {
                "verb": "reported",
                "description": "Fresh cooling liquid pipe is leaking",
                "severity": 20,
                "category": "business metrics",
                "notify": True
            },
        },
        debounce_window=1, # very short debounce!
    )
    EventDefinitionFactory(
        product=product,
        ref="door opened",
        condition="property_hot_pipe_leak==1",
        actions={
            "activity" : {
                "verb": "reported",
                "description": "Used cooling liquid pipe leaking",
                "severity": 20,
                "category": "business metrics",
                "notify": True
            },
        },
        debounce_window=1, # very short debounce!
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
        name="Fridge simulator",
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

    # joe seed
    joe = UserFactory()
    # joe.orgs.add(site1)
    joe.add_org(fake_org)

    # admin user
    admin = UserFactory(
        username="admin@zoetrope.io",
        email="admin@zoetrope.io",
        is_superuser=True,
        is_staff=True,
        password=make_password("SPITURSTUD"),
        first_name="bart",
        last_name="simpson",
    )

    admin.add_org(fake_org)


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
