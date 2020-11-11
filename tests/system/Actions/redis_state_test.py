"""Unittest of redis state."""
import pickle  # noqa: S403

import pytest

from Arbie.Actions.redis_state import RedisState
from Arbie.Variables import Address

collection_key = "pool_finder.1.pools"
item_key = "pool_finder.1.pools.0xAb12C"


class TestRedisState(object):
    @pytest.fixture
    def redis_state(self, redis_server):
        return RedisState(redis_server, "arbie_test")

    @pytest.fixture
    def redis_item(self, redis_state, address):
        redis_state.r.set(item_key, pickle.dumps(address))
        yield None
        redis_state.r.delete(item_key)

    @pytest.fixture
    def address(self):
        return Address()

    def test_get_empty_state(self, redis_state):
        with pytest.raises(KeyError):
            redis_state[collection_key]
        with pytest.raises(KeyError):
            redis_state[item_key]

    def test_get_item(self, redis_state, redis_item, address):
        assert redis_state[item_key] == address
