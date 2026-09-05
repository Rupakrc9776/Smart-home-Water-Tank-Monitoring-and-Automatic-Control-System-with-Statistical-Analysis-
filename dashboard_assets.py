"""Reusable canvas drawing helpers and the dashboard visual language."""

COLORS = {
    "background": "#08101D", "card": "#16213E", "accent": "#00D4FF",
    "success": "#20E58A", "warning": "#F6C945", "danger": "#FF5263",
    "text": "#EAF7FF", "muted": "#8294B2", "water": "#00B9E8",
    "line": "#2B3B59", "glass": "#203A5A",
}


def draw_tank(canvas, items=None, level=0):
    if items is None:
        canvas.create_rectangle(25, 18, 210, 318, outline="#52708C", width=3)
        canvas.create_rectangle(31, 24, 204, 312, outline=COLORS["glass"], width=1)
        canvas.create_line(31, 24, 204, 24, fill=COLORS["accent"], width=2)
        items = {"water": canvas.create_rectangle(32, 312, 203, 312, fill=COLORS["water"], outline="")}
    height = 288 * max(0, min(100, level)) / 100
    canvas.coords(items["water"], 32, 312 - height, 203, 312)
    return items


def draw_pump(canvas):
    canvas.create_oval(38, 14, 112, 88, outline="#52708C", width=2)
    canvas.create_line(112, 51, 174, 51, fill="#52708C", width=8)
    canvas.create_line(174, 51, 174, 70, fill="#52708C", width=5)
    return canvas.create_oval(58, 34, 92, 68, fill=COLORS["muted"], outline="")
