"""Unittest of redis state."""
from unittest.mock import MagicMock

import pytest
import redis
from pytest_mock.plugin import MockerFixture

from Arbie.Actions import Store
from Arbie.Actions.redis_state import RedisState


def patch_redis(mocker: MockerFixture) -> MagicMock:
    mock = MagicMock()
    mocker.patch("Arbie.Actions.redis_state.redis.Redis", return_value=mock)
    return mock


false_collection_key = "pool_finder.1.unit_of_account"
collection_key = "pool_finder.1.pools"
item_key = "pool_finder.1.pools.0xAb12C"


class TestRedisState(object):
    def test_bad_host(self, mocker: MockerFixture):
        mock = patch_redis(mocker)
        mock.ping.side_effect = redis.exceptions.ConnectionError
        with pytest.raises(redis.exceptions.ConnectionError):
            RedisState("bad.host.org:1337", "namespace")
        assert mock.ping.called

    @pytest.fixture
    def redis_state(self, mocker: MockerFixture):
        mock = patch_redis(mocker)
        state = RedisState("good.host.org:1337", "namespace")
        assert mock.ping.called
        return state

    def test_get(self, redis_state, mocker: MockerFixture):
        mock_collection = mocker.patch.object(
            RedisState, "_get_collection", return_value=[]
        )
        mock_item = mocker.patch.object(
            RedisState, "_get_item", return_value=MagicMock()
        )

        with pytest.raises(KeyError):
            redis_state[""]
        assert isinstance(redis_state[collection_key], list)
        assert mock_collection.called
        assert isinstance(redis_state[item_key], MagicMock)
        assert mock_item.called
        assert isinstance(redis_state[false_collection_key], MagicMock)

    def test_add(self, redis_state, mocker: MockerFixture):
        mock_collection = mocker.patch.object(RedisState, "_add_collection")
        mock_item = mocker.patch.object(RedisState, "_add_item")

        redis_state["my_key"] = None
        assert len(redis_state.local_state.keys()) == 1

        redis_state[collection_key] = None
        assert mock_collection.called

        redis_state[item_key] = None
        assert mock_item.called

    def test_store_get(self, redis_state, mocker: MockerFixture):
        mock_get = mocker.patch.object(RedisState, "__getitem__")

        store = Store(redis_state)

        store[item_key]
        assert mock_get.called

    def test_store_add(self, redis_state, mocker: MockerFixture):
        mock_set = mocker.patch.object(RedisState, "__setitem__")

        store = Store(redis_state)

        store.add(collection_key, None)
        assert mock_set.called
