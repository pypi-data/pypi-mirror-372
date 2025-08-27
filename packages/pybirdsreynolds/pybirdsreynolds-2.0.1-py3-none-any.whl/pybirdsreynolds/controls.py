import types
import copy
import sys
import tkinter as tk
import pybirdsreynolds.const as const
import pybirdsreynolds.params as params
import pybirdsreynolds.variables as variables
import pybirdsreynolds.reynolds as reynolds
import pybirdsreynolds.draw as draw
from pybirdsreynolds.args import get_help_text
from pybirdsreynolds.draw import (
    draw_paused,
    draw_fps,
    draw_canvas,
    draw_canvas_hidden,
    draw_points,
    draw_controls_and_params,
    draw_all,
    maximize_minimize,
    is_maximized,
    next_frame,
)
from pybirdsreynolds.reynolds import generate_points_and_facultative_move


def signal_handler(sig, frame):
    print("Interrupted! Closing application...")
    draw.root.destroy()
    sys.exit(0)


def on_click(l, sens):
    first_word = l.split()[0] if l.split() else None
    lines = [
        f"{name.removesuffix('_DOC'):15} :    {str(getattr(params, name.removesuffix('_DOC'))).split(maxsplit=1)[0]}"
        for name in vars(params)
        if name.endswith("_DOC") and getattr(params, f"{name[:-4]}_ACTIVATED") == 2
    ] + [
        f"{name.removesuffix('_TEXT'):15} :    {getattr(params, name)} [{getattr(params, name.replace('_TEXT', '_COMMAND'))}]"
        for name in vars(params)
        if name.endswith("_TEXT") and getattr(params, f"{name[:-5]}_ACTIVATED") == 2
    ]
    params.SELECTED_INDEX = next(
        (i for i, line in enumerate(lines) if line.split(":")[0].strip() == first_word),
        0,
    )
    on_other_key(types.SimpleNamespace(keysym=sens))


def repeat(ligne, direction):
    on_click(ligne, direction)
    if variables.REPEATING["active"]:
        variables.REPEATING["job"] = draw.canvas.after(100, repeat)


def start_repeat(ligne, direction):
    variables.REPEATING["active"] = True
    repeat(ligne, direction)


def stop_repeat():
    variables.REPEATING["active"] = False
    if variables.REPEATING["job"]:
        draw.canvas.after_cancel(variables.REPEATING["job"])
        variables.REPEATING["job"] = None


def on_shift_press(event):
    variables.shift_pressed = True


def on_shift_release(event):
    variables.shift_pressed = False


def toggle_pause(event=None):
    variables.BLINK_STATE = True
    variables.PAUSED = not variables.PAUSED
    draw_controls_and_params(False, on_other_key, start_repeat, stop_repeat)
    draw_paused()


