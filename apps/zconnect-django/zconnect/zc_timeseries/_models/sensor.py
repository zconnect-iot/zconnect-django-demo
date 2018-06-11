import logging
from math import fmod

import django
from django.conf import settings
from django.db import models

from zconnect.models import ModelBase
from zconnect.zc_timeseries.util.tsaggregations import aggregation_implementations

logger = logging.getLogger(__name__)


class SensorType(ModelBase):
    """A type of sensor

    Attributes:
        graph_type (str): What kind of graph this should be shown as in the app
            (bar or graph)
        sensor_name (str): name of sensor
        unit (str): Unit of measurement (eg, "Watts")
        product (Product): which product this sensor is associated with
    """

    GRAPH_CHOICES = [
        ("ts_bar", "Bar graph"),
        ("ts_graph", "Line graph"),
    ]

    AGGREGATION_CHOICES = [
        ("sum", "Sum values over the aggregation period"),
        ("mean", "Mean of values over the aggregation period"),
        ("median", "Median of values over the aggregation period"),
        ("min", "Minimum value over the aggregation period"),
        ("max", "Maximum value over the aggregation period"),
    ]

    # The canonical name for this sensor
    sensor_name = models.CharField(max_length=50, blank=True)

    # A human readable sensor name, could be displayed under graphs etc.
    descriptive_name = models.CharField(max_length=50, blank=True)
    unit = models.CharField(max_length=30)
    graph_type = models.CharField(max_length=20, choices=GRAPH_CHOICES, default="ts_graph")
    aggregation_type = models.CharField(max_length=20, choices=AGGREGATION_CHOICES, default="sum")
    # products can't be deleted until all devices are deleted as well. Once we
    # can delete it, all sensor types are a bit pointless to keep, so delete
    # them instead.
    product = models.ForeignKey("zconnect.Product", models.CASCADE, related_name="sensors", blank=False)


class DeviceSensor(ModelBase):
    """A sensor associated with a device

    Attributes:
        resolution (float): how often this is sampled, in seconds
        device (Device): associated device
        sensor_type (SensorType): type of sensor
    """

    resolution = models.FloatField(default=120.0)
    # If device goes, just delete this. device should never be deleted really
    # though
    device = models.ForeignKey(settings.ZCONNECT_DEVICE_MODEL, models.CASCADE, related_name="sensors", blank=False)
    # Can't leave the sensor type null
    sensor_type = models.ForeignKey(SensorType, models.PROTECT, blank=False)

    class Meta:
        # FIXME
        # This seems to make sense but it would break in the case that a device
        # has multiple of the same sensor.
        unique_together = ("device", "sensor_type")

    def get_latest_ts_data(self):
        """Get latest ts data on this sensor for this device

        The latest_ts_data_optimised on AbstractDevice should be used instead of
        directly calling this
        """

        from .timeseriesdata import TimeSeriesData

        try:
            data = TimeSeriesData.objects.filter(
                sensor=self,
            ).latest("ts")
        except TimeSeriesData.DoesNotExist:
            # If the device hasn't made any timeseries data yet.
            return {}

        return data

    def optimised_data_fetch(self, data_start, data_end, resolution):
        """Get data from given time block and possibly average it

        See Device.optimised_data_fetch for args

        This function assumes all the input data is already validated.
        """

        if resolution < self.resolution or fmod(resolution, self.resolution):
            raise django.db.DataError("Resolution should be a multiple of {} (was {})".format(
                self.resolution, resolution))

        from .timeseriesdata import TimeSeriesData

        # XXX
        # equals for floats? If resolution is not a whole number this won't work
        if resolution == self.resolution:
            # No aggregation, just get the data
            # It's already sorted by time in the database
            data = TimeSeriesData.objects.filter(
                sensor=self,
                ts__gte=data_start,
                ts__lt=data_end,
            )
        else:
            # Multiple of resolution
            # We extract just the values_list here because doing it in a
            # separate statement results in django querying the database
            # twice...
            raw = TimeSeriesData.objects.filter(
                sensor=self,
                ts__gte=data_start,
                ts__lt=data_end,
            ).values_list("value", "ts")

            logger.debug("%s objects to aggregate", len(raw))

            # Already checked that this divides nicely
            aggregation_factor = int(resolution//self.resolution)

            expected_samples = (data_end - data_start).total_seconds()/self.resolution

            aggregation_function = aggregation_implementations[settings.ZCONNECT_TS_AGGREGATION_ENGINE]

            logger.debug("Aggregating '%s' with %s, factor %d",
                self.sensor_type.aggregation_type, settings.ZCONNECT_TS_AGGREGATION_ENGINE,
                aggregation_factor)

            data = aggregation_function(
                raw,
                self.sensor_type.aggregation_type,
                aggregation_factor,
                expected_samples,
                data_start,
                data_end,
                self,
            )

        return data
