import logging

from zconnect.registry import decorators

from django_demo.util import transform_functions
from django_demo.util.exceptions import TransformError

logger = logging.getLogger(__name__)


@decorators.preprocessor(name="demo_mapping")
def mapping_preprocessor(data, device, ts_cls):
    """
    Handles mapping device variables to timeseries keys.

    Mappings should be defined in the wiring_mapping model which can be
    referenced from the following models (in order of precedence):

        - Device
        - SiteGroup
        - CompanyGroup
        - DistributorGroup
        - Product

    So if a mapping is defined on a device, it will override any other mapping.

    NB. If this preprocessor is used, it will mean that any keys in time series
    data which are not found in the mapping will be deleted.
    """

    mapping = device.get_canonical_mapping()

    if not mapping:
        logger.warning("No wiring mapping found for device: %s", device.id)
        return

    # Mapping contains a name and mapping field. We can just lookup each data
    # key in the mapping field, apply the transform and return the value.

    logger.debug("Applying Demo Wiring Mapping named: %s", mapping.name)

    new_data = {}

    for pin_map in mapping.mappings.all():
        # Key, wire_mapping
        try:
            data_value = data[pin_map.input_key]
        except KeyError:
            logger.warning("Received data which did not contain mapping: %s"
                           "for device: %s", pin_map.input_key, device.id)
            continue

        try:
            new_value = apply_transform(pin_map, data_value)
        except TransformError as e:
            logger.warning("Unable to apply transform function: %s on key: %s",
                           e, pin_map.input_key)
            continue

        new_data[pin_map.sensor_key] = new_value

    # Annoyingly we have to delete all keys and then update the dictionary
    # to keep the same reference.
    data.clear()
    data.update(new_data)



def apply_transform(wire_mapping, value):
    """Applies transformation in wire_mapping.transform_function

    Args:
        wire_mapping (WiringMapping): The full wiring mapping object
        value (Any): The value to be transformed

    Raises:
        TransformError: If the transform function raises an error

    Returns:
        Any: The transformed value
    """


    if getattr(wire_mapping, 'transform_function', None):
        transform_name = wire_mapping['transform_function']
        transform_function = getattr(transform_functions, transform_name, None)

        if not transform_function:
            logger.warning("Unknown transform function %s defined on mapping for %s",
                           transform_name, wire_mapping.input_key)
            raise TransformError("Unknown transform function {}".format(transform_name))

        new_value = transform_function(value)

    else:
        new_value = value

    return new_value
