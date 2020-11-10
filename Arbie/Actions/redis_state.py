"""A store object that uses redis for backend."""

import redis


class RedisState(object):
    """A bridge to access the state stored in redis.

    This makes it possible for different Arbie instances to share state.

    Keys for redis is stored in the following format:
        namespace.version.category.identifier

    Namespace is the name of the Arbie instance running or the name
    of the Arbie instance that we wan to get data from.

    Version is used so that we can change the API with out worrying about breaking
    Arbie instances that rely on old data. When we update how we store data,
    we should update the version. This makes more sence later once we have started
    using protobuff.

    Category contains information regarding what keys are available. If we store
    a list of Tokens then the category would contain the names of the tokens. So
    to get the token we first get the category to figure out which tokens are
    available.

    Identifier contains the identifier of the actuall data. In case of a Token
    this would be the address of that token.
    """

    def __init__(self, host, namespace, port="6379"):
        self.r = redis.Redis(host=host, port=port, db=0)
        self.r.ping()
        self.namespace = namespace
        self.local_state = {}

    def __getitem__(self, key):
        if self._is_collection(key):
            return self._get_collection(key)
        elif self._is_item(key):
            return self._get_item(key)
        return self.local_state[key]

    def __setitem__(self, key, value):
        if self._is_collection(key):
            self._add_collection(value)
        elif self._is_item(key):
            self._add_item(key, value)
        self.local_state[key] = value

    def _is_collection(self, key):
        return len(key.split(".")) == 3

    def _is_item(self, key):
        return len(key.split(".")) == 4

    def _get_collection(self, key):
        raise NotImplementedError()

    def _get_item(self, key):
        raise NotImplementedError()

    def _add_collection(self, key, value):
        raise NotImplementedError()

    def _add_item(self, key, value):
        raise NotImplementedError()
