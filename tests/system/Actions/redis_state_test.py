"""System tests for RedisState."""
import pickle  # noqa: S403

import pytest

from Arbie.Actions.redis_state import RedisState
from Arbie.address import dummy_token_generator

collection_key = "pool_finder.1.pools"
item_key = "pool_finder.1.pools.0xAb12C"


@pytest.fixture
def token():
    return dummy_token_generator("my_token")


@pytest.fixture
def tokens():
    return [dummy_token_generator("token1"), dummy_token_generator("token2")]


class TestRedisState(object):
    @pytest.fixture
    def redis_item(self, redis_state, token):
        redis_state.r.set(item_key, pickle.dumps(token))
        yield None
        redis_state.delete(item_key)

    @pytest.fixture
    def redis_collection(self, redis_state: RedisState, tokens):
        redis_state[collection_key] = tokens
        yield None
        redis_state.delete(collection_key)

    def test_get_empty_state(self, redis_state):
        with pytest.raises(KeyError):
            redis_state[collection_key]
        with pytest.raises(KeyError):
            redis_state[item_key]

    def test_get_item(self, redis_state, redis_item, token):
        assert redis_state[item_key] == token

    def test_get_collection(self, redis_state: RedisState, redis_collection, tokens):
        collection = redis_state[collection_key]

        for t in tokens:
            collection.index(t)

    def test_add_and_get(self, redis_state: RedisState, token):
        redis_state[item_key] = token
        token_round_trip = redis_state[item_key]
        redis_state.delete(item_key)
        assert token_round_trip == token