def on_other_key(event):
    shift = getattr(event, "state", None)
    if shift is not None:
        shift = (shift & 0x1) != 0
    else:
        shift = variables.SHIFT_PRESSED
    if params.SHIFT_ACTIVATED == 2:
        shift = False
    mult = 10 if shift else 1
    val = mult if event.keysym == "Right" else 1 * -mult
    param = params.PARAM_ORDER_IHM[params.SELECTED_INDEX]
    if (param == "WIDTH" or param == "HEIGHT") and is_maximized():
        val = 0
    if event.keysym == "Up" and params.ARROWS_ACTIVATED > 0:
        params.SELECTED_INDEX = (params.SELECTED_INDEX - 1) % len(
            params.PARAM_ORDER_IHM
        )
    elif event.keysym == "Down" and params.ARROWS_ACTIVATED > 0:
        params.SELECTED_INDEX = (params.SELECTED_INDEX + 1) % len(
            params.PARAM_ORDER_IHM
        )
    elif (
        event.keysym == "Right" or event.keysym == "Left"
    ) and params.ARROWS_ACTIVATED >= 1:
        if param == "TRIANGLES":
            params.TRIANGLES = not params.TRIANGLES
            draw_all(on_other_key, start_repeat, stop_repeat)
        elif param == "FONT_TYPE":
            current_index = const.FONT_TYPE_LIST.index(params.FONT_TYPE)
            params.FONT_TYPE = const.FONT_TYPE_LIST[
                (current_index + val) % len(const.FONT_TYPE_LIST)
            ]
            draw_all(on_other_key, start_repeat, stop_repeat)
            draw_controls_and_params(True, on_other_key, start_repeat, stop_repeat)
        elif param == "COLOR":
            COLOR = not COLOR
            if not COLOR:
                variables.CANVAS_BG = "black"
                variables.FILL_COLOR = "white"
                variables.OUTLINE_COLOR = "black"
            else:
                variables.CANVAS_BG = "#87CEEB"
                variables.FILL_COLOR = "black"
                variables.OUTLINE_COLOR = "white"
            draw_canvas()
            draw_all(on_other_key, start_repeat, stop_repeat)
        elif param == "FREE":
            params.FREE = not params.FREE
            for paramm in params.PARAM_ORDER_IHM:
                if paramm not in ["FREE", "COLOR", "TRIANGLES", "FONT_TYPE"]:
                    setattr(params, paramm, change_value(paramm, 0, params.FREE))
        else:
            setattr(params, param, change_value(param, val, params.FREE))

        if param == "NUM_BIRDS":
            generate_points_and_facultative_move(False, False)
            draw_points()
        elif param == "WIDTH":
            generate_points_and_facultative_move(False, False)
            draw_controls_and_params(True, on_other_key, start_repeat, stop_repeat)
            draw_canvas()
            draw_all(on_other_key, start_repeat, stop_repeat)
        elif param == "HEIGHT":
            generate_points_and_facultative_move(False, False)
            draw_controls_and_params(True, on_other_key, start_repeat, stop_repeat)
            draw_canvas()
            draw_all(on_other_key, start_repeat, stop_repeat)
        elif param == "FREE":
            generate_points_and_facultative_move(False, False)
            draw_all(on_other_key, start_repeat, stop_repeat)
        elif param == "SIZE":
            generate_points_and_facultative_move(False, False)
            draw_all(on_other_key, start_repeat, stop_repeat)
        elif param == "FONT_SIZE" or param == "FONT_TYPE":
            draw_controls_and_params(True, on_other_key, start_repeat, stop_repeat)
    elif (
        getattr(event, "keysym", "").lower() == str(params.RESET_COMMAND)
        and params.RESET_ACTIVATED >= 1
    ):
        restore_options()
        generate_points_and_facultative_move(False, False)
        draw_all(on_other_key, start_repeat, stop_repeat)
        draw_canvas()
        draw_controls_and_params(True, on_other_key, start_repeat, stop_repeat)
        draw.root.state("normal")
        draw.root.focus_force()
        draw.root.focus_set()
    elif (
        getattr(event, "keysym", "").lower() == str(params.REGENERATION_COMMAND)
        and params.REGENERATION_ACTIVATED >= 1
    ):
        reynolds.velocities = []
        reynolds.birds = []
        generate_points_and_facultative_move(False, False)
        draw_points()
    elif (
        getattr(event, "keysym", "").lower() == str(params.TOOGLE_FPS_COMMAND)
        and params.TOOGLE_FPS_ACTIVATED >= 1
    ):
        variables.FPS = not variables.FPS
        draw_fps()
    elif (
        getattr(event, "keysym", "").lower() == str(params.TOOGLE_START_PAUSE_COMMAND)
        and params.TOOGLE_START_PAUSE_ACTIVATED >= 1
    ):
        toggle_pause()
    elif (
        getattr(event, "keysym", "").lower() == str(params.NEXT_FRAME_COMMAND)
        and params.NEXT_FRAME_ACTIVATED >= 1
    ):
        next_frame()
    elif (
        getattr(event, "keysym", "").lower() == str(params.TOOGLE_MAXIMIZE_COMMAND)
        and params.TOOGLE_MAXIMIZE_ACTIVATED >= 1
    ):
        maximize_minimize(False)
    elif (
        getattr(event, "keysym", "").lower() == str(params.DOC_COMMAND)
        and params.DOC_ACTIVATED >= 1
    ):
        help = f"pybirdsreynolds {const.VERSION_PROG}\n\n" + get_help_text()
        popin = tk.Toplevel(draw.canvas)
        popin.title("Documentation - pybirdreynolds")
        popin.transient(draw.canvas.winfo_toplevel())
        popin.geometry("+200+200")
        popin.configure(bg="gray")

        frame = tk.Frame(popin, bg="gray")
        frame.pack(padx=10, pady=10)

        text_widget = tk.Text(
            frame,
            wrap="word",
            width=80,
            height=20,
            bg="gray",
            fg="black",
            insertbackground="black",
            highlightthickness=0,
            bd=0,
        )
        text_widget.insert("1.0", help)
        text_widget.config(state="disabled")
        text_widget.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame, command=text_widget.yview)
        scrollbar.pack(side="right", fill="y")
        text_widget.config(yscrollcommand=scrollbar.set)
        popin.wait_visibility()
        popin.grab_set()

    elif (
        getattr(event, "keysym", "").lower() == str(params.HIDE_COMMAND)
        and params.HIDE_ACTIVATED >= 1
    ):
        if not variables.HIDDEN:
            if is_maximized():
                maximize_minimize(True)
            variables.TRANS_HIDDEN = True
            variables.WIDTH_PARAMS = 0
            variables.WIDTH_CONTROLS = 0
            draw_controls_and_params(True, on_other_key, start_repeat, stop_repeat)
            generate_points_and_facultative_move(False, True)
            draw_canvas_hidden()
            variables.HIDDEN = True
            draw_all(on_other_key, start_repeat, stop_repeat)
        else:
            variables.WIDTH_PARAMS = const.WIDTH_PARAMS_DEFAULT
            variables.WIDTH_CONTROLS = const.WIDTH_CONTROLS_DEFAULT
            if is_maximized():
                params.WIDTH = (
                    draw.root.winfo_width()
                    - variables.WIDTH_PARAMS
                    - variables.WIDTH_CONTROLS
                )
            draw_controls_and_params(True, on_other_key, start_repeat, stop_repeat)
            generate_points_and_facultative_move(False, True)
            draw_canvas()
            variables.HIDDEN = False
            draw_all(on_other_key, start_repeat, stop_repeat)
    draw_controls_and_params(False, on_other_key, start_repeat, stop_repeat)


