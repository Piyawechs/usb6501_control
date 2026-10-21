import tkinter as tk

from .device import Usb6501


def run(dev="Dev1", simulate=False):
    root = tk.Tk()
    root.title("NI USB-6501")
    dev_var = tk.StringVar(value=dev)
    sim_var = tk.BooleanVar(value=simulate)
    state = {"d": None}
    dirs = {}     # (port,line) -> BooleanVar True=output
    outs = {}     # (port,line) -> bool
    leds = {}

    def connect():
        if state["d"]:
            state["d"].close()
        try:
            state["d"] = Usb6501(dev_var.get(), simulate=sim_var.get(), hold=True)
            status.set("connected")
        except Exception as e:
            state["d"] = None
            status.set(f"error: {e}")

    def toggle(p, l):
        outs[(p, l)] = not outs.get((p, l), False)
        if state["d"] and dirs[(p, l)].get():
            try:
                state["d"].write_line(p, l, outs[(p, l)])
            except Exception as e:
                status.set(f"error: {e}")
        refresh_btn(p, l)

    def refresh_btn(p, l):
        on = outs.get((p, l), False)
        leds[(p, l)].config(text="1" if on else "0", bg="#2ecc71" if on else "#bbb")

    top = tk.Frame(root)
    top.pack(padx=8, pady=6)
    tk.Label(top, text="Device").pack(side="left")
    tk.Entry(top, textvariable=dev_var, width=8).pack(side="left", padx=4)
    tk.Checkbutton(top, text="simulate", variable=sim_var).pack(side="left")
    tk.Button(top, text="Connect", command=connect).pack(side="left", padx=4)

    grid = tk.Frame(root)
    grid.pack(padx=8)
    for p in range(3):
        tk.Label(grid, text=f"P{p}").grid(row=p * 2, column=0)
        for l in range(8):
            dirs[(p, l)] = tk.BooleanVar(value=False)
            tk.Checkbutton(grid, text="out", variable=dirs[(p, l)]).grid(row=p * 2, column=l + 1)
            b = tk.Button(grid, text="0", width=4, bg="#bbb", command=lambda p=p, l=l: toggle(p, l))
            b.grid(row=p * 2 + 1, column=l + 1, padx=2, pady=2)
            leds[(p, l)] = b
    tk.Label(root, text="tick 'out' = drive output (click to toggle); unticked = input (live)").pack()
    status = tk.StringVar(value="not connected")
    tk.Label(root, textvariable=status, anchor="w").pack(fill="x", padx=8, pady=4)

    def poll():
        d = state["d"]
        if d:
            try:
                for p in range(3):
                    for l in range(8):
                        if not dirs[(p, l)].get():
                            outs[(p, l)] = d.read_line(p, l)
                            refresh_btn(p, l)
            except Exception as e:
                status.set(f"error: {e}")
        root.after(200, poll)

    poll()
    root.protocol("WM_DELETE_WINDOW", lambda: (state["d"] and state["d"].close(), root.destroy()))
    root.mainloop()


if __name__ == "__main__":
    run()
