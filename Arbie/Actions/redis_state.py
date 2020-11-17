"""A store object that uses redis for backend."""

import pickle  # noqa: S403

import redis


def init_redis(address):
    host_and_port = address.split(":")
    if len(host_and_port) != 2:
        raise ValueError(f"Invalid Address to redis server: {address}")
    return redis.Redis(host=host_and_port[0], port=host_and_port[1], db=0)


def _is_collection(key):
    parts = key.split(".")
    return len(parts) == 3 and parts[2].endswith("s")


def _is_item(key):
    parts = key.split(".")
    if len(parts) == 3 and not _is_collection(key):
        return True
    return len(parts) == 4


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
    available. A category containing a list of items ends with an s. A categaroy
    is of redis type set.

    Identifier contains the identifier of the actuall data. In case of a Token
    this would be the address of that token.
    """

    def __init__(self, host):
        self.r = init_redis(host)
        self.r.ping()
        self.local_state = {}

    def __getitem__(self, key):
        if _is_collection(key):
            return self._get_collection(key)
        elif _is_item(key):
            return self._get_item(key)
        return self.local_state[key]

    def __setitem__(self, key, value):
        if _is_collection(key):
            self._add_collection(key, value)
        elif _is_item(key):
            self._add_item(key, value)
        else:
            self.local_state[key] = value
            return
        self.publish(key, "updated")

    def __contains__(self, item) -> bool:
        if item is None:
            return False
        if item in self.local_state:
            return True
        return self.r.exists(item) == 1

    def subscribe(self, event_channel):
        p = self.r.pubsub()
        p.psubscribe(event_channel)
        return p

    def publish(self, event_channel, message):
        self.r.publish(event_channel, message)

    def keys(self):
        return self.local_state.keys()

    def delete(self, key):
        pipe = self.r.pipeline()
        if _is_collection(key):
            collection = self.r.smembers(key)
            for item in collection:
                pipe.delete(f"{key}.{item}")
        pipe.delete(key)
        pipe.execute()

    def _get_collection(self, key):
        self._exist_or_raise(key)
        pipe = self.r.pipeline()
        for item in self.r.smembers(key):
            item_name = item.decode("utf-8")
            item_key = f"{key}.{item_name}"
            pipe.get(item_key)
        raw_items = pipe.execute()
        return list(map(lambda i: pickle.loads(i), raw_items))  # noqa: S301

    def _get(self, key):
        self._exist_or_raise(key)
        return self.r.get(key)

    def _get_item(self, key):
        return pickle.loads(self._get(key))  # noqa: S301

    def _add_collection(self, collection_key, collection):
        pipe = self.r.pipeline()
        for item in collection:
            item_key = f"{collection_key}.{item}"
            pipe.set(item_key, pickle.dumps(item))
            pipe.sadd(collection_key, str(item))
        pipe.execute()

    def _add_item(self, key, value):
        self.r.set(key, pickle.dumps(value))

    def _exist_or_raise(self, key):
        if not self.__contains__(key):
            raise KeyError(f"key: {key} was not found in Redis")
