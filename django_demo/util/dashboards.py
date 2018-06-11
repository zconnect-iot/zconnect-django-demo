from django.apps import apps
from django.conf import settings
from django.db.models import F, Max, Min, Sum
from rest_framework.exceptions import ValidationError as DRFValidationError

from zconnect.zc_timeseries.models import TimeSeriesData

from django_demo.models import CompanyGroup, SiteGroup

Device = apps.get_model(settings.ZCONNECT_DEVICE_MODEL)
User = apps.get_model(settings.AUTH_USER_MODEL)

def row_data(row):
    ts_diff = round((row["last_ts"] - row["first_ts"]).total_seconds())
    total_time = ts_diff + row["resolution"]
    return {
        "sum": row['total'],
        "total_time": total_time,
        # Django 2 line, see below
        # "count_nonzero": row["count_nonzero"]
    }


def timeseries_totals_by_device(ts_data):
    aggregated = (
        ts_data
        .values(
            sensor_name=F('sensor__sensor_type__sensor_name'),
            resolution=F('sensor__resolution'),
            device=F('sensor__device')
        )
        .annotate(
            total=Sum('value'),
            first_ts=Min('ts'),
            last_ts=Max('ts'),
        )
    )
    readings = {}
    for row in aggregated:
        data = row_data(row)
        try:
            readings[row['device']][row['sensor_name']] = data
        except KeyError:
            readings[row['device']] = {row['sensor_name']: data}
    return readings


def timeseries_totals(ts_data):
    aggregated = (
        ts_data
        .values(
            sensor_name=F('sensor__sensor_type__sensor_name'),
            resolution=F('sensor__resolution'),
        )
        .annotate(
            total=Sum('value'),
            first_ts=Min('ts'),
            last_ts=Max('ts'),
            # When we upgrade to Django 2 we can use:
            # count_nonzero=Count(
            #     'sensor__device',
            #     filter=Q(participants__is_paid=True),
            #     distinct=True
            # )
        )
    )
    readings = {}
    for row in aggregated:
        readings[row['sensor_name']] = row_data(row)
    return readings

def d_sum(device_obj, key):
    """ Shortcut: extract a sum from the device aggregation """
    try:
        return device_obj[key]["sum"]
    except (KeyError, TypeError):
        return 0.0

def d_percent(device_obj, key, inverse=False):
    """ Shortcut: extract a time percentage from the device aggregation """
    try:
        obj = device_obj[key]
        ret = (obj["sum"] / obj["total_time"]) * 100
        if inverse:
            return 100 - ret
        return ret
    except (KeyError, TypeError):
        return 0.0

def d_time(device_obj, key):
    """ Shortcut: extract the collection period for a key for a device """
    try:
        return device_obj[key]["total_time"]
    except (KeyError, TypeError):
        return 0.0

def t_sum(data, key):
    """ Shortcut: extract a sum across all devices """
    try:
        return data[key]["sum"]
    except (KeyError, TypeError):
        return 0.0

def t_percent(data, key, num_devices, inverse=False):
    """ Shortcut: extract a time percentage from the device aggregation """
    try:
        obj = data[key]
        ret = (obj["sum"] / (obj["total_time"]*num_devices)) * 100
        if inverse:
            return 100 - ret
        return ret
    except (KeyError, TypeError):
        return 0.0

def t_other(data, key, aggregate_key):
    try:
        return data[key][aggregate_key]
    except (KeyError, TypeError):
        return 0 if aggregate_key == 'count_nonzero' else 0.0

def organization_stats(org, start, end):
    time_series_data = (
        TimeSeriesData.objects
        # Remove ordering to remove Django's secret fields which can result in
        # otherwise identical rows appearing to be distinct
        .order_by()
        .filter(sensor__device__orgs=org)
    )
    if start:
        time_series_data = time_series_data.filter(ts__gte=start)
    if end:
        time_series_data = time_series_data.filter(ts__lte=end)
    totals = timeseries_totals(time_series_data)
    totals_by_device = timeseries_totals_by_device(time_series_data)
    devices = Device.objects.filter(orgs=org)
    return {
        "total": len(devices),
        "panic_count": t_sum(totals, "panic"), # t_other(totals, "panic", "count_nonzero"),
        "total_operations": t_sum(totals, "door_open_count"),
        "soft_close_count": t_sum(totals, "soft_close"), #t_other(totals, "soft_close", "count_nonzero"),
        "active": len(totals_by_device.keys()),
        "closed_time_percentage": t_percent(totals, "door_open_time", len(devices), inverse=True),
        "closed_time": (len(devices) * t_other(totals, "door_open_time", "total_time")) - t_sum(totals, "door_open_time"),
        "total_time": t_other(totals, "door_open_time", "total_time")
    }

def device_stats(device, totals_by_device):
    try:
        device_obj = totals_by_device[device.id]
    except KeyError:
        device_obj = None
    return {
        "active": device.id in totals_by_device,
        "r_number": device.site.r_number,
        "soft_close_count": d_sum(device_obj, "soft_close"),
        "soft_close_time": d_sum(device_obj, "soft_close_time"),
        "panic_count": d_sum(device_obj, "panic"),
        "total_operations": d_sum(device_obj, "door_open_count"),
        "closed_time_percentage": d_percent(device_obj, "door_open_time", inverse=True),
        "closed_time": d_time(device_obj, "door_open_time") - d_sum(device_obj, "door_open_time"),
        "device": {
            "id": device.id,
            "name": device.name,
            "product": {
                "name": device.product.name,
                "id": device.product.id,
            }
        },
        "site": {
            "id": device.site.id,
            "name": device.site.name
        }
    }

def construct_dashboard_response(org, start, end, dashboard_name):
    time_series_data = (
        TimeSeriesData.objects
        # Remove ordering to remove Django's secret fields which can result in
        # otherwise identical rows appearing to be distinct
        .order_by()
        .filter(sensor__device__orgs=org)
    )
    if start:
        time_series_data = time_series_data.filter(ts__gte=start)
    if end:
        time_series_data = time_series_data.filter(ts__lte=end)
    totals_by_device = timeseries_totals_by_device(time_series_data)
    devices = Device.objects.filter(orgs=org)

    device_list = [device_stats(d, totals_by_device) for d in devices]

    if dashboard_name == "loneworker_company_dashboard":
        if not isinstance(org, CompanyGroup):
            msg = "The requested dashboard is only available for companies"
            raise DRFValidationError({"dashboard_name": msg})
        return {
            "devices": device_list,
            "company_stats": organization_stats(org, start, end)
        }
    elif dashboard_name == "loneworker_site_dashboard":
        if not isinstance(org, SiteGroup):
            msg = "The requested dashboard is only available for sites"
            raise DRFValidationError({"dashboard_name": msg})
        return {
            "devices": device_list,
            "site_stats": organization_stats(org, start, end),
            "company_stats": organization_stats(org.company, start, end)
        }

    raise DRFValidationError({"dashboard_name": "Dashboard name does not match known dashboards"})
