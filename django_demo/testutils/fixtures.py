from unittest.mock import patch

from mockredis import mock_strict_redis_client
import pytest


# Always mock redis
@pytest.fixture(autouse=True)
def fake_get_redis():
    with patch("zconnect.tasks.get_redis", return_value=mock_strict_redis_client()):
        yield
