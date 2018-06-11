import json

from dateutil import parser as date_parser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand

from zconnect.testutils.factories import (
    DeviceEventDefinitionFactory, DeviceFactory, DeviceSensorFactory, EventDefinitionFactory,
    ProductPreprocessorsFactory, ProductTagsFactory, SensorTypeFactory, UserFactory)
from zconnect.zc_timeseries.models import TimeSeriesData

from django_demo.testutils.factories import (
    CompanyFactory, DistributorFactory, Eco3Factory, MappingFactory, SiteFactory,
    WiringMappingFactory)


class Command(BaseCommand):
    help = "Import Demo devices, products and TS data from zconnect v1"
    def add_arguments(self, parser):
        parser.add_argument("--kwak", nargs="?", const=True)

    def get_ts_data(self, kwak):
        """ Function gets all timeseries data via mongo command and transforms into json object. Can be
        executed from host or kwak if connected to the network """
        MONGO_COMMAND = 'mongo "mongodb+srv://zconnect-jbbvh.mongodb.net/test" --quiet\
                 --username admin --password k7ko6g9dfROkHjNu\
                 --eval "\
                   db = db.getSiblingDB(\'demo-trial\');\
                   records = [];\
                   var cursor = db.getCollection(\'time_series_data\').find({}, {});\
                   while(cursor.hasNext()) { records.push(cursor.next())};\
                   print(tojson(records));"'
        if kwak:
            import paramiko
            self.stdout.write("Getting v1 time series data via kwak...")
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect("kwak.local", username="build")
            _, stdout, _ = ssh.exec_command(MONGO_COMMAND)
            output = stdout.read()
        else:
            import subprocess
            self.stdout.write("Getting v1 time series data...")
            output = subprocess.check_output(['bash','-c', MONGO_COMMAND])
        # Remove mongo logging output, there is probably a better way to do this
        json_string = output.decode("utf-8").split("with a 5 second timeout)\n")[-1]
        # Remove object names
        json_string = json_string.replace("ISODate(", "").replace("ObjectId(", "")
        # Remove new lines and tabs
        json_string = json_string.replace(")", "").replace("\n", "").replace("\t", "")
        parsed_json = json.loads(json_string)
        return parsed_json

    def handle(self, *args, **options):
        # Create Demo Product, ProductPreprocessors and ProductTags
        # See https://sqldbm.com/Project/MySQL/Share/qvOpUcDfTnwexCqKFXLgBg for schema
        self.stdout.write("Adding product, sensors, orgs, devices, and device sensors...")
        product = Eco3Factory()
        ProductPreprocessorsFactory(
            preprocessor_name="demo_mapping",
            product=product,
        )
        ProductTagsFactory(
            tag="sliding-door",
            product=product,
        )
        # Product event definitions
        EventDefinitionFactory(
            enabled=True,
            ref="emergency_close:email:site",
            condition="panic>0&&email_site_emergency_close==True",
            actions={"email": {"alert_text": "An emergency close has occured on the door."}},
            product=product,
        )
        EventDefinitionFactory(
            enabled=True,
            ref="emergency_close:email:company",
            condition="panic>0&&email_company_emergency_close==True",
            actions={"email": {"alert_text": "An emergency close has occured on the door."}},
            product=product,
        )
        EventDefinitionFactory(
            enabled=True,
            ref="emergency_close:email:distributor",
            condition="panic>0&&email_distributor_emergency_close==True",
            actions={"email": {"alert_text": "An emergency close has occured on the door."}},
            product=product,
        )

        # All sensors for Demo door product
        sensor1 = SensorTypeFactory(
            sensor_name="door_open_count",
            descriptive_name="Door Open Count",
            unit="",
            product=product
        )
        sensor2 = SensorTypeFactory(
            sensor_name="external_activation",
            descriptive_name="External Activation",
            unit="",
            product=product
        )
        sensor3 = SensorTypeFactory(
            sensor_name="door_open_time",
            descriptive_name="Door Open Time",
            unit="s",
            product=product
        )
        sensor4 = SensorTypeFactory(
            sensor_name="soft_close",
            descriptive_name="Soft Close",
            unit="",
            product=product
        )
        sensor5 = SensorTypeFactory(
            sensor_name="panic",
            descriptive_name="Panic",
            unit="",
            product=product
        )
        sensor6 = SensorTypeFactory(
            sensor_name="soft_close_time",
            descriptive_name="Soft Close Time",
            unit="s",
            product=product
        )
        sensor7 = SensorTypeFactory(
            sensor_name="internal_activation",
            descriptive_name="Internal Activation",
            unit="",
            product=product
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
            new_map = MappingFactory(sensor_key=m[0], input_key=m[1], mapping=m[2])
            self.stdout.write("Adding new_map: {}".format(new_map))

        # Demo orgs (1 distributor, 1 company, 5 sites)
        distributor = DistributorFactory(
            name="GEZE",
            # no location
        )
        company = CompanyFactory(
            name="BP",
            distributor=distributor,
            wiring_mapping=wiring_mapping,
            # no location
            # no dashboards
        )
        site1 = SiteFactory(
            name="BP Guys Cliffe",
            company=company,
            r_number="R10668",
            # no location
            # no dashboards
        )
        site2 = SiteFactory(
            name="BP Barnwood",
            company=company,
            r_number="R14977",
            # no location
            # no dashboards
        )
        site3 = SiteFactory(
            name="BP Hutton Mount",
            company=company,
            r_number="R15213",
            # no location
            # no dashboards
        )
        site4 = SiteFactory(
            name="BP Lower Wick",
            company=company,
            r_number="R14881",
            # no location
            # no dashboards
        )
        site5 = SiteFactory(
            name="BP Pevensey",
            company=company,
            r_number="R15184",
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
        device1.set_site(site1)

        device2 = DeviceFactory(
            product=product,
            name="Front Door",
            # no fw_version
            online=False,
            sim_number="8944538525004715387",
        )
        device2.set_site(site2)

        device3 = DeviceFactory(
            product=product,
            name="Front Door",
            # no fw_version
            online=False,
            sim_number="8944538525004715403",
        )
        device3.set_site(site3)

        device4 = DeviceFactory(
            product=product,
            name="Front Door",
            # no fw_version
            online=False,
            sim_number="8944538525004714422",
        )
        device4.set_site(site4)

        device5 = DeviceFactory(
            product=product,
            name="Front Door",
            # no fw_version
            online=False,
            sim_number="8944538525004714406",
        )
        device5.set_site(site5)

        gateway_user = UserFactory
        gateway_user = UserFactory(
            email="gateway@zoetrope.io",
            username="gateway@zoetrope.io",
            password=make_password("5Trp6P564z"),
            is_superuser=False,
            is_staff=False,
        )
        perm = Permission.objects.get(codename='can_create_timeseries_http')
        gateway_user.user_permissions.add(perm)
        gateway_user.save()

        # map the old mongo DB ids to the new django IDs
        old_id_map = {
            "5a9d41d697c64ab95a135ed2": device1.id,
            "5aa68dbb97c64ab95a6f9991": device2.id,
            "5aa68f6297c64ab95a728e4b": device3.id,
            "5aa68fc797c64ab95a7340e4": device4.id,
            "5aa6901597c64ab95a73d0cb": device5.id,
        }

        devices = [device1, device2, device3, device4, device5]
        sensor_types = [sensor1, sensor2, sensor3, sensor4, sensor5, sensor6, sensor7]
        device_sensor_map = {}
        # Loop over all devices and sensors to create 35 device_sensors
        for device in devices:
            device.orgs.add(distributor)
            device.orgs.add(company)
            device.save()
            # Create device event defintion
            DeviceEventDefinitionFactory(
                enabled=True,
                ref="high_door_open_time_last_8hr:site",
                condition="sum_28800_door_open_time>25920",
                actions={"email": {"alert_text": "The device on the door has low battery."}},
                device=device,
            )
            for sensor_type in sensor_types:
                device_sensor = DeviceSensorFactory(
                    device=device,
                    resolution=900,
                    sensor_type=sensor_type,
                )
                # This key should include the resolution for cases where resolution is not constant
                # across all data, but for this case is it
                device_sensor_map["{}:{}".format(device.id, sensor_type.sensor_name)] = device_sensor

        # Have encountered problems where mongo command cannot connect to trial DB from certain
        # machines, if this is the case can ssh into kwak and send mongo command from there
        ts_data_array = self.get_ts_data(options["kwak"])

        self.stdout.write("Creating time series data objects...")

        # Create a TimeSeriesData entries, attaching it to the appropriate device_sensor
        i = 0
        ts_data_to_save = []
        for ts_data in ts_data_array:
            device = ts_data["device"]
            if device in old_id_map:
                for device_sensor_data in ts_data["data"]:
                    sensor_type = device_sensor_data["sensor_type"]
                    ds_map_key = "{}:{}".format(old_id_map[device], sensor_type)
                    sensor = device_sensor_map[ds_map_key]
                    for datum in device_sensor_data["series"]:
                        ts_data_to_save.append(TimeSeriesData(
                            ts=date_parser.parse(datum["ts"]), #.replace(tzinfo=None),
                            sensor=sensor,
                            value=datum["value"],
                        ))
                        i+=1
                        if i % 10000 == 0:
                            self.stdout.write("  - created {} entries so far".format(i))

        self.stdout.write("Inserting time series data...")

        def chunk_devices(queryset, chunksize):
            """Chunk up the queryset into chunksize chunks"""

            for i in range(0, len(queryset), chunksize):
                yield queryset[i:i+chunksize]

        for cn, c in enumerate(chunk_devices(ts_data_to_save, 10000)):
            TimeSeriesData.objects.bulk_create(c)
            self.stdout.write("  - saved {} entries so far".format((1+cn)*10000))

        self.stdout.write(self.style.SUCCESS("Successfully imported v1 data")) # pylint: disable=no-member
