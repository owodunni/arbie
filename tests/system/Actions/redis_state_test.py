"""Unittest of redis state."""
import pytest

from Arbie.Actions.redis_state import RedisState

collection_key = "pool_finder.1.pools"
item_key = "pool_finder.1.pools.0xAb12C"


class TestRedisState(object):
    @pytest.fixture
    def redis_state(self, redis_server):
        return RedisState(redis_server, "arbie_test")

    def test_get(self, redis_state):
        with pytest.raises(KeyError):
            redis_state[""]  # noqa: WPS428
        assert isinstance(redis_state[collection_key], list)
        assert redis_state[item_key] is None
