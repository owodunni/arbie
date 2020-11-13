"""Unittest of redis state."""
import pytest

from Arbie.Actions import Action, Store


@pytest.fixture
def local_store():
    return Store()


@pytest.fixture
def redis_store(redis_state):
    return Store(redis_state)


class DummyAction(Action):
    """Dummy action used to test store.

    [Settings]
    input:
        my_key_default: 1
        my_key: required
    output:
        my_output: thing
    """


class TestStore(object):
    def test_get_add(self, local_store):
        local_store.add("key", 1)
        assert local_store.get("key") == 1

    def test_create_input_value_error(self, local_store):
        with pytest.raises(ValueError):
            local_store.create_input(DummyAction())

    def test_create_input(self, local_store):
        local_store.add("required", 1337)
        local_store.create_input(DummyAction())


class TestStoreRedisState(object):
    def test_get_add(self, redis_store):
        redis_store.add("key", 1)
        assert redis_store.get("key") == 1

    def test_create_input_value_error(self, redis_store):
        with pytest.raises(ValueError):
            redis_store.create_input(DummyAction())

    def test_create_input(self, redis_store):
        redis_store.add("required", 1337)
        redis_store.create_input(DummyAction())
