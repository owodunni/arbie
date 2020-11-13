"""Unittest of redis state."""
import pytest

from Arbie.Actions import Action, Store


@pytest.fixture
def local_store():
    return Store()


@pytest.fixture
def redis_store(redis_state):
    return Store(redis_state)


class TestAction(object):


    in_variable_name = "pools"
    out_variable_name = "tokens"

    in_settings = {in_variable_name: "uniswap"}
    out_settings = {out_variable_name: "good_tokens"}

    def test_get_input_settings(self, mocker):
        mocker.patch(
            "Arbie.Actions.action.yaml.safe_load",
            return_value = {
                Action.input_key: TestAction.in_settings,
                Action.output_key: TestAction.out_settings})
        input_settings = Action().get_input_settings()
        assert TestAction.in_settings == input_settings

    def test_get_output_settings(self, mocker):
        assert False

    def test_on_next(self, mocker):
       with pytest.raises(NotImplementedError):
            Action().on_next(None)



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
