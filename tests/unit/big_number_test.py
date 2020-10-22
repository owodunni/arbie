"""Tests for BigNumber."""

from Arbie.Variables import BigNumber


def test_create_big_number():
    bg = BigNumber(5)
    assert bg.to_number() == 5


def test_equals():
    assert BigNumber(5) == BigNumber(5)


def test_list_equals():
    assert [BigNumber(5)] == [BigNumber(5)]


def test_not_equal():
    assert BigNumber(5) != BigNumber(6)


def test_not_list_equals():
    assert [BigNumber(5)] != [BigNumber(6)]
