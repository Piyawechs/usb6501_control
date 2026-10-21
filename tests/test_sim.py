import pytest

from usb6501 import Usb6501


def test_line_roundtrip():
    with Usb6501(simulate=True) as d:
        d.write_line(0, 3, True)
        assert d.read_line(0, 3) is True
        assert d.read_port(0) == 0b1000
        d.write_line(0, 3, False)
        assert d.read_port(0) == 0


def test_port_write():
    with Usb6501(simulate=True) as d:
        d.write_port(1, 0xA5)
        assert d.read_port(1) == 0xA5


def test_pulse_ends_low():
    with Usb6501(simulate=True) as d:
        d.pulse(2, 7, 1)
        assert d.read_line(2, 7) is False


@pytest.mark.parametrize("port,line", [(3, 0), (0, 8), (-1, 0)])
def test_range_errors(port, line):
    with Usb6501(simulate=True) as d:
        with pytest.raises(ValueError):
            d.read_line(port, line)


def test_value_range():
    with Usb6501(simulate=True) as d:
        with pytest.raises(ValueError):
            d.write_port(0, 256)
