import datetime
from datetime import timedelta
import logging
import os

from actstream import action as action_model
import django
from django.apps import apps
from django.conf import settings
from django.contrib.auth.hashers import make_password

from django_demo.testutils.factories import MappingFactory, WiringMappingFactory

logger = logging.getLogger(__name__)


def seed_data():
    from zconnect.zc_timeseries.models import TimeSeriesData
    from zconnect.testutils.factories import (
        UserFactory, DeviceSensorFactory, SensorTypeFactory,
        DeviceFactory, ProductPreprocessorsFactory, ProductTagsFactory,
        EventDefinitionFactory,
    )
    from django_demo.testutils.factories import (
        DistributorFactory, CompanyFactory, SiteFactory, Eco3Factory
    )

    # Create Demo Product, ProductPreprocessors and ProductTags
    # See https://sqldbm.com/Project/MySQL/Share/qvOpUcDfTnwexCqKFXLgBg for schema
    product = Eco3Factory()
    ProductPreprocessorsFactory(
        preprocessor_name="demo_mapping",
        product=product,
    )
    ProductTagsFactory(
        tag="sliding-door",
        product=product,
    )

    EventDefinitionFactory(
        product=product,
        scheduled=True
    )

    EventDefinitionFactory(
        product=product,
        ref="panic test",
        condition="panic>0",
        actions={
            "activity" : {
                "verb": "reported",
                "description": "Emergency close operation performed",
                "severity": 20,
                "category": "business metrics",
                "notify": True
            },
        },
        debounce_window=10, # very short debounce!
    )

    EventDefinitionFactory(
        product=product,
        ref="open time",
        condition="sum_600_door_open_time>540",
        actions={
            "activity" : {
                "verb": "reported",
                "description": "The door was open for more than 90% "
                                "of the time over the past 10 minutes. "
                                "Was open for {sum_600_door_open_time}s",
                "severity": 20,
                "category": "business metrics",
                "notify": True
            },
        },
        debounce_window=300, # very short debounce!
    )

    wiring_mapping = WiringMappingFactory(name="BP Trial Mapping")

    maps = [
        ("external_activation", "pulse_counter__10", wiring_mapping),
        ("soft_close", "pulse_counter__8", wiring_mapping),
        ("door_open_count", "pulse_counter__4", wiring_mapping),
        ("internal_activation", "pulse_counter__9", wiring_mapping),
        ("door_open_time", "analog_inputs__4", wiring_mapping),
        ("panic", "pulse_counter__11", wiring_mapping),
        ("soft_close_time", "analog_inputs__5", wiring_mapping),
    ]

    for m in maps:
        MappingFactory(sensor_key=m[0], input_key=m[1], mapping=m[2])


    # All sensors for Demo door product
    sensor1 = SensorTypeFactory(
        sensor_name="door_open_count",
        unit="",
        product=product
    )
    sensor2 = SensorTypeFactory(
        sensor_name="external_activation",
        unit="",
        product=product
    )
    sensor3 = SensorTypeFactory(
        sensor_name="door_open_time",
        unit="s",
        product=product
    )
    sensor4 = SensorTypeFactory(
        sensor_name="soft_close",
        unit="",
        product=product
    )
    sensor5 = SensorTypeFactory(
        sensor_name="panic",
        unit="",
        product=product
    )
    sensor6 = SensorTypeFactory(
        sensor_name="soft_close_time",
        unit="s",
        product=product
    )
    sensor7 = SensorTypeFactory(
        sensor_name="internal_activation",
        unit="",
        product=product
    )

    # Demo Orgs (1 distributor, 1 company, 2 sites)
    distributor = DistributorFactory(
        name="GEZE",
        id=1,
        # no location
    )
    company = CompanyFactory(
        name="BP",
        distributor=distributor,
        id=2,
        wiring_mapping=wiring_mapping,
        # no location
        # no dashboards
    )
    site1 = SiteFactory(
        name="BP Guys Cliffe",
        company=company,
        r_number="R10668",
        id=3,
        # no location
        # no dashboards
    )
    site2 = SiteFactory(
        name="BP Barnwood",
        company=company,
        r_number="R14977",
        id=4,
        # no location
        # no dashboards
    )

    device1 = DeviceFactory(
        product=product,
        name="Front Door",
        # no fw_version
        online=False,
        sim_number="8944538525004714414",
    )
    device1.orgs.add(site1)

    device1a = DeviceFactory(
        product=product,
        name="Back Door",
        # no fw_version
        online=False,
        sim_number="123456789",
    )
    device1a.orgs.add(site1)

    device2 = DeviceFactory(
        product=product,
        name="Front Door",
        # no fw_version
        online=False,
        sim_number="8944538525004715387",
    )
    device2.orgs.add(site2)

    devices = [device1, device1a, device2]
    sensor_types = [sensor1, sensor2, sensor3, sensor4, sensor5, sensor6, sensor7]
    device_sensor_map = {}
    # Loop over all devices and sensors to create 35 device_sensors
    for device in devices:
        device.orgs.add(distributor)
        device.orgs.add(company)
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
            "description": "Open time was less than 20%",
            "severity": 20,
            "category": "business metric",
            "notify": False
        },
        {
            "verb": "reported",
            "description": "Open time was less than 10%",
            "severity": 30,
            "category": "maintenance",
            "notify": False
        },
        {
            "verb": "reported",
            "description": "Open time was less than 5%",
            "severity": 40,
            "category": "system",
            "notify": True
        }
    ]

    now = datetime.datetime.utcnow()
    # Create a TimeSeriesData entries, attaching it to the appropriate device_sensor
    ts_data_to_save = []
    for device in devices:
        for sensor_type in sensor_types:
            for i in range(100):
                ds_map_key = "{}:{}".format(device.id, sensor_type.sensor_name)
                name = sensor_type.sensor_name
                if name == "door_open_count":
                    value = 5
                elif name == "door_open_time":
                    value = 225 # a quarter of the time
                elif name == "soft_close_time":
                    value = 5 if (i%10 == 0) else 0
                elif name == "soft_close":
                    value = 1 if (i%10 == 0) else 0
                elif name == "external_activation":
                    value = 1 if (i%10 == 0) else 0
                elif name == "internal_activation":
                    value = 1 if (i%10 == 0) else 0
                elif name == "panic":
                    value = 1 if (i%50 == 0 and device == device1) else 0
                else:
                    value = 1
                ts_data_to_save.append(TimeSeriesData(
                    ts=now - timedelta(minutes=15*i),
                    sensor=device_sensor_map[ds_map_key],
                    #value=sin(i),
                    value=value
                ))
        # Populate an activity stream for each device
        for activity in activities:
            action_model.send(device, target=device, **activity)

    TimeSeriesData.objects.bulk_create(ts_data_to_save)

     # joe seed
    joe = UserFactory()
    # joe.orgs.add(site1)
    joe.add_org(site1)

    company_user = UserFactory(
        username="company@zoetrope.io",
        email="company@zoetrope.io",
    )
    # company_user.orgs.add(company)
    company_user.add_org(company)

    distributor_user = UserFactory(
        username="distributor@zoetrope.io",
        email="distributor@zoetrope.io",
    )
    # distributor_user.orgs.add(distributor)
    distributor_user.add_org(distributor)

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
