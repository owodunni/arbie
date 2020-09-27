"""Tests for BigNumber."""

from Arbie import BigNumber


def test_create_big_number():
    bg = BigNumber(5)
    assert bg.to_numer() == 5
