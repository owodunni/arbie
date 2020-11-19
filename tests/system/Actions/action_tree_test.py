"""System tests for ActionTree."""
import asyncio

import pytest

from Arbie.Actions import Action, ActionTree, Store


class ActionA(Action):
    """Dummy Action for testing.

    [Settings]
    input:
        times_ran_old: actionA.1.times_ran
    output:
        times_ran: actionA.1.times_ran
        my_result: actionA.1.result
    """

    async def on_next(self, data):
        data.times_ran(data.times_ran_old() + 1)
        data.my_result(1337)


class ActionB(Action):
    """Dummy Action for testing.

    [Settings]
    input:
        times_ran_old: actionB.1.times_ran
        someone_elses_result: actionA.1.result
    output:
        times_ran: actionB.1.times_ran
        my_result: result
    """

    async def on_next(self, data):
        data.times_ran(data.times_ran_old() + 1)
        data.my_result(data.someone_elses_result() + 1)


a_times_ran = "actionA.1.times_ran"
b_times_ran = "actionB.1.times_ran"
a_result = "actionA.1.result"
b_result = "result"

redis_channel = a_result


@pytest.fixture
def tree_a(redis_store: Store):
    tree = ActionTree(redis_store)
    tree.add_action(ActionA())

    redis_store.add(a_times_ran, 0)
    yield tree
    redis_store.delete(a_times_ran)
    redis_store.delete(a_result)


@pytest.fixture
def tree_b(redis_store: Store):
    tree = ActionTree(redis_store)
    tree.add_action(ActionB())

    redis_store.add(b_times_ran, 0)
    yield tree
    redis_store.delete(b_times_ran)


pytestmark = pytest.mark.asyncio


async def wait_and_stop(tree):
    await asyncio.sleep(0.2)
    tree.stop()


class TestActionTree(object):
    async def test_subscribe_no_publisher(self, tree_a, redis_store):
        await tree_a.run()
        await tree_a.run()
        assert redis_store.get(a_times_ran) == 2

    async def test_subscribe(self, redis_store: Store, tree_a):
        tree_a.register_event("my_channel")
        redis_store.publish("my_channel", "new pool added")
        await asyncio.gather(tree_a.run(), wait_and_stop(tree_a))
        assert redis_store.get(a_times_ran) == 1

    # Whenever a result is added to redis
    # a message with that variables name is
    # published to the channel with the
    # same name as the variable.
    async def test_subscribe_publish(
        self, redis_store: Store, tree_a: ActionTree, tree_b: ActionTree
    ):
        tree_b.register_event(redis_channel)

        await asyncio.gather(tree_b.run(), tree_a.run(), wait_and_stop(tree_b))
        assert redis_store.get(b_times_ran) == 1
        assert redis_store.get(a_times_ran) == 1
        assert redis_store.get(a_result) == 1337
        assert redis_store.get(b_result) == 1338
