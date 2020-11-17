"""Base class for actions."""

from typing import Dict

import yaml

from Arbie import StateError


class Argument(object):
    def __init__(self, default_value):
        self.name = None
        self.value = None
        if default_value == "None":
            return
        if isinstance(default_value, str):
            self.name = default_value
        else:
            self.value = default_value

    def __eq__(self, other):
        return self.name == other.name and self.value == other.value


def parse_settings(settings: Dict):
    if settings is None:
        return None
    parsed_settings = {}
    for key, argument in settings.items():
        parsed_settings[key] = Argument(argument)
    return parsed_settings


class Action(object):
    """Action is a base class for data processing actions.

    Actions are combined to ActionTrees. Actions are configured
    by parsing their __doc__ and comparing with the settings that
    have been given when starting Arbie.

    Everything bellow the settings section is parsed as yaml.
    There are two lists that need to be configured. The input
    list and the output list. These are then mapped to the items
    that can be read to the store.
    [Settings]
    input:
        key_name: 1  # default_value
    output:
        key_name: variable_name
    """

    input_key = "input"
    output_key = "output"

    def __init__(self, config=None):
        self.settings = self._create_settings()
        self.settings = self._update_settings_with_config(config)

    def get_input_settings(self):
        return self.settings[self.input_key]

    def get_output_settings(self):
        return self.settings[self.output_key]

    def on_next(self, data):
        raise NotImplementedError("Action does not have a on_next statement")

    def _create_settings(self):
        settings = yaml.safe_load(self.__doc__.split("[Settings]\n")[1])

        return {
            self.input_key: parse_settings(settings[self.input_key]),
            self.output_key: parse_settings(settings[self.output_key]),
        }

    def _update_settings_with_config(self, config):
        if config is None:
            return self.settings

        if self.input_key in config and config[self.input_key] is not None:
            self._emplace_settings(config[self.input_key], self.get_input_settings())

        if self.output_key in config and config[self.output_key] is not None:
            self._emplace_settings(config[self.output_key], self.get_output_settings())

        return self.settings

    def _emplace_settings(self, config, settings):
        for key, name in config.items():
            if key not in settings:
                raise ValueError(
                    f"""Argument: {key} is not a valid input/output for action {type(self).__name__},
                        look over your configuration"""
                )
            settings[key] = Argument(name)


def get_value_lambda(value):
    return lambda _: value


class Store(object):
    """Store the state of the Action Tree.

    Making it possible for Actions to share state between each other.
    It also makes it possible for actions to export state.
    """

    def __init__(self, state=None):
        if state is None:
            self.state = {}
        else:
            self.state = state

    def __getitem__(self, key):
        return self.state[key]

    def add(self, key, item):
        self.state[key] = item

    def get(self, key):
        return self.state[key]

    def delete(self, key):
        try:
            self.state.delete(key)
        except AttributeError:
            raise StateError("RedisState is required to remove keys from store.")

    def subscribe(self, event_channel):
        try:
            return self.state.subscribe(event_channel)
        except AttributeError:
            raise StateError("RedisState is required to subscribe to store.")

    def publish(self, event_channel, message):
        try:
            self.state.publish(event_channel, message)
        except AttributeError:
            raise StateError("RedisState is required to publish event.")

    def create_input(self, action):
        return self._create_data(
            action.get_input_settings(), action.get_output_settings()
        )

    def _create_data(self, input_settings, output_settings):
        methods = {}
        for key, argument in input_settings.items():
            if argument.name in self.state:
                methods[key] = self._get_lambda(argument.name)
            elif argument.value is not None:
                methods[key] = get_value_lambda(argument.value)
            else:
                raise ValueError(
                    f"Argument {key}, with name {argument.name} not found in state and no default value"
                )

        for key_out, argument_out in output_settings.items():
            methods[key_out] = self._add_lambda(argument_out.name)
        return type("ActionData", (), methods)()

    def _get_lambda(self, key):
        return lambda _: self.get(key)

    def _add_lambda(self, key):
        return lambda _, value: self.add(key, value)