def restore_options():

    params.MAX_SPEED = copy.deepcopy(params.MAX_SPEED_INIT)
    params.NEIGHBOR_RADIUS = copy.deepcopy(params.NEIGHBOR_RADIUS_INIT)
    params.NUM_BIRDS = copy.deepcopy(params.NUM_BIRDS_INIT)
    params.WIDTH = copy.deepcopy(params.WIDTH_INIT)
    params.HEIGHT = copy.deepcopy(params.HEIGHT_INIT)
    params.REFRESH_MS = copy.deepcopy(params.REFRESH_MS_INIT)
    params.RANDOM_SPEED = copy.deepcopy(params.RANDOM_SPEED_INIT)
    params.RANDOM_ANGLE = copy.deepcopy(params.RANDOM_ANGLE_INIT)
    params.SEP_WEIGHT = copy.deepcopy(params.SEP_WEIGHT_INIT)
    params.ALIGN_WEIGHT = copy.deepcopy(params.ALIGN_WEIGHT_INIT)
    params.COH_WEIGHT = copy.deepcopy(params.COH_WEIGHT_INIT)
    params.SIZE = copy.deepcopy(params.SIZE_INIT)
    params.COLOR = copy.deepcopy(params.COLOR_INIT)
    params.FREE = copy.deepcopy(params.FREE_INIT)
    params.TRIANGLES = copy.deepcopy(params.TRIANGLES_INIT)
    params.FONT_TYPE = copy.deepcopy(params.FONT_TYPE_INIT)

    if not params.COLOR:
        variables.CANVAS_BG = "black"
        variables.FILL_COLOR = "white"
        variables.OUTLINE_COLOR = "black"
    else:
        variables.CANVAS_BG = "#87CEEB"
        variables.FILL_COLOR = "black"
        variables.OUTLINE_COLOR = "white"


def change_value(type, val, free):
    value = getattr(params, type, None)
    prefix = type.upper()
    min_value = getattr(params, f"{prefix}_MIN", None)
    max_value = getattr(params, f"{prefix}_MAX", None)
    min_free_value = getattr(params, f"{prefix}_FREE_MIN", None)
    max_free_value = getattr(params, f"{prefix}_FREE_MAX", None)
    value += val
    if not free:
        if max_value is not None:
            value = min(value, max_value)
        if min_value is not None:
            value = max(value, min_value)
    else:
        if max_free_value is not None:
            value = min(value, max_free_value)
        if min_free_value is not None:
            value = max(value, min_free_value)
    return value
