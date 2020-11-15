"""Common configuration for Action system tests."""

import pytest

from Arbie.Actions import RedisState, Store


@pytest.fixture
def redis_state(redis_server):
    return RedisState(redis_server)


@pytest.fixture
def redis_store(redis_state):
    return Store(redis_state)
