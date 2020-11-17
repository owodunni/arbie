"""ActionTree is a set of Actions."""

import inspect
import logging
import sys
from typing import Dict, List, Tuple

from Arbie.Actions.action import Action, Store


def is_class_action(member):
    return inspect.isclass(member) and Action in member.__bases__  # noqa: WPS609


def get_all_actions(extra_actions=None) -> List[Tuple[str, type(Action)]]:
    actions = inspect.getmembers(sys.modules["Arbie.Actions"], is_class_action)
    if extra_actions is not None:
        return actions + extra_actions
    return actions


def create_action(name, config, extra_actions):
    for name_cls, action_cls in get_all_actions(extra_actions):
        if name_cls == name:
            return action_cls(config)
    raise ValueError(f"Action: {name} not found.")


class ActionTree(object):
    def __init__(self, store: Store):
        self.store = store
        self.actions = []
        self.channel = None
        self.is_stopped = False

    def register_event(self, event_channel):
        self.channel = self.store.subscribe(event_channel)

    @classmethod
    def create(cls, action_configs: Dict, store: Store, extra_actions=None):
        tree = cls(store)
        for key, config in action_configs.items():
            action = create_action(key, config, extra_actions)
            tree.add_action(action)
        return tree

    def add_action(self, action: Action):
        self.actions.append(action)

    def run(self):
        if self.channel is not None:
            self._run_continous()
        else:
            self._run_once()

    def _run_continous(self):
        while not self.is_stopped:
            new_message = self.channel.get_message()
            logging.getLogger().info(f"New message {new_message}")
            self._run_once()

    def _run_once(self):
        for action in self.actions:
            data = self.store.create_input(action)
            action.on_next(data)
