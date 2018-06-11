import logging

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from zconnect.serializers import (
    BilledOrganizationSerializer, CreateDeviceSerializer, DeviceSerializer, JWTUserSerializer,
    LocationSerializer, StubDeviceSerializer, StubSerializerMixin, UserSerializer,
    UserSerializerAdmin)

from .models import (
    CompanyGroup, DistributorGroup, Mapping, DemoDevice, DemoProduct, SiteGroup, TSRawData,
    WiringMapping)

logger = logging.getLogger(__name__)


# Only return a stub
# TODO
# move read_only_fields to a setting or something?
class StubDistributorSerializer(StubSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = DistributorGroup
        fields = ("name", "id",)
        read_only_fields = ("name", "id",)


class StubCompanySerializer(StubSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = CompanyGroup
        fields = ("name", "id",)
        read_only_fields = ("name", "id",)


class StubSiteSerializer(StubSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = SiteGroup
        fields = ("name", "id", "r_number")
        read_only_fields = ("name", "id",)

demo_org_type_map = {
    "site": (SiteGroup, StubSiteSerializer),
    "company": (CompanyGroup, StubCompanySerializer),
    "distributor": (DistributorGroup, StubDistributorSerializer),
}

class DemoDeviceSerializer(DeviceSerializer):
    site = StubSiteSerializer(read_only=True)

    class Meta:
        model = apps.get_model(settings.ZCONNECT_DEVICE_MODEL)
        fields = ("id", "product", "name", "online", "last_seen", "fw_version",
                  "sensors_current", "orgs", "online", "sim_number", "created_at", "updated_at",
                  'site', 'online', 'sim_number', 'email_site_emergency_close',
                  'email_company_emergency_close', 'email_distributor_emergency_close')
        read_only_fields = ("id", "product", "orgs", "created_at", "updated_at", 'site',
                            'online', 'sim_number')

class CreateDemoDeviceSerializer(CreateDeviceSerializer):
    site = StubSiteSerializer(read_only=True)

    class Meta:
        model = DemoDevice
        fields = ("id", "product", "name", "online", "last_seen", "fw_version",
                  "orgs", "online", "sim_number", "created_at", "updated_at",
                  'online', 'sim_number', "site", 'email_site_emergency_close',
                  'email_company_emergency_close', 'email_distributor_emergency_close')
        read_only_fields = ("id", "created_at", "updated_at", "site")

class DemoProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemoProduct
        fields = ("id", "version", "name", "iot_name", "sku", "manufacturer",
            "url", "support_url", "previous_version", "periodic_data",
            "periodic_data_interval_short", "periodic_data_num_intervals_short",
            "periodic_data_interval_long", "periodic_data_num_intervals_long",
            "periodic_data_retention_short", "server_side_events",
            "battery_voltage_full", "battery_voltage_critical",
            "battery_voltage_low", "created_at", "updated_at",
            "wiring_mapping",)
        read_only_fields = ("id", "created_at", "updated_at",)

class MappingSerializer(serializers.ModelSerializer):
    """ Serialize a Mapping object
    """

    class Meta:
        model = Mapping
        fields = ("input_key","transform_function","sensor_key", "id", "created_at", "updated_at",)
        read_only_fields = ("id", "created_at", "updated_at",)


class WiringMappingSerializer(WritableNestedModelSerializer):
    # Normally, nested serializers are not writeable, inheriting
    # from WritableNestedModelSerializer fills out the boilerplate
    mappings = MappingSerializer(many=True)
    class Meta:
        model = WiringMapping
        fields = ("name","id", "mappings", "created_at", "updated_at",)
        read_only_fields = ("name", "id", "created_at", "updated_at",)


# Normal serializers
# return everything
class DistributorSerializer(WritableNestedModelSerializer,
                            BilledOrganizationSerializer):
    companies = StubCompanySerializer(many=True)
    dashboards = serializers.SerializerMethodField('list_of_dashboards')
    location = LocationSerializer()

    def list_of_dashboards(self, obj):
        return ["default"]

    class Meta:
        model = DistributorGroup
        fields = ("name", "id", "location", "companies", "dashboards", "logo")
        read_only_fields = ("id", "dashboards", "companies",)

def add_default_dashboard(context, dashboards):
    """
    Get a list of dashboards depending on the user type.
    """
    request = context.get("request")
    user = getattr(request, "user", None)

    if user and (user.is_staff or user.is_superuser):
        dashboards.append("default")

    return dashboards

class CompanySerializer(WritableNestedModelSerializer,
                        BilledOrganizationSerializer):
    distributor = StubDistributorSerializer()
    sites = StubSiteSerializer(many=True)
    dashboards = serializers.SerializerMethodField('list_of_dashboards')
    location = LocationSerializer()

    def list_of_dashboards(self, obj):
        # For admins, return the default dashboard as well
        dashboards = ["loneworker_company_dashboard"]

        dashboards = add_default_dashboard(self.context, dashboards)

        return dashboards

    class Meta:
        model = CompanyGroup
        fields = ("name", "id", "location", "distributor", "sites",
                  "dashboards", "logo")
        read_only_fields = ("id", "dashboards", "sites",)


class SiteSerializer(WritableNestedModelSerializer,
                     BilledOrganizationSerializer):
    company = StubCompanySerializer()
    devices = StubDeviceSerializer(read_only=True, many=True)
    dashboards = serializers.SerializerMethodField('list_of_dashboards')
    location = LocationSerializer()

    def list_of_dashboards(self, obj):

        dashboards = ["loneworker_site_dashboard"]

        dashboards = add_default_dashboard(self.context, dashboards)

        return dashboards

    class Meta:
        model = SiteGroup
        fields = ("name", "id", "location", "company", "r_number", "dashboards",
                  "devices", "logo")
        read_only_fields = ("id", "dashboards", "devices")


class DemoJWTUserSerializer(JWTUserSerializer):
    """Same as JWTUserSerializer, but add demo org information
    """

    company_slugs = serializers.SerializerMethodField()

    org_type_map = demo_org_type_map

    class Meta:
        model = apps.get_model(settings.AUTH_USER_MODEL)
        fields = ("email", "orgs", "is_superuser", "is_staff", "iat",
                  "company_slugs")
        read_only_fields = fields

    def get_company_slugs(self, obj):
        """ Go through every organization and find the associated company """
        slugs = []
        for org in obj.orgs.all():
            try:
                slugs.append(CompanyGroup.objects.get(pk=org.id).slug)
            except ObjectDoesNotExist:
                try:
                    slugs.append(SiteGroup.objects.get(pk=org.id).company.slug)
                except ObjectDoesNotExist:
                    pass
        return list(set(slugs))


class TSRawDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TSRawData
        fields = ("timestamp", "raw_data", "device")
        read_only_fields = ("id",)

class DemoOrgSerializerMixin:
    org_type_map = demo_org_type_map

class DemoAdminUserSerializer(DemoOrgSerializerMixin, UserSerializerAdmin):
    pass

class DemoUserSerializer(DemoOrgSerializerMixin, UserSerializer):
    pass
