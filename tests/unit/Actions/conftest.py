"""Common fixtures for Actions."""
from unittest.mock import MagicMock

import pytest
from pytest_mock.plugin import MockerFixture

from Arbie.Actions import RedisState


@pytest.fixture
def redis_mock(mocker: MockerFixture) -> MagicMock:
    mock = MagicMock()
    mocker.patch("Arbie.Actions.redis_state.redis.Redis", return_value=mock)
    return mock


@pytest.fixture
def redis_state(redis_mock):
    state = RedisState("good.host.org:1337")
    assert redis_mock.ping.called
    return state
