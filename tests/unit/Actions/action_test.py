"""Unittest of redis state."""
from unittest.mock import MagicMock

import pytest
from pytest_mock.plugin import MockerFixture

from Arbie import StateError
from Arbie.Actions import Action, RedisState, Store
from Arbie.Actions.action import Argument


@pytest.fixture
def local_store():
    return Store()


@pytest.fixture
def redis_store(redis_state):
    return Store(redis_state)


class MockAction(object):
    in_variable_name = "pools"
    in_constant_name = "amount"
    out_variable_name = "tokens"

    redis_item_key = "arbie.1.amount"
    redis_collection_key = "arbie.1.pools"
    redis_collection_item_key = "arbie.1.pools.0xA1cB32"

    in_settings = {in_variable_name: "uniswap", in_constant_name: 1337}
    out_settings = {out_variable_name: "good_tokens"}

    in_settings_parsed = {
        in_variable_name: Argument("uniswap"),
        in_constant_name: Argument(1337),
    }

    redis_in_settings_parsed = {
        in_variable_name: Argument("arbie.1.pools"),
        in_constant_name: Argument(1337),
    }

    out_settings_parsed = {out_variable_name: Argument("good_tokens")}


class TestAction(object):
    def test_get_input_output_settings(self, mocker: MockerFixture):
        mocker.patch(
            "Arbie.Actions.action.yaml.safe_load",
            return_value={
                Action.input_key: MockAction.in_settings,
                Action.output_key: MockAction.out_settings,
            },
        )
        action = Action()
        assert MockAction.in_settings_parsed == action.get_input_settings()
        assert MockAction.out_settings_parsed == action.get_output_settings()

    def test_on_next(self):
        with pytest.raises(NotImplementedError):
            Action().on_next(None)


@pytest.fixture
def mock_action():
    mock = MagicMock()
    mock.get_input_settings.return_value = MockAction.in_settings_parsed
    mock.get_output_settings.return_value = MockAction.out_settings_parsed
    return mock


@pytest.fixture
def mock_action_redis():
    mock = MagicMock()
    mock.get_input_settings.return_value = MockAction.redis_in_settings_parsed
    mock.get_output_settings.return_value = MockAction.out_settings_parsed
    return mock


class TestStore(object):
    def test_get_raises(self, local_store):
        with pytest.raises(KeyError):
            local_store.get("key")

    def test_get_add(self, local_store):
        local_store.add("key", 1)
        assert local_store.get("key") == 1

    def test_create_input_value_error(self, local_store, mock_action):
        with pytest.raises(ValueError):
            local_store.create_input(mock_action)

    def test_create_input(self, local_store, mock_action):
        local_store.add("uniswap", 1337)
        local_store.create_input(mock_action)

    def test_publish(self, local_store: Store):
        with pytest.raises(StateError):
            local_store.publish("random channel", "random message")

    def test_subscribe(self, local_store: Store):
        with pytest.raises(StateError):
            local_store.subscribe("random channel")

    def test_delete(self, local_store: Store):
        with pytest.raises(StateError):
            local_store.delete("random key")


class TestRedisStore(object):
    def test_get_raises(self, redis_store):
        with pytest.raises(KeyError):
            redis_store.get("key")

    def test_get_add(self, redis_store):
        redis_store.add("key", 1)
        assert redis_store.get("key") == 1

    def test_store_get(self, redis_state, mocker: MockerFixture):
        mock_get = mocker.patch.object(RedisState, "__getitem__")
        store = Store(redis_state)

        store[MockAction.redis_item_key]  # noqa: WPS428
        assert mock_get.called

    def test_store_add(self, redis_state, mocker: MockerFixture):
        mock_set = mocker.patch.object(RedisState, "__setitem__")
        store = Store(redis_state)

        store.add(MockAction.redis_collection_key, None)
        assert mock_set.called

    def test_create_input_value_error(self, redis_store, mock_action):
        with pytest.raises(ValueError):
            redis_store.create_input(mock_action)

    def test_create_input(self, redis_store, mock_action):
        redis_store.add("uniswap", 1337)
        redis_store.create_input(mock_action)

    def test_create_input_from_redis(self, redis_store, mock_action_redis, mocker):
        mocker.patch.object(RedisState, "__contains__", return_value=True)
        redis_store.create_input(mock_action_redis)
