"""Unit tests for Circuit breaker."""
import pytest

from Arbie.Contracts.circuit_breaker import CircuitBreaker


def raise_exception():
    raise AssertionError()


def test_safe_call():
    breaker = CircuitBreaker(1, 0, raise_exception)
    with pytest.raises(AssertionError):
        breaker.safe_call()
