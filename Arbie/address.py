"""Helper functions for interacting with eth addresses."""

import os

from Arbie.Variables.token import Token


def dummy_address_generator() -> str:
    return f"0x{os.urandom(20).hex()}"  # noqa: WPS432


def dummy_token_generator(name, value=None) -> Token:
    return Token(name, dummy_address_generator(), value)
