"""Action Tree is a set of Actions."""

import inspect
import sys
from typing import Dict, List, Tuple

from Arbie.Actions import Action, Store


def is_class_action(member):
    return inspect.isclass(member) and Action in member.__bases__  # noqa: WPS609


def get_all_actions() -> List[Tuple[str, type(Action)]]:
    return inspect.getmembers(sys.modules['Arbie.Actions'], is_class_action)


def create_action(name, config):
    for name_cls, action_cls in get_all_actions():
        if name_cls == name:
            return action_cls(config)


class ActionTree(object):

    def __init__(self, store: Store):
        self.store = store
        self.actions = []

    @classmethod
    def create(cls, action_configs: Dict, store: Store):
        tree = cls(store)
        for key, config in action_configs.items():
            action = create_action(key, config)
            tree.add_action(action)
        return tree

    def add_action(self, action: Action):
        self.actions.append(action)

    def run(self):
        for action in self.actions:
            data = self.store.create_input(action)
            action.on_next(data)
