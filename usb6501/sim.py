"""In-memory backend so the code can be tested without hardware / NI-DAQmx."""


class SimBackend:
    def __init__(self):
        self.out = {0: 0, 1: 0, 2: 0}   # driven output values per port
        self.dirs = {0: 0, 1: 0, 2: 0}  # bit=1 -> output

    def read_line(self, port, line):
        return bool((self._port_value(port) >> line) & 1)

    def write_line(self, port, line, value):
        if value:
            self.out[port] |= 1 << line
        else:
            self.out[port] &= ~(1 << line)
        self.dirs[port] |= 1 << line

    def read_port(self, port):
        return self._port_value(port)

    def write_port(self, port, value):
        self.out[port] = value
        self.dirs[port] = 0xFF

    def close(self):
        pass

    def _port_value(self, port):
        # Simulated loopback: an output line reads back what was written, inputs read 0.
        return self.out[port] & self.dirs[port]
