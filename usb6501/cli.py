import argparse
import time

from .device import Usb6501, list_devices


def main(argv=None):
    p = argparse.ArgumentParser(prog="usb6501", description="NI USB-6501 control")
    p.add_argument("--dev", default="Dev1", help="device name in NI MAX (default Dev1)")
    p.add_argument("--simulate", action="store_true", help="no hardware, in-memory sim")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="list NI devices")
    r = sub.add_parser("read", help="read a line, or a whole port if LINE omitted")
    r.add_argument("port", type=int)
    r.add_argument("line", type=int, nargs="?")
    w = sub.add_parser("write", help="write a line (0/1), or a whole port (0-255)")
    w.add_argument("port", type=int)
    w.add_argument("args", type=lambda s: int(s, 0), nargs="+", metavar="[LINE] VALUE")
    pu = sub.add_parser("pulse", help="pulse a line high for MS milliseconds")
    pu.add_argument("port", type=int)
    pu.add_argument("line", type=int)
    pu.add_argument("ms", type=float)
    m = sub.add_parser("monitor", help="poll a port and print on change")
    m.add_argument("port", type=int)
    m.add_argument("--interval", type=float, default=0.1)
    sub.add_parser("gui", help="open the Tkinter GUI")
    a = p.parse_args(argv)

    if a.cmd == "list":
        print("\n".join(list_devices()) or "(no devices)")
        return
    if a.cmd == "gui":
        from .gui import run
        return run(a.dev, a.simulate)

    with Usb6501(a.dev, simulate=a.simulate) as d:
        if a.cmd == "read":
            if a.line is None:
                v = d.read_port(a.port)
                print(f"port{a.port} = {v} (0b{v:08b})")
            else:
                print(int(d.read_line(a.port, a.line)))
        elif a.cmd == "write":
            if len(a.args) == 1:
                d.write_port(a.port, a.args[0])
            else:
                d.write_line(a.port, a.args[0], a.args[1])
        elif a.cmd == "pulse":
            d.pulse(a.port, a.line, a.ms)
        elif a.cmd == "monitor":
            last = None
            try:
                while True:
                    v = d.read_port(a.port)
                    if v != last:
                        print(f"{time.strftime('%H:%M:%S')} port{a.port} = 0b{v:08b}")
                        last = v
                    time.sleep(a.interval)
            except KeyboardInterrupt:
                pass
