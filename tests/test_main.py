from flowvcutils.main import bray_add
import pytest


def test_bray_add():
    expected = 8
    actual = bray_add(3, 5)
    assert expected == actual


if __name__ == "__main__":
    pytest.main()
