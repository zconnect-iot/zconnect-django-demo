from django.db import models

from zconnect.models import ModelBase


class Mapping(ModelBase):
    """Mapping a single sensor to a value ???

    Attributes:
        sensor_key (str): Should match the key of the sensor on a product (not the name field)
        transform_function (str): A transform to be applied to a value of this type before it is mapped.
        input_key (str): The input field for the mapping. eg "digital_input_4"
        mapping (WiringMapping): reference to top level mapping object
    """

    sensor_key = models.CharField(max_length=50)
    # long enough?
    transform_function = models.CharField(max_length=50, blank=True)

    input_key = models.CharField(max_length=50)
    mapping = models.ForeignKey("WiringMapping", models.PROTECT, blank=False, related_name="mappings")

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "Wiring Map Object: {} -> ({}) -> {}\n".format(
            self.input_key, self.transform_function or '_', self.sensor_key
        )


class WiringMapping(ModelBase):
    """
    Holds a mapping to show how a device is wired up.

    Mappings can be stored in a number of places, for instance:
        Device
        Product
        Organization

    The mapping field defines how a field which we receive from a device
    should be mapped on to a functional element in timeseries data.

    Example:
    If we receive

    ```
    {
        digital_input__1: 1
    }
    ```

    from a device with a mapping of:

    ```
    {
        name: "LobbyDoor"
        mappings: [
            {
                # The key of the input we're mapping
                "input_key": "digital_input_1",
                # corresponds to the key in product sensors.
                "sensor_key": "em_stop_switch",
                # A preprocessor function just for this field.
                "transform_function": "invert_bool"
            }
        ]
    }
    ```

    and a product which includes a sensor:

    ```
    "sensors": {
        "em_stop_switch": {
            "unit": "",
            "name": "Emergency Stop Switch"
        }
    }
    ```

    Would add time series data of (in pseudo format)

    ```
    {
        "em_stop_switch": 0
    }
    ```

    Attributes:
        name (str): description of what this mapping is
        mappings: Reverse reference to any mappings referencing this model
    """
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        out = "Demo Wiring Mapping: '{}':\n".format(self.name)
        for mapping in self.mappings.all():
            out += "\t{} -> ({}) -> {}\n".format(
                mapping.input_key,
                mapping.transform_function or "",
                mapping.sensor_key
            )
        return out
