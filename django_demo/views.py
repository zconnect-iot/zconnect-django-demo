from datetime import date, datetime, time

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from zconnect.permissions import IsAdminOrReadOnly, IsAdminOrTimeseriesIngress
from zconnect.views import AbstractStubbableModelViewSet, DeviceViewSet
from zconnect.filters import OrganizationObjectPermissionsFilter

from .models import CompanyGroup, DistributorGroup, SiteGroup, TSRawData, WiringMapping
from .serializers import (
    CompanySerializer, CreateDemoDeviceSerializer, DistributorSerializer, DemoDeviceSerializer,
    SiteSerializer, StubCompanySerializer, StubDistributorSerializer, StubSiteSerializer,
    TSRawDataSerializer, WiringMappingSerializer)
from .util.dashboards import construct_dashboard_response


class DemoDeviceViewSet(DeviceViewSet):
    normal_serializer = DemoDeviceSerializer
    create_serializer = CreateDemoDeviceSerializer

    def update(self, request, *args, **kwargs):
        if "site" in request.data:
            device = self.get_object()
            if request.data["site"] is None:
                del device.site
            else:
                try:
                    site_id = request.data["site"]["id"]
                except KeyError:
                    raise DRFValidationError({
                        "code": "no_site_id",
                        "detail": "When updating a site `id` must be provided"
                    })
                # Set new site if site has changed
                if device.site is None or device.site.id != site_id:
                    try:
                        site = SiteGroup.objects.get(id=site_id)
                    except SiteGroup.DoesNotExist:
                        raise DRFValidationError({
                            "code": "site_not_found",
                            "detail": "Site with id `{}` cannot be found".format(site_id)
                        })
                    device.site = site

        return super(DemoDeviceViewSet, self).update(request, *args, **kwargs)


class GroupStubViewSet(AbstractStubbableModelViewSet):
    """Similar functionality to GenericStubEndpoint in bigbird

    Restriction of the number of fields is done in the serializers
    """
    filter_backends = [DjangoFilterBackend]
    filter_fields = ["name"]
    ordering_fields = ["location"]
    ordering = ["location"]

    filter_backends = [
        OrganizationObjectPermissionsFilter,
    ]

    # Do not allow put due to use of `partial_update` so child orgs are not updated
    http_method_names = ["get", "post", "head", "patch", "delete"]

    @detail_route(methods=['get'])
    def dashboards(self, request, pk=None):
        """ Aggregate dashboard data for sites, companies and distributors """

        errors = {}

        dashboard_name = request.GET.get('dashboard_name')
        if not dashboard_name:
            errors["dashboard_name"] = "Dashboard name is required"

        start_ts = None
        end_ts = None
        live = request.GET.get('live')
        if live and live.lower() == 'true':
            start_ts = datetime.combine(date.today(), time())
        else:
            if request.GET.get('start') is not None:
                try:
                    start = int(request.GET.get('start'))
                    start_ts = datetime.fromtimestamp(start/1000)
                except (TypeError, ValueError):
                    errors["start"] = "Start must be a unix timestamp"

            if request.GET.get('end') is not None:
                try:
                    end = int(request.GET.get('end'))
                    end_ts = datetime.fromtimestamp(end/1000)
                except (TypeError, ValueError):
                    errors["end"] = "End must be a unix timestamp"

        if errors:
            raise DRFValidationError(errors)

        org = get_object_or_404(self.queryset, pk=pk)
        res = construct_dashboard_response(org, start_ts, end_ts, dashboard_name)
        return Response(res)


def check_location_id(data):
    """ Raise error if request attempts to update the location without providing
    the id """
    if "location" in data and "id" not in data["location"]:
        raise DRFValidationError({
            "code": "stub_viewset",
            "detail": "You need to provide an id to update a nested field"
            })


class DistributorViewSet(GroupStubViewSet):
    queryset = DistributorGroup.objects.all()
    # model = DistributorGroup

    # serializer_class = DistributorSerializer
    normal_serializer = DistributorSerializer
    stub_serializer = StubDistributorSerializer

    permission_classes = [IsAdminOrReadOnly,]

    def update(self, request, *args, **kwargs):
        """ Custom update function to ensure the child companies of the
        distributor cannot be changed and location has an id field present """
        data = request.data
        check_location_id(data)
        if "companies" in data:
            data.pop("companies")
            return super().partial_update(request, *args, **kwargs)
        return super().update(request, *args, **kwargs)


class CompanyViewSet(GroupStubViewSet):
    queryset = CompanyGroup.objects.all()
    # model = CompanyGroup

    # serializer_class = CompanySerializer
    normal_serializer = CompanySerializer
    stub_serializer = StubCompanySerializer

    permission_classes = [IsAdminOrReadOnly,]

    def update(self, request, *args, **kwargs):
        """ Custom update function to ensure the child sites of the
        company cannot be changed and location has an id field present """
        data = request.data
        check_location_id(data)
        if "sites" in data:
            data.pop("sites")
            return super().partial_update(request, *args, **kwargs)
        return super().update(request, *args, **kwargs)


class SiteViewSet(GroupStubViewSet):
    queryset = SiteGroup.objects.all()
    # model = SiteGroup

    # serializer_class = SiteSerializer
    normal_serializer = SiteSerializer
    stub_serializer = StubSiteSerializer

    permission_classes = [IsAdminOrReadOnly,]

    def update(self, request, *args, **kwargs):
        """ Custom update function to ensure location has an id field
        present """
        check_location_id(request.data)
        return super().update(request, *args, **kwargs)


class WiringMappingViewSet(viewsets.ModelViewSet):
    """ Viewset for wiring mappings
    """
    filter_backends = [DjangoFilterBackend]
    filter_fields = ["name"]
    ordering_fields = ["name"]
    ordering = ["name"]

    queryset = WiringMapping.objects.all()

    serializer_class = WiringMappingSerializer
    permission_classes = [IsAdminUser,]


class TSRawDataViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    """ Viewset to allow writing to the raw data table
    """
    # Currently this is write-only. We don't want anyone to be able to hammer the
    # API by fetching this data.
    http_method_names = ['post']
    queryset = TSRawData.objects.all()
    serializer_class = TSRawDataSerializer
    permission_classes = [IsAdminOrTimeseriesIngress,]
