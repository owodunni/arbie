"""Tests for Address."""

from Arbie.Variables import Address


def test_create():
    address = Address()
    assert address.value is not None


def test_create_from_str():
    str_address = "0x59A19D8c652FA0284f44113D0ff9aBa70bd46fB4"
    bad_str_address = "0x59A19D8c652FA0284f44113d0ff9aba70bd46fb4"
    address = Address(bad_str_address)
    assert address.value == str_address
