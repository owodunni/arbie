"""System tests for ActionTree."""
import pytest
import asyncio

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

    def on_next(self, data):
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

    def on_next(self, data):
        data.times_ran(data.times_ran_old() + 1)
        data.my_result(data.someone_elses_result())

@pytest.fixture
def action_tree_a(redis_store: Store):
    tree = ActionTree(redis_store)
    tree.add_action(ActionA())
    return tree


class TestActionTree(object):
    @pytest.mark.asyncio
    async def test_subscribe_no_publisher(self, action_tree_a, redis_store):
        # what happens if we never publish anything
        await action_tree_a.run()
        await action_tree_a.run()
        assert redis_store.get("actionA.1.times_ran") == 2

    def test_subscribe(self, redis_store: Store):
        tree = ActionTree(redis_store)
        tree.register_event("some_event")
        tree.add_action(ActionA())
        # tree.run()
        # redis_store.publich("arbie.1.pools", "new pool added")
        # assert tree ran once

    def test_subscribe_publish(self, redis_store: Store):
        tree1 = ActionTree(redis_store)
        tree1.register_event("arbie.1.pool")
        tree1.add_action(None)  # Add action A
        # tree1.run()

        tree2 = ActionTree(redis_store)
        tree2.add_action(None)  # Add action B
        tree2.run()
        # assert result from tree2 added to store
        # assert tree1 ran once
