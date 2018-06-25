import logging

from zconnect.registry import get_preprocessor
from zconnect.tasks import send_triggered_events
from zconnect.util.redis_util import RedisEventDefinitions, get_redis
from zconnect.zc_timeseries.models import TimeSeriesData

logger = logging.getLogger(__name__)

def insert_timeseries_data(message, device):
    """
    Adds a timeseries datum to the database for all sensor_types in the message

    This will also call any preprocessors necessary

    """
    # Get the product and check for any preprocessors
    product = device.product

    preprocessors = product.preprocessors.all()

    for preprocessor in preprocessors:
        preprocessor = get_preprocessor(preprocessor.preprocessor_name)
        if preprocessor:
            preprocessor(message.body, device=device, ts_cls=TimeSeriesData)
        else:
            logger.warning("No preprocessor handler called %s on product %s",
                           preprocessor.preprocessor_name, product.name)

    for sensor in device.sensors.all():
        sensor_name = sensor.sensor_type.sensor_name
        if message.body.get(sensor_name) is not None:
            new_datum = TimeSeriesData(
                ts=message.timestamp,
                sensor=sensor,
                value=message.body[sensor_name]
            )
            new_datum.save()


    # Evaluate any definitions data with new datapoint
    context = device.get_context(context=message.body, time=message.timestamp)
    logger.debug("device context %s", context)
    redis_cache = RedisEventDefinitions(get_redis())

    triggered_events = device.evaluate_all_event_definitions(
        context, redis_cache, check_product=True
    )

    send_triggered_events(triggered_events, device, message.body)
