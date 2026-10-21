"""NI USB-6501 digital I/O (3 ports x 8 lines, 5V TTL) via NI-DAQmx."""
import time

from .sim import SimBackend

PORTS = (0, 1, 2)
LINES = range(8)


def _check(port, line=None):
    if port not in PORTS:
        raise ValueError(f"port must be 0-2, got {port}")
    if line is not None and line not in LINES:
        raise ValueError(f"line must be 0-7, got {line}")


def list_devices():
    import nidaqmx.system
    return [d.name for d in nidaqmx.system.System.local().devices]


class _DaqBackend:
    """Each operation uses a short-lived Task. Note: when a task closes the lines
    return to input (tri-state), so outputs do not hold their level."""

    def __init__(self, dev):
        import nidaqmx
        self._nidaqmx = nidaqmx
        self.dev = dev

    def read_line(self, port, line):
        with self._nidaqmx.Task() as t:
            t.di_channels.add_di_chan(f"{self.dev}/port{port}/line{line}")
            return bool(t.read())

    def write_line(self, port, line, value):
        with self._nidaqmx.Task() as t:
            t.do_channels.add_do_chan(f"{self.dev}/port{port}/line{line}")
            t.write(bool(value))

    def read_port(self, port):
        from nidaqmx.constants import LineGrouping
        with self._nidaqmx.Task() as t:
            t.di_channels.add_di_chan(f"{self.dev}/port{port}",
                                      line_grouping=LineGrouping.CHAN_FOR_ALL_LINES)
            return int(t.read())

    def write_port(self, port, value):
        from nidaqmx.constants import LineGrouping
        with self._nidaqmx.Task() as t:
            t.do_channels.add_do_chan(f"{self.dev}/port{port}",
                                      line_grouping=LineGrouping.CHAN_FOR_ALL_LINES)
            t.write(int(value))

    def close(self):
        pass


class _HoldBackend(_DaqBackend):
    """hold=True: keep one persistent output task per line so levels stay driven."""

    def __init__(self, dev):
        super().__init__(dev)
        self._tasks = {}

    def write_line(self, port, line, value):
        key = (port, line)
        if key not in self._tasks:
            t = self._nidaqmx.Task()
            t.do_channels.add_do_chan(f"{self.dev}/port{port}/line{line}")
            self._tasks[key] = t
        self._tasks[key].write(bool(value))

    def close(self):
        for t in self._tasks.values():
            t.close()
        self._tasks.clear()


class Usb6501:
    def __init__(self, dev_name="Dev1", simulate=False, hold=False):
        if simulate:
            self._b = SimBackend()
        else:
            try:
                self._b = (_HoldBackend if hold else _DaqBackend)(dev_name)
            except ImportError as e:
                raise RuntimeError("nidaqmx not installed (pip install nidaqmx) "
                                   "- use simulate=True to test without hardware") from e

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def close(self):
        self._b.close()

    def read_line(self, port, line):
        _check(port, line)
        return self._b.read_line(port, line)

    def write_line(self, port, line, value):
        _check(port, line)
        self._b.write_line(port, line, value)

    def read_port(self, port):
        _check(port)
        return self._b.read_port(port)

    def write_port(self, port, value):
        _check(port)
        if not 0 <= value <= 255:
            raise ValueError(f"value must be 0-255, got {value}")
        self._b.write_port(port, value)

    def pulse(self, port, line, ms, active=True):
        """Drive the line to `active` for `ms` milliseconds, then to the opposite level."""
        self.write_line(port, line, active)
        time.sleep(ms / 1000)
        self.write_line(port, line, not active)
