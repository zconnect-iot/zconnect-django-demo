from gevent import monkey
monkey.patch_all()

# pylint: disable=wrong-import-position
import django
from .listener import get_listener
from zconnect.util.profiling.stats_server import get_flask_server

django.setup(set_prefix=False)

listener = get_listener()
listener.start()

# different wsgi things use different names
app = application = get_flask_server()
