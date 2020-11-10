"""Help module for web3 tests."""
import pytest


def pytest_addoption(parser):
    parser.addoption("--web3_server", action="store", default="http://127.0.0.1:7545")
    parser.addoption("--redis_server", action="store", default="127.0.0.1:6379")
