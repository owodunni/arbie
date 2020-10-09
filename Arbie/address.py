"""Utility function for interacting with ethereum addresses."""

import os

from ethereum import utils


class Address(object):
    """Utility class for Ethereum Addresses."""

    def __init__(self, address: str = None):
        self.value = address
        if self.value is None:
            private_key = utils.sha3(os.urandom(4096))  # noqa: WPS432
            raw = utils.privtoaddr(private_key)
            self.value = raw

        self.value = utils.checksum_encode(self.value)

    def __str__(self):
        return self.value

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash(self.value)
