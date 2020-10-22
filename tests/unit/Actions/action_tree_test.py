"""Unittest of ActionTree."""

import pytest
import yaml

from Arbie.Actions import Action, ActionTree, Store


class DummyAction(Action):
    """
    Dummy description for dummy action.

    [Settings]
    input:
    output:
    """


store = Store()


class TestActionTree(object):
    def test_create(self):
        tree = ActionTree.create({"PathFinder": {}}, store)
        assert len(tree.actions) == 1

    def test_create_bad_arg(self):
        config = """
        PathFinder:
            input:
                non_existing: []
        """
        with pytest.raises(ValueError):
            ActionTree.create(yaml.safe_load(config), store)

    def test_create_bad_action(self):
        with pytest.raises(ValueError):
            ActionTree.create({"NonExistingAction": {}}, store)

    def test_create_dummy_action(self):
        config = """
        PathFinder:
        DummyAction:
        """

        tree = ActionTree.create(
            yaml.safe_load(config), store, [("DummyAction", DummyAction)]
        )
        assert len(tree.actions) == 2
