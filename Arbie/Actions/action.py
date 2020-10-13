"""Base class for actions."""


class Store(object):
    """Store the state of the Action Tree.

    Making it possible for Actions to share state between each other.
    It also makes it possible for actions to export state.
    """

    def __init__(self):
        self.state = {}

    def __getitem__(self, key):
        return self.state[key]
    
    def add(self, key, item):
        self.state[key] = item


class Action(object):
    """Action operates on data.

    It can also get and set data to the store.
    However the primary result should be transmitted
    as input and output of the on_next function
    """

    def __init__(self, store):
        self.store = store

    def on_next(self, data):
        raise NotImplementedError('Action does not have a on_next statement')

    def on_error(self, error):
        raise NotImplementedError('Action does not have an on_error statement')
