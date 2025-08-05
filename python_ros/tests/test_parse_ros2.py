import pytest

from python_ros.rosmsg.parse import parse


def test_parse_ros2_not_implemented():
    with pytest.raises(NotImplementedError):
        parse("string name", ros2=True)
