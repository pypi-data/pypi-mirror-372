import types
import copy
import tkinter as tk
import pybirdsreynolds.const as const
import pybirdsreynolds.reynolds as reynolds
import pybirdsreynolds.draw as draw
from pybirdsreynolds.args import get_help_text
from pybirdsreynolds.draw import (
    draw_paused,
    draw_fps,
    draw_canvas,
    draw_canvas_hiden,
    draw_points,
    draw_status,
    draw_all,
    maximize_minimize,
    is_maximized,
    next_frame,
)
from pybirdsreynolds.reynolds import generate_points_and_facultative_move


def on_click(l, sens):
    first_word = l.split()[0] if l.split() else None
    lines = [
        f"{name.removesuffix('_DOC'):15} :    {str(getattr(const, name.removesuffix('_DOC'))).split(maxsplit=1)[0]}"
        for name in vars(const)
        if name.endswith("_DOC") and getattr(const, f"{name[:-4]}_HIDEN", 1) == 0
    ] + [
        f"{name.removesuffix('_TEXT'):15} :    {getattr(const, name)} [{getattr(const, name.replace('_TEXT', '_COMMAND'), '')}]"
        for name in vars(const)
        if name.endswith("_TEXT") and getattr(const, f"{name[:-5]}_HIDEN", 1) == 0
    ]
    const.SELECTED_INDEX = next(
        (i for i, line in enumerate(lines) if line.split(":")[0].strip() == first_word),
        0,
    )
    on_other_key(types.SimpleNamespace(keysym=sens))


def start_repeat(ligne, direction):
    def repeat():
        on_click(ligne, direction)
        if const.REPEATING["active"]:
            const.REPEATING["job"] = draw.canvas.after(100, repeat)

    const.REPEATING["active"] = True
    repeat()


def stop_repeat():
    const.REPEATING["active"] = False
    if const.REPEATING["job"]:
        draw.canvas.after_cancel(const.REPEATING["job"])
        const.REPEATING["job"] = None


def on_shift_press(event):
    const.shift_pressed = True


def on_shift_release(event):
    const.shift_pressed = False


def toggle_pause(event=None):
    const.BLINK_STATE = True
    const.PAUSED = not const.PAUSED
    draw_status(False, False, on_other_key, start_repeat, stop_repeat)
    draw_paused()


