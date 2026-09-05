"""Industrial desktop dashboard for the BCREC smart water tank project."""
from __future__ import annotations

import csv
import shutil
import threading
import time
import tkinter as tk
from collections import deque
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox

try:
    import ttkbootstrap as ttk
except ImportError:
    from tkinter import ttk

import serial
from serial.tools import list_ports
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from dashboard_assets import COLORS, draw_pump, draw_tank

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "water_data.csv"
SCREENSHOT_DIR = BASE_DIR / "screenshots"
BAUD_RATE = 9600
LOW_THRESHOLD = 30
FULL_THRESHOLD = 90


def parse_reading(line: str) -> tuple[float, float, str] | None:
    """Parse distance, percentage, pump; also accept the old four-field format."""
    fields = [part.strip() for part in line.split(",")]
    if len(fields) == 3:
        distance, level, pump = fields
    elif len(fields) == 4:
        _, distance, level, pump = fields
    else:
        return None
    try:
        result = max(0.0, float(distance)), min(100.0, max(0.0, float(level))), pump.upper()
    except ValueError:
        return None
    return result if result[2] in {"ON", "OFF"} else None


class DataLogger:
    headers = ["Time", "Distance_cm", "Water_Percent", "Pump"]

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists() or path.stat().st_size == 0:
            with path.open("w", newline="", encoding="utf-8") as file:
                csv.writer(file).writerow(self.headers)

    def read_history(self) -> list[dict[str, str]]:
        try:
            with self.path.open(newline="", encoding="utf-8") as file:
                return list(csv.DictReader(file))
        except (OSError, csv.Error):
            return []

    def append(self, distance: float, level: float, pump: str) -> str:
        stamp = datetime.now().strftime("%H:%M:%S")
        with self.path.open("a", newline="", encoding="utf-8") as file:
            csv.writer(file).writerow((stamp, f"{distance:g}", f"{level:g}", pump))
        return stamp


class SerialReader:
    def __init__(self, port: str, on_reading, on_status) -> None:
        self.port, self.on_reading, self.on_status = port.strip(), on_reading, on_status
        self.connection: serial.Serial | None = None
        self.running = True
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def set_port(self, port: str) -> None:
        with self.lock:
            self.port = port.strip()
        self.close()
        if not self.thread.is_alive():
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()

    def _run(self) -> None:
        while self.running:
            if self.connection is None:
                try:
                    port = self.port or self._find_port()
                    if not port:
                        self.on_status(False, "No Arduino port detected")
                        time.sleep(1)
                        continue
                    self.connection = serial.Serial(port, BAUD_RATE, timeout=0.25)
                    self.on_status(True, f"Connected to {port}")
                except (serial.SerialException, OSError):
                    self.on_status(False, f"Waiting for {self.port or 'Arduino'}")
                    time.sleep(1)
                    continue
            try:
                line = self.connection.readline().decode("utf-8", errors="ignore").strip()
                if line:
                    reading = parse_reading(line)
                    if reading:
                        self.on_reading(reading)
            except (serial.SerialException, OSError):
                self.on_status(False, "Serial communication lost")
                self.close()

    @staticmethod
    def _find_port() -> str | None:
        ports = list(list_ports.comports())
        preferred = ("arduino", "wch", "usb serial", "ch340", "usb")
        for port in ports:
            description = f"{port.description} {port.manufacturer or ''}".lower()
            if any(marker in description for marker in preferred):
                return port.device
        return ports[0].device if ports else None

    def close(self) -> None:
        with self.lock:
            connection, self.connection = self.connection, None
        if connection and connection.is_open:
            connection.close()

    def stop(self) -> None:
        self.running = False
        self.close()


