import datetime
import logging

from dateutil import parser
from django.apps import apps
from django.conf import settings

from zconnect.registry import get_message_handlers, load_from_file

logger = logging.getLogger(__name__)

class Message():
    def __init__(self, category, body, device, timestamp=None):
        """ A standard message object which has all the necessary information
            to construct an event/message in most brokers, e.g. Watson IoT

        Args:
            category (string): The category/type of message which controls what handler(s)
                                will respond to it
            body (dict): A dict which has been decoded by the broker interface.
            device (zconnect.models.Device): The device which this corresponds to.
            timestamp (datetime, optional): if passed in, must be a datetime, or it will be
                            set to the current time.
        """
        self.category = category
        self.body = body
        self.device = device
        self.timestamp = timestamp or datetime.datetime.now()

    def __repr__(self):
        return "Message(\
            category={}\
            timestamp={}\
            device={}\
            body={}\
        )".format(self.category, self.timestamp, self.device.id, self.body)

    def as_dict(self):
        fields = ["category", "body"]
        d =  {f: getattr(self, f, None) for f in fields}
        # Just send the PK of the device, because devices are not serializable
        d["device_pk"] = self.device.pk
        d["timestamp"] = self.timestamp.isoformat()
        return d

    @classmethod
    def from_dict(cls, d):

        device_pk = d.pop("device_pk")
        Device = apps.get_model(settings.ZCONNECT_DEVICE_MODEL)
        device = Device.objects.get(pk=device_pk)

        timestamp = d.pop("timestamp")
        timestamp = parser.parse(timestamp)

        # Recreates a timeseries object
        return cls(
            device=device,
            timestamp=timestamp,
            **d
        )


class MessageProcessor():

    def __init__(self, message_handlers=False):

        if not message_handlers:
            load_from_file("handlers")
            message_handlers = get_message_handlers()
        self.message_handlers = message_handlers

    def process(self, message):
        handlers = self.message_handlers.get(message.category, [])

        if not handlers:
            logger.error("No handler for '{}' messages".format(message.category))
            logger.debug(message.body)
            return

        for handler in handlers:
            try:
                logger.debug("Recieved message: %r", message)
                handler(message, self)
            except Exception: # pylint: disable=broad-except
                logger.exception("Exception raised during processing of "
                                 "event %s", message)


class MessageProcessorSingleton:
    """ Singleton for message processor object
    """
    instance = None

    def __new__(cls):
        if not cls.instance:
            cls.instance = MessageProcessor()

        return cls.instance


def get_message_processor():
    """ Get singleton for MessageProcessor

    Returns:
        MessageProcessor: a message processor
    """
    client = MessageProcessorSingleton()

    return client
