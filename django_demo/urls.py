"""django_demo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
"""
# Django imports
from django.conf.urls import include, url
from django.contrib import admin
from rest_framework_extensions.routers import ExtendedSimpleRouter

from zconnect.views import CeleryMQTTTestViewSet, StackSamplerView

from .views import (
    CompanyViewSet, DistributorViewSet, DemoDeviceViewSet, SiteViewSet, TSRawDataViewSet,
    WiringMappingViewSet)

##############################
# For this app
##############################





router = ExtendedSimpleRouter()
router.register(r'distributors', DistributorViewSet, base_name="distributors")
router.register(r'companies', CompanyViewSet, base_name="companies")
router.register(r'sites', SiteViewSet, base_name="sites")
router.register(r'wiring_mappings', WiringMappingViewSet, base_name="wiringmappings")

device_router = router.register(r'devices', DemoDeviceViewSet, base_name="devices")
device_router.register(
    r'ts_raw_data',
    TSRawDataViewSet,
    parents_query_lookups=['device'],
    base_name="ts_raw_data"
)

# TODO
# http data endpoint
# Might have to be a basic function-type view because it doesn't correspond
# directly to the Device model


##############################
# All
##############################

urlpatterns = [
    # enable the admin interface
    url(r'^admin/', admin.site.urls),

    url(r'^stats/stacksampler', StackSamplerView.as_view()),

    # Rest Auth requires auth urls. If we remove this, then we'll get an error
    # around NoReverseMatch
    # TODO: Work out how to avoid external access to these URLs if possible
    url(r'^', include('django.contrib.auth.urls')),

    url(r'^api/v3/', include(router.urls)),

    url(r'^api/v3/', include('zconnect.urls')),
    url(r'^api/v3/', include('zconnect.zc_billing.urls')),

    url(r'^celerymqtttest/', CeleryMQTTTestViewSet.as_view({'post': 'create'})),
    # For django-db-file-storage:
    url(r'^files/', include('db_file_storage.urls')),
]