class Dashboard:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("AQUA CONTROL | Automated Water Tank Monitoring")
        self.root.geometry("1440x900")
        self.root.minsize(1100, 720)
        self.root.configure(bg=COLORS["background"])
        self.logger = DataLogger(CSV_PATH)
        self.readings = deque(maxlen=30)
        self.level = self.distance = 0.0
        self.visual_level = 0.0
        self.pump = self.previous_pump = "OFF"
        self.connected = False
        self.activation_count = 0
        self.alerts: deque[str] = deque(maxlen=8)
        self.port_var = tk.StringVar(value="")
        self.mode_var = tk.StringVar(value="AUTO")
        self.status_var = tk.StringVar(value="DISCONNECTED")
        self.status_detail = tk.StringVar(value="Arduino port scan active")
        self._pending_reading = None
        self._reading_queued = False
        self._graph_refresh_queued = False
        self._style()
        self._build_ui()
        self._load_history()
        self.reader = SerialReader(self.port_var.get(), self._queue_reading, self._queue_status)
        self.root.after(50, self._animate_level)
        self.root.after(1000, self._clock_tick)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def _style(self) -> None:
        style = ttk.Style(theme="darkly") if hasattr(ttk, "Window") else ttk.Style()
        style.configure("TFrame", background=COLORS["background"])
        style.configure("Panel.TFrame", background=COLORS["card"])
        style.configure("TLabel", background=COLORS["card"], foreground=COLORS["text"])
        style.configure("Title.TLabel", background=COLORS["background"], foreground=COLORS["accent"], font=("Segoe UI", 19, "bold"))
        style.configure("Kpi.TLabel", background=COLORS["card"], foreground=COLORS["text"], font=("Segoe UI", 22, "bold"))
        style.configure("Muted.TLabel", background=COLORS["card"], foreground=COLORS["muted"], font=("Segoe UI", 9))

    def _panel(self, parent, title: str, column: int, row: int, colspan: int = 1):
        panel = ttk.Frame(parent, style="Panel.TFrame", padding=16)
        panel.grid(row=row, column=column, columnspan=colspan, sticky="nsew", padx=6, pady=6)
        ttk.Label(panel, text=title.upper(), style="Muted.TLabel").pack(anchor="w", pady=(0, 10))
        return panel

    def _build_ui(self) -> None:
        header = ttk.Frame(self.root, padding=(22, 16)); header.pack(fill="x")
        ttk.Label(header, text="AQUA CONTROL", style="Title.TLabel").pack(side="left")
        ttk.Label(header, text="  /  AUTOMATED WATER TANK MONITORING", style="Muted.TLabel").pack(side="left", pady=5)
        right = ttk.Frame(header); right.pack(side="right")
        self.connection_dot = ttk.Label(right, text="●", foreground=COLORS["danger"], font=("Segoe UI", 15)); self.connection_dot.pack(side="left")
        ttk.Label(right, textvariable=self.status_var, foreground=COLORS["danger"], font=("Segoe UI", 10, "bold")).pack(side="left", padx=6)
        self.clock_label = ttk.Label(right, text="--:--:--  |  --", style="Muted.TLabel"); self.clock_label.pack(side="left", padx=10)
        ttk.Label(right, text="PORT", style="Muted.TLabel").pack(side="left", padx=(8, 4))
        ttk.Entry(right, textvariable=self.port_var, width=10).pack(side="left")
        ttk.Button(right, text="RECONNECT", command=self.reconnect).pack(side="left", padx=6)

        kpis = ttk.Frame(self.root, padding=(16, 0)); kpis.pack(fill="x")
        self.kpi_values: dict[str, tk.StringVar] = {}
        cards = (("level", "WATER LEVEL", "accent"), ("pump", "PUMP STATUS", "success"), ("avg", "AVERAGE LEVEL", "accent"), ("max", "MAXIMUM LEVEL", "warning"), ("min", "MINIMUM LEVEL", "muted"), ("alert", "ACTIVE ALERT", "danger"))
        for index, (key, label, color) in enumerate(cards):
            card = ttk.Frame(kpis, style="Panel.TFrame", padding=(14, 12)); card.grid(row=0, column=index, sticky="ew", padx=5); kpis.columnconfigure(index, weight=1)
            ttk.Label(card, text=label, style="Muted.TLabel").pack(anchor="w")
            self.kpi_values[key] = tk.StringVar(value="--")
            ttk.Label(card, textvariable=self.kpi_values[key], style="Kpi.TLabel", foreground=COLORS[color]).pack(anchor="w", pady=(5, 0))

        content = ttk.Frame(self.root, padding=(16, 2)); content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=2); content.columnconfigure(1, weight=3); content.columnconfigure(2, weight=2); content.rowconfigure(0, weight=3); content.rowconfigure(1, weight=2)
        tank_panel = self._panel(content, "Tank visualization", 0, 0)
        self.tank_canvas = tk.Canvas(tank_panel, width=235, height=345, bg=COLORS["card"], highlightthickness=0); self.tank_canvas.pack(fill="both", expand=True)
        self.tank_items = draw_tank(self.tank_canvas); self.tank_percent = self.tank_canvas.create_text(117, 168, text="0%", fill=COLORS["text"], font=("Segoe UI", 25, "bold")); self.tank_distance = self.tank_canvas.create_text(117, 333, text="Distance -- cm", fill=COLORS["muted"], font=("Segoe UI", 10))
        gauge_panel = self._panel(content, "Circular level gauge", 1, 0)
        self.gauge_canvas = tk.Canvas(gauge_panel, width=350, height=290, bg=COLORS["card"], highlightthickness=0); self.gauge_canvas.pack(fill="both", expand=True); self.gauge_canvas.bind("<Configure>", self._resize_gauge)
        self.gauge_track = self.gauge_canvas.create_arc(45, 20, 305, 280, start=210, extent=120, style="arc", outline=COLORS["line"], width=18); self.gauge_arc = self.gauge_canvas.create_arc(45, 20, 305, 280, start=210, extent=1, style="arc", outline=COLORS["accent"], width=18); self.gauge_value = self.gauge_canvas.create_text(175, 139, text="0%", fill=COLORS["text"], font=("Segoe UI", 30, "bold")); ttk.Label(gauge_panel, text="SENSOR RANGE  |  LIVE PERCENTAGE", style="Muted.TLabel").pack()
        pump_panel = self._panel(content, "Pump control", 2, 0)
        self.pump_canvas = tk.Canvas(pump_panel, width=190, height=100, bg=COLORS["card"], highlightthickness=0); self.pump_canvas.pack(pady=4); self.pump_icon = draw_pump(self.pump_canvas)
        self.pump_label = ttk.Label(pump_panel, text="PUMP OFF", style="Kpi.TLabel", foreground=COLORS["muted"]); self.pump_label.pack(); self.relay_label = ttk.Label(pump_panel, text="RELAY DEACTIVATED", style="Muted.TLabel"); self.relay_label.pack(pady=3)
        self.buzzer_label = ttk.Label(pump_panel, text="●  BUZZER STANDBY", style="Muted.TLabel"); self.buzzer_label.pack(pady=3)
        self.stats_label = ttk.Label(pump_panel, text="ACTIVATIONS 0  |  LAST UPDATE --:--:--", style="Muted.TLabel"); self.stats_label.pack(pady=3)
        mode = ttk.Frame(pump_panel); mode.pack(pady=10); ttk.Label(mode, text="CONTROL MODE", style="Muted.TLabel").pack(side="left", padx=5); ttk.Combobox(mode, textvariable=self.mode_var, values=("AUTO", "MANUAL"), state="readonly", width=8).pack(side="left")
        self.led_labels = {}
        for name in ("RED", "YELLOW", "GREEN"):
            label = ttk.Label(pump_panel, text=f"●  {name} LED", foreground=COLORS["muted"], font=("Segoe UI", 10, "bold")); label.pack(anchor="w", pady=2); self.led_labels[name] = label
        graph_panel = self._panel(content, "Live water level trend", 0, 1, 2)
        self.figure = Figure(figsize=(7, 2.5), dpi=100, facecolor=COLORS["card"]); self.axis = self.figure.add_subplot(111); self.graph = FigureCanvasTkAgg(self.figure, master=graph_panel); self.graph.get_tk_widget().pack(fill="both", expand=True)
        alert_panel = self._panel(content, "Alert center", 2, 1)
        self.alert_list = tk.Listbox(alert_panel, height=7, bg=COLORS["card"], fg=COLORS["text"], bd=0, highlightthickness=0, font=("Segoe UI", 10), activestyle="none"); self.alert_list.pack(fill="both", expand=True)
        footer = ttk.Frame(self.root, padding=(22, 8)); footer.pack(fill="x"); ttk.Label(footer, text="BCREC  •  ELECTRICAL ENGINEERING  •  4TH SEMESTER MINI PROJECT", style="Muted.TLabel").pack(side="left")
        for text, command in (("EXPORT CSV", self.export_csv), ("SAVE GRAPH PNG", self.save_graph), ("SCREENSHOT", self.take_screenshot), ("CLEAR GRAPH", self.clear_graph), ("EXIT", self.close)): ttk.Button(footer, text=text, command=command).pack(side="right", padx=3)

    def _load_history(self) -> None:
        for row in self.logger.read_history()[-30:]:
            try: self.readings.append((float(row["Distance_cm"]), float(row["Water_Percent"]), row["Pump"]))
            except (KeyError, TypeError, ValueError): continue
        if self.readings: self._apply_reading(self.readings[-1], False)
        else: self._refresh_graph()

    def _queue_reading(self, reading) -> None:
        self._pending_reading = reading
        if not self._reading_queued:
            self._reading_queued = True
            self.root.after(0, self._drain_reading)

    def _drain_reading(self) -> None:
        self._reading_queued = False
        reading, self._pending_reading = self._pending_reading, None
        if reading:
            self._apply_reading(reading, True)
    def _queue_status(self, connected: bool, message: str) -> None: self.root.after(0, lambda: self._set_status(connected, message))
    def _set_status(self, connected: bool, message: str) -> None:
        self.connected = connected; self.status_var.set("CONNECTED" if connected else "DISCONNECTED"); self.status_detail.set(message)
        self.connection_dot.configure(foreground=COLORS["success"] if connected else COLORS["danger"])
        if connected and message.startswith("Connected to "):
            self.port_var.set(message.removeprefix("Connected to "))

    def _apply_reading(self, reading, log: bool) -> None:
        self.distance, self.level, self.pump = reading; self.readings.append(reading)
        if log: self.logger.append(*reading)
        if self.previous_pump == "OFF" and self.pump == "ON": self.activation_count += 1
        self.previous_pump = self.pump; self.stats_label.configure(text=f"ACTIVATIONS {self.activation_count}  |  LAST UPDATE {datetime.now():%H:%M:%S}"); self._update_visuals()

    def _update_visuals(self) -> None:
        draw_tank(self.tank_canvas, self.tank_items, self.visual_level); self.tank_canvas.itemconfigure(self.tank_percent, text=f"{self.level:.0f}%"); self.tank_canvas.itemconfigure(self.tank_distance, text=f"Distance {self.distance:.1f} cm")
        color = COLORS["success"] if self.level >= FULL_THRESHOLD else COLORS["warning"] if self.level >= LOW_THRESHOLD else COLORS["danger"]; self.gauge_canvas.itemconfigure(self.gauge_arc, extent=max(1, 120 * self.level / 100), outline=color); self.gauge_canvas.itemconfigure(self.gauge_value, text=f"{self.level:.0f}%")
        on = self.pump == "ON"; self.pump_label.configure(text=f"PUMP {'ON' if on else 'OFF'}", foreground=COLORS["success"] if on else COLORS["muted"]); self.relay_label.configure(text=f"RELAY {'ACTIVATED' if on else 'DEACTIVATED'}"); self.pump_canvas.itemconfigure(self.pump_icon, fill=COLORS["success"] if on else COLORS["muted"])
        low = self.level < LOW_THRESHOLD; self.buzzer_label.configure(text=f"●  BUZZER {'WARNING ACTIVE' if low else 'STANDBY'}", foreground=COLORS["danger"] if low else COLORS["muted"])
        active = "RED" if self.level < LOW_THRESHOLD else "YELLOW" if self.level < FULL_THRESHOLD else "GREEN"
        led_colors = {"RED": COLORS["danger"], "YELLOW": COLORS["warning"], "GREEN": COLORS["success"]}
        for name, label in self.led_labels.items(): label.configure(foreground=led_colors[name] if name == active else COLORS["muted"])
        values = [item[1] for item in self.readings]; self.kpi_values["level"].set(f"{self.level:.0f}%"); self.kpi_values["pump"].set("ON" if on else "OFF"); self.kpi_values["avg"].set(f"{sum(values) / len(values):.1f}%" if values else "--"); self.kpi_values["max"].set(f"{max(values):.0f}%" if values else "--"); self.kpi_values["min"].set(f"{min(values):.0f}%" if values else "--")
        alert = "LOW WATER / BUZZER ACTIVE" if self.level < LOW_THRESHOLD else "TANK FULL" if self.level >= FULL_THRESHOLD else ("PUMP RUNNING" if on else "PUMP STOPPED"); self.kpi_values["alert"].set(alert); self._add_alert(alert); self._schedule_graph_refresh()

    def _animate_level(self) -> None:
        self.visual_level += (self.level - self.visual_level) * 0.18
        if abs(self.level - self.visual_level) < 0.1: self.visual_level = self.level
        draw_tank(self.tank_canvas, self.tank_items, self.visual_level)
        self.gauge_canvas.itemconfigure(self.gauge_arc, extent=max(1, 120 * self.visual_level / 100))
        self.root.after(50, self._animate_level)

    def _resize_gauge(self, event) -> None:
        size = max(180, min(event.width - 36, event.height - 22))
        left, top = (event.width - size) / 2, (event.height - size) / 2
        box = (left, top, left + size, top + size)
        for item in (self.gauge_track, self.gauge_arc): self.gauge_canvas.coords(item, *box)
        self.gauge_canvas.coords(self.gauge_value, event.width / 2, top + size / 2)

    def _add_alert(self, text: str) -> None:
        if not self.alerts or self.alerts[-1].split("  |  ")[-1] != text: self.alerts.append(f"{datetime.now():%H:%M:%S}  |  {text}")
        self.alert_list.delete(0, tk.END)
        for alert in reversed(self.alerts): self.alert_list.insert(tk.END, alert)

    def _schedule_graph_refresh(self) -> None:
        if not self._graph_refresh_queued:
            self._graph_refresh_queued = True
            self.root.after(200, self._refresh_graph)

    def _refresh_graph(self) -> None:
        self._graph_refresh_queued = False
        values = [item[1] for item in self.readings]
        self.axis.clear()
        self.axis.set_facecolor(COLORS["card"])
        self.axis.set_ylim(0, 100)
        self.axis.set_xlim(1, 30)
        self.axis.set_ylabel("LEVEL %", color=COLORS["muted"], fontsize=8)
        self.axis.set_xlabel("READING", color=COLORS["muted"], fontsize=8)
        self.axis.set_xticks(range(1, 31, 5))
        self.axis.tick_params(colors=COLORS["muted"], labelsize=8)
        self.axis.grid(color=COLORS["line"], alpha=.55)
        if values:
            x = list(range(1, len(values) + 1))
            self.axis.plot(x, values, color=COLORS["accent"], linewidth=2, solid_capstyle="round")
            self.axis.fill_between(x, values, color=COLORS["accent"], alpha=.12)
        for spine in self.axis.spines.values(): spine.set_color(COLORS["line"])
        self.figure.subplots_adjust(left=.10, right=.98, bottom=.20, top=.94)
        self.graph.draw_idle()

    def _clock_tick(self) -> None: self.clock_label.configure(text=f"{datetime.now():%H:%M:%S  |  %d %b %Y}"); self.root.after(1000, self._clock_tick)
    def reconnect(self) -> None: self.reader.set_port(self.port_var.get().strip())
    def clear_graph(self) -> None:
        self.readings.clear(); self._refresh_graph()
    def export_csv(self) -> None:
        target = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=(("CSV files", "*.csv"),)); shutil.copy2(CSV_PATH, target) if target else None
    def save_graph(self) -> None:
        target = filedialog.asksaveasfilename(defaultextension=".png", filetypes=(("PNG files", "*.png"),)); self.figure.savefig(target, dpi=180, facecolor=COLORS["card"]) if target else None
    def take_screenshot(self) -> None:
        SCREENSHOT_DIR.mkdir(exist_ok=True)
        try:
            from PIL import ImageGrab
            self.root.update_idletasks(); x, y, w, h = self.root.winfo_rootx(), self.root.winfo_rooty(), self.root.winfo_width(), self.root.winfo_height(); ImageGrab.grab(bbox=(x, y, x + w, y + h)).save(SCREENSHOT_DIR / f"dashboard_{datetime.now():%Y%m%d_%H%M%S}.png")
        except (ImportError, OSError) as error: messagebox.showerror("Screenshot failed", str(error))
    def close(self) -> None:
        if hasattr(self, "reader"): self.reader.stop()
        self.root.destroy()


def main() -> None:
    root = ttk.Window(themename="darkly") if hasattr(ttk, "Window") else tk.Tk()
    Dashboard(root); root.mainloop()


if __name__ == "__main__": main()
