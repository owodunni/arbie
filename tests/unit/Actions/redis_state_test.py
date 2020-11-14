"""Unittest of redis state."""
import pickle  # noqa: S403
from unittest.mock import MagicMock

import pytest
from pytest_mock.plugin import MockerFixture

from Arbie.Actions.redis_state import RedisState

item_key = "pool_finder.1.unit_of_account"
collection_key = "pool_finder.1.pools"
collection_item_key = "pool_finder.1.pools.0xAb12C"


class TestRedisState(object):
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
        assert isinstance(redis_state[collection_item_key], MagicMock)
        assert mock_item.called
        assert isinstance(redis_state[item_key], MagicMock)

    def test_add(self, redis_state, mocker: MockerFixture):
        mock_collection = mocker.patch.object(RedisState, "_add_collection")
        mock_item = mocker.patch.object(RedisState, "_add_item")

        redis_state["my_key"] = None
        assert len(redis_state.local_state.keys()) == 1

        redis_state[collection_key] = None
        assert mock_collection.called

        redis_state[item_key] = None
        assert mock_item.called

    def test_get_item_raises(self, redis_state, redis_mock):
        redis_mock.exists.return_value = 0
        with pytest.raises(KeyError):
            redis_state[item_key]
        assert redis_mock.exists.called

    def test_get_collection_raises(self, redis_state, redis_mock):
        redis_mock.exists.return_value = 0
        with pytest.raises(KeyError):
            redis_state[collection_key]
        assert redis_mock.exists.called

    def test_get_collection_item_raises(self, redis_state, redis_mock):
        redis_mock.exists.return_value = 0
        with pytest.raises(KeyError):
            redis_state[collection_item_key]
        assert redis_mock.exists.called

    def test_get_keys(self, redis_state):
        redis_state["item"] = 1
        assert len(redis_state.keys()) == 1

    def test_in_redis_state(self, redis_state, redis_mock):
        redis_mock.exists.side_effect = Exception
        assert None not in redis_state

    def test_get_item(self, redis_state, redis_mock):
        redis_mock.exists.return_value = 1
        redis_mock.get.return_value = pickle.dumps(1337)
        assert redis_state[item_key] == 1337
