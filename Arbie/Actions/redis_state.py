"""A store object that uses redis for backend."""

import redis
import re


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

    # def __getitem__(self, key):
    #    parts = key.split(".")
    #    if len(parts) == 1:
    #        return local_state[key]
    #    elif len(parts) ==
