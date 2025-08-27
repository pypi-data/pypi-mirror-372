import signal
import sys
import copy
import tkinter as tk
import pybirdsreynolds.const as const
import pybirdsreynolds.draw as draw
from importlib.metadata import version
from tkinter import font
from functools import partial
from pybirdsreynolds.args import compute_args
from pybirdsreynolds.draw import draw_paused, draw_status, draw_all, update, on_resize
from pybirdsreynolds.reynolds import generate_points_and_facultative_move
from pybirdsreynolds.controls import (
    on_other_key,
    start_repeat,
    stop_repeat,
    toggle_pause,
    on_shift_press,
    on_shift_release,
)


def app():

    fonts = []
    const.VERSION_PROG = version("pybirdsreynolds")
    options = compute_args()
    for var_name in dir(const):
        if var_name.endswith("_DEFAULT"):
            option_name = var_name[:-8]
            default_value = getattr(const, var_name)
            value = getattr(options, option_name.lower(), default_value)
            setattr(const, option_name, value)

    if not const.COLOR:
        const.CANVAS_BG = "black"
        const.FILL_COLOR = "white"
        const.OUTLINE_COLOR = "black"
    else:
        const.CANVAS_BG = "#87CEEB"
        const.FILL_COLOR = "black"
        const.OUTLINE_COLOR = "white"

    const.MAX_SPEED_INIT = copy.deepcopy(const.MAX_SPEED)
    const.NEIGHBOR_RADIUS_INIT = copy.deepcopy(const.NEIGHBOR_RADIUS)
    const.NUM_BIRDS_INIT = copy.deepcopy(const.NUM_BIRDS)
    const.WIDTH_INIT = copy.deepcopy(const.WIDTH)
    const.HEIGHT_INIT = copy.deepcopy(const.HEIGHT)
    const.REFRESH_MS_INIT = copy.deepcopy(const.REFRESH_MS)
    const.RANDOM_SPEED_INIT = copy.deepcopy(const.RANDOM_SPEED)
    const.RANDOM_ANGLE_INIT = copy.deepcopy(const.RANDOM_ANGLE)
    const.SEP_WEIGHT_INIT = copy.deepcopy(const.SEP_WEIGHT)
    const.ALIGN_WEIGHT_INIT = copy.deepcopy(const.ALIGN_WEIGHT)
    const.COH_WEIGHT_INIT = copy.deepcopy(const.COH_WEIGHT)
    const.SIZE_INIT = copy.deepcopy(const.SIZE)
    const.FONT_SIZE_INIT = copy.deepcopy(const.FONT_SIZE)
    const.FONT_TYPE_INIT = copy.deepcopy(const.FONT_TYPE)
    const.TRIANGLES_INIT = copy.deepcopy(const.TRIANGLES)
    const.FREE_INIT = copy.deepcopy(const.FREE)
    const.COLOR_INIT = copy.deepcopy(const.COLOR)

    param_docs = {
        name.removesuffix("_DOC"): value
        for name, value in vars(const).items()
        if name.endswith("_DOC") and getattr(const, f"{name[:-4]}_HIDEN", 1) == 0
    }
    const.PARAM_ORDER = list(param_docs.keys())

    def signal_handler(sig, frame):
        print("Interrupted! Closing application...")
        draw.root.destroy()
        sys.exit(0)

    def rustine_1():
        # TODO BUGFIX
        draw.root.geometry(
            f"{const.WIDTH_PARAMS + const.WIDTH +1+ const.WIDTH_CONTROLS}x{max(const.HEIGHT -1, const.HEIGHT_PARAMS_CONTROLS_DEFAULT)}"
        )
        # draw.root.geometry(f"{const.WIDTH_PARAMS + const.WIDTH + const.WIDTH_CONTROLS}x{max(const.HEIGHT , const.HEIGHT_PARAMS_CONTROLS_DEFAULT)}")

    def rustine_2():
        # TODO BUGFIX
        draw.root.geometry(
            f"{const.WIDTH_PARAMS + const.WIDTH +3+ const.WIDTH_CONTROLS}x{max(const.HEIGHT -3, const.HEIGHT_PARAMS_CONTROLS_DEFAULT)}"
        )
        # draw.root.geometry(f"{const.WIDTH_PARAMS + const.WIDTH + const.WIDTH_CONTROLS}x{max(const.HEIGHT , const.HEIGHT_PARAMS_CONTROLS_DEFAULT)}")

    draw.root = tk.Tk()
    draw.root.title(f"pybirdsreynolds")
    draw.root.minsize(
        const.WIDTH_PARAMS + const.WIDTH_MIN + const.WIDTH_CONTROLS,
        max(const.HEIGHT, const.HEIGHT_PARAMS_CONTROLS_DEFAULT),
    )
    draw.canvas = tk.Canvas(
        draw.root,
        width=const.WIDTH_PARAMS + const.WIDTH + const.WIDTH_CONTROLS,
        height=const.HEIGHT,
        bg=const.CANVAS_BG,
    )
    draw.canvas.pack(fill="both", expand=True, padx=0, pady=0)
    default_fonts = [f for f in const.FONT_TYPE_LIST if f in font.families()]
    fonts = []
    for f in default_fonts:
        if f not in fonts:
            fonts.append(f)
    if const.FONT_TYPE not in fonts:
        const.FONT_TYPE = fonts[0]
        const.FONT_TYPE_INIT = copy.deepcopy(const.FONT_TYPE)
    generate_points_and_facultative_move(True, False)
    draw_all(on_other_key, start_repeat, stop_repeat)
    draw_status(True, True, on_other_key, start_repeat, stop_repeat)
    draw_paused()
    draw.root.bind("p", toggle_pause)
    draw.root.bind("<Key>", on_other_key)
    draw.root.bind_all("<Shift_L>", on_shift_press)
    draw.root.bind_all("<Shift_R>", on_shift_press)
    draw.root.bind_all("<KeyRelease-Shift_L>", on_shift_release)
    draw.root.bind_all("<KeyRelease-Shift_R>", on_shift_release)
    draw.canvas.bind(
        "<Configure>", partial(on_resize, on_other_key, start_repeat, stop_repeat)
    )

    signal.signal(signal.SIGINT, signal_handler)
    update()
    global last_x, last_y
    last_x = draw.root.winfo_x()
    last_y = draw.root.winfo_y()

    draw.root.after(100, rustine_1)
    draw.root.after(200, rustine_2)
    draw.root.update()
    draw.root.mainloop()
