"""ActionTree is a set of Actions."""

import asyncio
import inspect
import logging
import sys
from typing import Dict, List, Tuple

from Arbie.Actions.action import Action, Store
from Arbie.prometheus import get_prometheus

RUN_TIME = get_prometheus().summary("arbie_run", "Time spent running actions")


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
        self.channels = []
        self.is_stopped = False

    def register_event(self, event_channel):
        self.channels.append(self.store.subscribe(event_channel))

    @classmethod
    def create(cls, action_configs: Dict, store: Store, extra_actions=None):
        tree = cls(store)
        for key, config in action_configs.items():
            action = create_action(key, config, extra_actions)
            tree.add_action(action)
        return tree

    def add_action(self, action: Action):
        self.actions.append(action)

    async def run(self):
        with RUN_TIME.time():
            self.is_stopped = False
            if self.channels:
                await self._run_continuous()
            else:
                await self._run_once()

    def stop(self):
        self.is_stopped = True

    async def _run_continuous(self):
        while not self.is_stopped:
            new_messages = self._get_messages()
            if new_messages:
                logging.getLogger().info(f"New messages {new_messages}")
                await self._run_once()
            else:
                await asyncio.sleep(0.1)

    async def _run_once(self):
        for action in self.actions:
            data = self.store.create_input(action)
            action_name = action.__class__.__name__
            with get_prometheus().summary(
                f"{action_name.lower()}_time",
                f"Time taken to process action {action_name}",
            ).time():
                await action.on_next(data)

    def _get_messages(self):
        messages = list(map(lambda c: c.get_message(True), self.channels))
        # Remove None
        return [message for message in messages if message]
