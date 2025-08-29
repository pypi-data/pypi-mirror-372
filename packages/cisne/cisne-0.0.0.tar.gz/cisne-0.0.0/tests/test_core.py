import pytest
from cisne.core import hello_cisne, get_version


def test_hello_cisne():
    result = hello_cisne()
    assert result == "Hello from cisne!"


def test_get_version():
    version = get_version()
    assert version == "0.0.0"
