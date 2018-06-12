from zconnect.views import DeviceViewSet

from .serializers import CreateDemoDeviceSerializer, DemoDeviceSerializer


class DemoDeviceViewSet(DeviceViewSet):
    normal_serializer = DemoDeviceSerializer
    create_serializer = CreateDemoDeviceSerializer
