import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from usb6501 import Usb6501

simulate = "--simulate" in sys.argv
with Usb6501("Dev1", simulate=simulate, hold=True) as d:
    for _ in range(5):
        d.pulse(0, 0, 200)
    print("P0.0 blinked 5 times")
