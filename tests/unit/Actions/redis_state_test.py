"""Unittest of redis state."""
import pytest
from pytest_mock.plugin import MockerFixture

from Arbie.Actions.redis_state import RedisState

class TestRedisState(object):
    def test_create(self, mocker: MockerFixture):
        mocker.patch("Arbie.Actions.redis_state.redis.Redis")
        state = RedisState("", "")
