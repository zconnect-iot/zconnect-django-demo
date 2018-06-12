import logging

from django.apps import apps
from django.conf import settings
from rest_framework import serializers

from zconnect.serializers import CreateDeviceSerializer, DeviceSerializer
from zconnect.models import Product

from .models import DemoDevice

logger = logging.getLogger(__name__)


class DemoDeviceSerializer(DeviceSerializer):
    class Meta:
        model = apps.get_model(settings.ZCONNECT_DEVICE_MODEL)
        fields = ("id", "product", "name", "online", "last_seen", "fw_version",
                  "sensors_current", "orgs", "online", "sim_number", "created_at", "updated_at",
                  'online', 'sim_number',)
        read_only_fields = ("id", "product", "orgs", "created_at", "updated_at",
                            'online', 'sim_number')

class CreateDemoDeviceSerializer(CreateDeviceSerializer):
    class Meta:
        model = DemoDevice
        fields = ("id", "product", "name", "online", "last_seen", "fw_version",
                  "orgs", "online", "sim_number", "created_at", "updated_at",
                  'online', 'sim_number',)
        read_only_fields = ("id", "created_at", "updated_at")

class DemoProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("id", "version", "name", "iot_name", "sku", "manufacturer",
            "url", "support_url", "previous_version", "periodic_data",
            "periodic_data_interval_short", "periodic_data_num_intervals_short",
            "periodic_data_interval_long", "periodic_data_num_intervals_long",
            "periodic_data_retention_short", "server_side_events",
            "battery_voltage_full", "battery_voltage_critical",
            "battery_voltage_low", "created_at", "updated_at",)
        read_only_fields = ("id", "created_at", "updated_at",)
