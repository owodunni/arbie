"""Utility functions for interacting with Tokens."""

from Arbie.Contracts import Contract


class GenericToken(Contract):
    name = 'bnb'
    protocol = 'tokens'
    abi = 'bnb'
