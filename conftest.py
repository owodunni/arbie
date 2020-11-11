"""Help module for web3 tests."""
import pytest


def pytest_addoption(parser):
    parser.addoption("--web3_server", action="store", default="http://127.0.0.1:7545")
    parser.addoption("--redis_server", action="store", default="127.0.0.1:6379")
    parser.addoption(
        "--run_slow", action="store_true", default=False, help="run slow tests"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run_slow"):
        # --run_slow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)