def on_other_key(event):
    global fonts
    shift = getattr(event, "state", None)
    if shift is not None:
        shift = (shift & 0x1) != 0
    else:
        shift = const.SHIFT_PRESSED
    if const.SHIFT_HIDEN == 0:
        shift = False
    mult = 10 if shift else 1
    val = mult if event.keysym == "Right" else 1 * -mult
    param = const.PARAM_ORDER[const.SELECTED_INDEX]
    if (param == "WIDTH" or param == "HEIGHT") and is_maximized():
        val = 0
    if event.keysym == "Up" and const.ARROWS_HIDEN < 2:
        const.SELECTED_INDEX = (const.SELECTED_INDEX - 1) % len(const.PARAM_ORDER)
    elif event.keysym == "Down" and const.ARROWS_HIDEN < 2:
        const.SELECTED_INDEX = (const.SELECTED_INDEX + 1) % len(const.PARAM_ORDER)
    elif (
        event.keysym == "Right" or event.keysym == "Left"
    ) and const.ARROWS_HIDEN <= 1:
        if param == "TRIANGLES":
            const.TRIANGLES = not const.TRIANGLES
            draw_all(on_other_key, start_repeat, stop_repeat)
        elif param == "FONT_TYPE":
            current_index = fonts.index(const.FONT_TYPE)
            const.FONT_TYPE = fonts[(current_index + val) % len(fonts)]
            draw_all(on_other_key, start_repeat, stop_repeat)
            draw_status(True, True, on_other_key, start_repeat, stop_repeat)
        elif param == "COLOR":
            COLOR = not COLOR
            if not COLOR:
                const.CANVAS_BG = "black"
                const.FILL_COLOR = "white"
                const.OUTLINE_COLOR = "black"
            else:
                const.CANVAS_BG = "#87CEEB"
                const.FILL_COLOR = "black"
                const.OUTLINE_COLOR = "white"
            draw_canvas()
            draw_all(on_other_key, start_repeat, stop_repeat)
        elif param == "FREE":
            const.FREE = not const.FREE
            for paramm in const.PARAM_ORDER:
                if paramm not in ["FREE", "COLOR", "TRIANGLES", "FONT_TYPE"]:
                    setattr(const, paramm, change_value(paramm, 0, const.FREE))
        else:
            setattr(const, param, change_value(param, val, const.FREE))

        if param == "NUM_BIRDS":
            generate_points_and_facultative_move(False, False)
            draw_points()
        elif param == "WIDTH":
            generate_points_and_facultative_move(False, False)
            draw_status(False, True, on_other_key, start_repeat, stop_repeat)
            draw_canvas()
            draw_all(on_other_key, start_repeat, stop_repeat)
        elif param == "HEIGHT":
            generate_points_and_facultative_move(False, False)
            draw_status(False, True, on_other_key, start_repeat, stop_repeat)
            draw_canvas()
            draw_all(on_other_key, start_repeat, stop_repeat)
        elif param == "FREE":
            generate_points_and_facultative_move(False, False)
            draw_all(on_other_key, start_repeat, stop_repeat)
        elif param == "SIZE":
            generate_points_and_facultative_move(False, False)
            draw_all(on_other_key, start_repeat, stop_repeat)
        elif param == "FONT_SIZE" or param == "FONT_TYPE":
            draw_status(True, True, on_other_key, start_repeat, stop_repeat)
    elif (
        getattr(event, "keysym", "").lower() == str(const.RESET_COMMAND)
        and const.RESET_HIDEN <= 1
    ):
        restore_options()
        generate_points_and_facultative_move(False, False)
        draw_all(on_other_key, start_repeat, stop_repeat)
        draw_canvas()
        draw_status(False, True, on_other_key, start_repeat, stop_repeat)
        draw.root.state("normal")
        draw.root.focus_force()
        draw.root.focus_set()
    elif (
        getattr(event, "keysym", "").lower() == str(const.REGENERATION_COMMAND)
        and const.REGENERATION_HIDEN <= 1
    ):
        reynolds.velocities = []
        reynolds.birds = []
        generate_points_and_facultative_move(False, False)
        draw_points()
    elif (
        getattr(event, "keysym", "").lower() == str(const.TOOGLE_FPS_COMMAND)
        and const.TOOGLE_FPS_HIDEN <= 1
    ):
        const.FPS = not const.FPS
        draw_fps()
    elif (
        getattr(event, "keysym", "").lower() == str(const.TOOGLE_START_PAUSE_COMMAND)
        and const.TOOGLE_START_PAUSE_HIDEN <= 1
    ):
        toggle_pause()
    elif (
        getattr(event, "keysym", "").lower() == str(const.NEXT_FRAME_COMMAND)
        and const.NEXT_FRAME_HIDEN <= 1
    ):
        next_frame()
    elif (
        getattr(event, "keysym", "").lower() == str(const.TOOGLE_MAXIMIZE_COMMAND)
        and const.TOOGLE_MAXIMIZE_HIDEN <= 1
    ):
        maximize_minimize(False)
    elif (
        getattr(event, "keysym", "").lower() == str(const.DOC_COMMAND)
        and const.DOC_HIDEN <= 1
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
        getattr(event, "keysym", "").lower() == str(const.HIDE_COMMAND)
        and const.HIDE_HIDEN <= 1
    ):
        if not const.HIDDEN:
            if is_maximized():
                maximize_minimize(True)
            const.TRANS_HIDEN = True
            const.WIDTH_PARAMS = 0
            const.WIDTH_CONTROLS = 0
            draw_status(True, True, on_other_key, start_repeat, stop_repeat)
            generate_points_and_facultative_move(False, True)
            draw_canvas_hiden()
            const.HIDDEN = True
            draw_all(on_other_key, start_repeat, stop_repeat)
        else:
            const.WIDTH_PARAMS = const.WIDTH_PARAMS_DEFAULT
            const.WIDTH_CONTROLS = const.WIDTH_CONTROLS_DEFAULT
            if is_maximized():
                const.WIDTH = (
                    draw.root.winfo_width() - const.WIDTH_PARAMS - const.WIDTH_CONTROLS
                )
            draw_status(True, True, on_other_key, start_repeat, stop_repeat)
            generate_points_and_facultative_move(False, True)
            draw_canvas()
            const.HIDDEN = False
            draw_all(on_other_key, start_repeat, stop_repeat)
    draw_status(False, False, on_other_key, start_repeat, stop_repeat)


def restore_options():

    const.MAX_SPEED = copy.deepcopy(const.MAX_SPEED_INIT)
    const.NEIGHBOR_RADIUS = copy.deepcopy(const.NEIGHBOR_RADIUS_INIT)
    const.NUM_BIRDS = copy.deepcopy(const.NUM_BIRDS_INIT)
    const.WIDTH = copy.deepcopy(const.WIDTH_INIT)
    const.HEIGHT = copy.deepcopy(const.HEIGHT_INIT)
    const.REFRESH_MS = copy.deepcopy(const.REFRESH_MS_INIT)
    const.RANDOM_SPEED = copy.deepcopy(const.RANDOM_SPEED_INIT)
    const.RANDOM_ANGLE = copy.deepcopy(const.RANDOM_ANGLE_INIT)
    const.SEP_WEIGHT = copy.deepcopy(const.SEP_WEIGHT_INIT)
    const.ALIGN_WEIGHT = copy.deepcopy(const.ALIGN_WEIGHT_INIT)
    const.COH_WEIGHT = copy.deepcopy(const.COH_WEIGHT_INIT)
    const.SIZE = copy.deepcopy(const.SIZE_INIT)
    const.COLOR = copy.deepcopy(const.COLOR_INIT)
    const.FREE = copy.deepcopy(const.FREE_INIT)
    const.TRIANGLES = copy.deepcopy(const.TRIANGLES_INIT)
    const.FONT_TYPE = copy.deepcopy(const.FONT_TYPE_INIT)

    if not const.COLOR:
        const.CANVAS_BG = "black"
        const.FILL_COLOR = "white"
        const.OUTLINE_COLOR = "black"
    else:
        const.CANVAS_BG = "#87CEEB"
        const.FILL_COLOR = "black"
        const.OUTLINE_COLOR = "white"


def change_value(type, val, free):
    value = getattr(const, type, None)
    prefix = type.upper()
    default = getattr(const, f"{prefix}_DEFAULT", None)
    min_value = getattr(const, f"{prefix}_MIN", None)
    max_value = getattr(const, f"{prefix}_MAX", None)
    min_free_value = getattr(const, f"{prefix}_FREE_MIN", None)
    max_free_value = getattr(const, f"{prefix}_FREE_MAX", None)
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
