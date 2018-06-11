import logging

from zconnect import zsettings
from zconnect.util.general import load_from_module

logger = logging.getLogger(__name__)


class Sender:

    def __init__(self):
        sender_settings = dict(zsettings.SENDER_SETTINGS)
        cls_name = sender_settings.get("cls", "zconnect.messages.IBMInterface")
        interface_class = load_from_module(cls_name)
        self.interface = interface_class(sender_settings)

    def _resolve_device(self, device=None, device_id=None, device_type=None,
                        incoming_message=None):
        if incoming_message:
            if device:
                logger.warning("Message send method was passed two devices, " \
                               "one in the device parameter and one in the " \
                               "incoming_message. The device in " \
                               "incoming_message takes priority.")
            device = incoming_message.device

        if device:
            if device_id or device_type:
                logger.warning("Message send method was passed a device and " \
                               "separate device_id and device_type " \
                               "parameters. The device takes priority over " \
                               "the device_id and device_type.")
            device_id = device.get_iot_id()
            device_type = device.product.iot_name

        if not device_id or not device_type:
            logger.warning("Tried to send a message to a device but neither " \
                           "device nor incoming message was provided")
            return (None, None)

        return (device_id, device_type)

    def to_device(self, category, body, device=None, device_id=None,
                  device_type=None, incoming_message=None, **kwargs):

        (d_id, d_type) = self._resolve_device(device, device_id, device_type,
                                              incoming_message)
        if not d_id or not d_type:
            return # Warning message sent in _resolve_device_args
        self.interface.send_message(category, body, device_id=d_id,
                                    device_type=d_type)

    def as_device(self, category, body, device=None, device_id=None,
                  device_type=None, incoming_message=None, **kwargs):

        (d_id, d_type) = self._resolve_device(device, device_id, device_type,
                                              incoming_message)
        if not d_id or not d_type:
            return # Warning message sent in _resolve_device_args
        self.interface.send_as_device(category, body, device_id=d_id,
                                      device_type=d_type)


class SenderSingleton:
    """ Singleton for message sender object
    """
    instance = None

    def __new__(cls):
        if not cls.instance:
            cls.instance = Sender()

        return cls.instance


def get_sender():
    """ Get singleton for watson sender

    Returns:
        SenderSingleton: global sender object
    """
    sender_settings = dict(zsettings.SENDER_SETTINGS)

    # only connect if there are settings
    if not sender_settings:
        logger.warning("Skipping watson IoT connection because there's no " \
                       "connection details")
        client = None
    else:
        client = SenderSingleton()

    return client
