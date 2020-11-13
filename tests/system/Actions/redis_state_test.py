"""Unittest of redis state."""
import pickle  # noqa: S403
from typing import List

import pytest

from Arbie.Actions.redis_state import RedisState
from Arbie.Variables import Address

collection_key = "pool_finder.1.pools"
item_key = "pool_finder.1.pools.0xAb12C"


@pytest.fixture
def address():
    return Address()


@pytest.fixture
def addresses():
    return [Address(), Address()]


class TestRedisState(object):
    @pytest.fixture
    def redis_state(self, redis_server):
        return RedisState(redis_server, "arbie_test")

    @pytest.fixture
    def redis_item(self, redis_state, address):
        redis_state.r.set(item_key, pickle.dumps(address))
        yield None
        redis_state.delete(item_key)

    @pytest.fixture
    def redis_collection(self, redis_state: RedisState, addresses: List[Address]):
        redis_state[collection_key] = addresses
        yield None
        redis_state.delete(collection_key)

    def test_get_empty_state(self, redis_state):
        with pytest.raises(KeyError):
            redis_state[collection_key]
        with pytest.raises(KeyError):
            redis_state[item_key]

    def test_get_item(self, redis_state, redis_item, address):
        assert redis_state[item_key] == address

    def test_get_collection(
        self, redis_state: RedisState, redis_collection, addresses: List[Address]
    ):
        collection = redis_state[collection_key]

        for address in addresses:
            collection.index(address)

    def test_add_and_get(self, redis_state: RedisState, address):
        redis_state[item_key] = address
        address_round_trip = redis_state[item_key]
        redis_state.delete(item_key)
        assert address_round_trip == address
