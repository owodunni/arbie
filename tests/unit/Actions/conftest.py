"""Common fixtures for Actions."""
from unittest.mock import MagicMock

import pytest
from pytest_mock.plugin import MockerFixture

from Arbie.Actions import RedisState


def patch_redis(mocker: MockerFixture) -> MagicMock:
    mock = MagicMock()
    mocker.patch("Arbie.Actions.redis_state.redis.Redis", return_value=mock)
    return mock


@pytest.fixture
def redis_state(mocker: MockerFixture):
    mock = patch_redis(mocker)
    state = RedisState("good.host.org:1337")
    assert mock.ping.called
    return state
