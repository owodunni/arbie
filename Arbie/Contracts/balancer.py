"""Utility functions for interacting with balancer."""

from Arbie.Contracts import Contract


class PoolFactory(Contract):
    name = 'pool_factory'
    protocol = 'balancer'
