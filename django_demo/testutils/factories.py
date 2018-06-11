# import datetime
import datetime

import factory
import factory.fuzzy

from zconnect.testutils.factories import LocationFactory, ModelBaseFactory, ProductFactory

from django_demo.models import (
    CompanyGroup, DistributorGroup, Mapping, SiteGroup, TSRawData, WiringMapping)


class MappingFactory(ModelBaseFactory):
    class Meta:
        model = Mapping

    input_key = 'digital_input_17'
    sensor_key = 'door_open_time'
    # Pass `mappings=None` to avoid infinite loop of references
    mapping = factory.SubFactory('django_demo.testutils.factories.WiringMappingFactory', mappings=None)

class WiringMappingFactory(ModelBaseFactory):
    class Meta:
        model = WiringMapping

    name = "Good wiring mapping"
    # Mappings have a reverse dependancy to WiringMapping.
    # RelatedFactory allows us to create these automagically.
    mappings = factory.RelatedFactory(MappingFactory, 'mapping')


# class BillGeneratorFactory(ModelBaseFactory):
#     class Meta:
#         model = BillGenerator
#
#     rate_per_device = "1.50"
#     currency = "GBP"
#     period = "weekly"
#     active_from_date = factory.LazyFunction(datetime.datetime.utcnow)


class DistributorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DistributorGroup
        # pk on name
        django_get_or_create = ["name"]

    name = "Cool distributor"
    location = factory.SubFactory(LocationFactory)


class CompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CompanyGroup
        # pk on name
        django_get_or_create = ["name"]

    name = "Ok company"
    location = factory.SubFactory(LocationFactory)
    distributor = factory.SubFactory(DistributorFactory)


class SiteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SiteGroup
        # pk on name
        django_get_or_create = ["name"]

    name = "Bad site"
    location = factory.SubFactory(LocationFactory)
    company = factory.SubFactory(CompanyFactory)

    r_number = "Site 123-xtz"

class TSRawDataFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TSRawData

    raw_data = 'SomeRawData ina compressed format with lots of potentially weird chars;,."'
    timestamp = factory.LazyFunction(datetime.datetime.utcnow)


class Eco3Factory(ProductFactory):
    name="ECO3"
    iot_name="eco3"
    sku="ECO5500"
    manufacturer="Demo"
    url="http://www.google.co.uk"
    support_url="http://www.google.co.uk"
    version="0.0.1"
    # no previous_version
    periodic_data=True
    periodic_data_interval_short=900
    periodic_data_num_intervals_short=24
    periodic_data_interval_long=21600
    periodic_data_num_intervals_long=112
    periodic_data_retention_short=2592000
    server_side_events=True
    battery_voltage_full=3.0
    battery_voltage_critical=2.5
    battery_voltage_low=2.7
