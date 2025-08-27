import time
import math
import types
import tkinter as tk
import pybirdsreynolds.const as const
import pybirdsreynolds.params as params
import pybirdsreynolds.variables as variables
import pybirdsreynolds.reynolds as reynolds
from tkinter import font
from pybirdsreynolds.reynolds import generate_points_and_facultative_move
from pybirdsreynolds.args import display_range

root = None
canvas = None


def rustine_1():
    # TODO BUGFIX
    root.geometry(
        f"{variables.WIDTH_PARAMS + params.WIDTH +1+ variables.WIDTH_CONTROLS}x{max(params.HEIGHT -1, const.HEIGHT_PARAMS_CONTROLS_DEFAULT)}"
    )


def rustine_2():
    # TODO BUGFIX
    root.geometry(
        f"{variables.WIDTH_PARAMS + params.WIDTH +3+ variables.WIDTH_CONTROLS}x{max(params.HEIGHT -3, const.HEIGHT_PARAMS_CONTROLS_DEFAULT)}"
    )


def next_frame():
    if variables.PAUSED:
        generate_points_and_facultative_move(True, False)
        draw_points()


def update():
    if not variables.PAUSED:
        generate_points_and_facultative_move(True, False)
        draw_points()
        draw_fps()
        variables.FRAME_COUNT += 1
        now = time.time()
        if not variables.COUNT:
            variables.LAST_TIME = now
            variables.COUNT = True
        # to stabilize fps
        if now - variables.LAST_TIME >= 1.0:
            variables.FPS_VALUE = variables.FRAME_COUNT / (now - variables.LAST_TIME)
            variables.FRAME_COUNT = 0
            variables.LAST_TIME = now
    # reset fps if paused
    else:
        variables.FRAME_COUNT = 0
        variables.COUNT = False
        variables.FPS_VALUE = 0

    root.after(params.REFRESH_MS, update)


def draw_all(on_other_key, start_repeat, stop_repeat):
    draw_controls_and_params(False, on_other_key, start_repeat, stop_repeat)
    draw_points()
    draw_rectangle()
    draw_fps()
    draw_hidden()


def draw_controls_and_params(
    fullRefreshControls, on_other_key, start_repeat, stop_repeat
):

    normal_font = font.Font(
        family=params.FONT_TYPE, size=params.FONT_SIZE, weight="normal"
    )

    lines = [
        f"{name.removesuffix('_DOC'):15} :    {str(getattr(params, name.removesuffix('_DOC'))).split(maxsplit=1)[0]}"
        for name in vars(params)
        if name.endswith("_DOC") and getattr(params, f"{name[:-4]}_ACTIVATED") == 2
    ] + [
        f"{name.removesuffix('_TEXT'):15} :    {getattr(params, name)} [{getattr(params, name.replace('_TEXT', '_COMMAND'))}]"
        for name in vars(params)
        if name.endswith("_TEXT") and getattr(params, f"{name[:-5]}_ACTIVATED") == 2
    ]
    x_text = 10
    y_text = 10
    canvas.delete("controls")
    canvas.delete("params")
    if variables.WIDTH_PARAMS == 0 and variables.WIDTH_CONTROLS == 0:
        canvas.delete("params_button")
        canvas.delete("controls_button")
        for name in dir(params):
            if name.endswith(("_BUTTON", "_BUTTON_UP", "_BUTTON_DOWN")):
                setattr(params, name, None)
        return

    i_param = -1
    i_control = -1
    y_pos_control = 0
    for i, line in enumerate(lines):
        key = line.split()[0]
        font_to_use = normal_font
        fill = variables.FILL_COLOR

        if i == params.SELECTED_INDEX and params.ARROWS_ACTIVATED > 0:
            i_param = i_param + 1
            fill = "red"
            item = canvas.create_text(
                x_text + variables.WIDTH_CONTROLS + params.WIDTH,
                y_text + i_param * 2.3 * params.FONT_SIZE,
                anchor="nw",
                fill=fill,
                font=font_to_use,
                tags="params",
                text=line.lower(),
            )
            add_canvas_tooltip(
                item,
                getattr(params, key.upper() + "_DOC")
                + " ("
                + display_range(key.upper())
                + ")",
            )
        elif "[" in line:
            i_control = i_control + 1
        elif not "[" in line:
            i_param = i_param + 1
            item = canvas.create_text(
                x_text + variables.WIDTH_CONTROLS + params.WIDTH,
                y_text + i_param * 2.3 * params.FONT_SIZE,
                anchor="nw",
                fill=variables.FILL_COLOR,
                font=font_to_use,
                tags="params",
                text=line.lower(),
            )
            add_canvas_tooltip(
                item,
                getattr(params, key.upper() + "_DOC")
                + " ("
                + display_range(key.upper())
                + ")",
            )

        y_pos_control = y_text + i_control * 2.1 * 2 * params.FONT_SIZE
        y_pos_param = y_text + i_param * 2.3 * params.FONT_SIZE

        if fullRefreshControls:
            first_colon_index = line.find(":") + 1
            f = font.Font(font=font_to_use)
            x_offset = 0
            if "[" in line:
                key = line.split()[0]
                btn_font = (params.FONT_TYPE, params.FONT_SIZE * 2)
                btn_width = 2
                btn_height = 1
                highlight_color = "black"
                highlight_thickness = 2

                name_button = key + "_BUTTON"
                key = line.split()[0]
                icon = getattr(params, key.upper() + "_ICON")
                cmd = getattr(params, key.upper() + "_COMMAND")

                lbl_btn_tmp = tk.Label(
                    canvas,
                    text=icon,
                    fg="black",
                    bg="white",
                    font=btn_font,
                    width=btn_width,
                    height=btn_height,
                    anchor="center",
                    highlightbackground=highlight_color,
                    highlightthickness=highlight_thickness,
                )

                tooltip_text = f"{getattr(params, key.upper() + '_TEXT')} [{getattr(params, key.upper() + '_COMMAND')}]"
                add_widget_tooltip(lbl_btn_tmp, tooltip_text)

                lbl_btn_tmp.bind(
                    "<Button-1>",
                    lambda e, c=cmd: on_other_key(types.SimpleNamespace(keysym=c)),
                )

                # Création du bouton
                if getattr(params, name_button, None) is None:
                    setattr(
                        params,
                        name_button,
                        canvas.create_window(
                            x_text + x_offset + 2,
                            y_pos_control,
                            anchor="nw",
                            window=lbl_btn_tmp,
                            tags=("controls_button",),
                        ),
                    )
                else:
                    canvas.coords(
                        getattr(params, name_button),
                        x_text + x_offset + 2,
                        y_pos_control,
                    )

            first_colon_index = line.find(":") + 1
            f = font.Font(font=font_to_use)
            x_offset = f.measure(line[:first_colon_index])
            if "[" not in line and params.ARROWS_ACTIVATED > 0:
                highlight_color = "black"
                highlight_thickness = 1
                name_button_up = key + "_BUTTON_UP"
                name_button_down = key + "_BUTTON_DOWN"
                lbl_left = tk.Label(
                    canvas,
                    text="<",
                    fg="black",
                    bg="white",
                    font=font_to_use,
                    highlightbackground=highlight_color,
                    highlightthickness=highlight_thickness,
                )
                lbl_left.bind(
                    "<ButtonPress-1>", lambda e, l=line: start_repeat(l, "Left")
                )
                lbl_left.bind("<ButtonRelease-1>", lambda e: stop_repeat())
                if (
                    not hasattr(params, name_button_down)
                    or getattr(params, name_button_down) is None
                ):
                    setattr(
                        params,
                        name_button_down,
                        canvas.create_window(
                            x_text
                            + x_offset
                            + 1
                            + variables.WIDTH_CONTROLS
                            + params.WIDTH,
                            y_pos_param,
                            anchor="nw",
                            window=lbl_left,
                            tags=("params_button",),
                        ),
                    )

                else:
                    canvas.coords(
                        getattr(params, name_button_down),
                        x_text + x_offset + 1 + variables.WIDTH_CONTROLS + params.WIDTH,
                        y_pos_param,
                    )
                lbl_right = tk.Label(
                    canvas,
                    text=">",
                    fg="black",
                    bg="white",
                    font=font_to_use,
                    highlightbackground=highlight_color,
                    highlightthickness=highlight_thickness,
                )
                lbl_right.bind(
                    "<ButtonPress-1>", lambda e, l=line: start_repeat(l, "Right")
                )
                lbl_right.bind("<ButtonRelease-1>", lambda e: stop_repeat())
                if (
                    not hasattr(params, name_button_up)
                    or getattr(params, name_button_up) is None
                ):
                    setattr(
                        params,
                        name_button_up,
                        canvas.create_window(
                            x_text
                            + x_offset
                            + 18
                            + variables.WIDTH_CONTROLS
                            + params.WIDTH,
                            y_pos_param,
                            anchor="nw",
                            window=lbl_right,
                            tags=("params_button",),
                        ),
                    )
                else:
                    canvas.coords(
                        getattr(params, name_button_up),
                        x_text
                        + x_offset
                        + 18
                        + variables.WIDTH_CONTROLS
                        + params.WIDTH,
                        y_pos_param,
                    )


def draw_paused():
    canvas.delete("paused")
    if variables.PAUSED:
        if variables.BLINK_STATE:
            canvas.create_text(
                variables.WIDTH_CONTROLS,
                max(params.HEIGHT, const.HEIGHT_PARAMS_CONTROLS_DEFAULT),
                anchor="sw",
                fill="red",
                font=(params.FONT_TYPE, params.FONT_SIZE, "bold"),
                tags="paused",
                text=" PAUSED ",
            )
        variables.BLINK_STATE = not variables.BLINK_STATE
        canvas.after(500, lambda: draw_paused)


def draw_fps():
    canvas.delete("fps")
    if variables.FPS:
        if not variables.PAUSED:
            if variables.FPS_VALUE == 0:
                value = "..."
            else:
                value = f"{variables.FPS_VALUE:.1f}"
        else:
            value = "NA"
        canvas.create_text(
            variables.WIDTH_CONTROLS,
            0,
            anchor="nw",
            fill="yellow",
            font=(params.FONT_TYPE, params.FONT_SIZE, "bold"),
            tags="fps",
            text=f" FPS : {value}",
        )


def draw_hidden():
    canvas.delete("hidden")
    if variables.HIDDEN:
        canvas.create_text(
            variables.WIDTH_CONTROLS + params.WIDTH,
            max(params.HEIGHT, const.HEIGHT_PARAMS_CONTROLS_DEFAULT),
            anchor="se",
            fill="gray",
            font=(params.FONT_TYPE, params.FONT_SIZE),
            tags="hidden",
            text="h to restore panels ",
        )


def draw_rectangle():
    if not is_maximized():
        const.WIDTH_BEFORE_MAXIMIZED = params.WIDTH
        const.HEIGHT_BEFORE_MAXIMIZED = params.HEIGHT
    canvas.delete("boundary")
    canvas.create_rectangle(
        variables.WIDTH_CONTROLS,
        0,
        variables.WIDTH_CONTROLS + params.WIDTH,
        params.HEIGHT,
        outline=variables.FILL_COLOR,
        width=const.MARGIN,
        tags="boundary",
    )


def draw_canvas_hidden():
    # TODO BUG FIX
    # root.geometry(f"{params.WIDTH+2}x{max(params.HEIGHT, const.HEIGHT_PARAMS_CONTROLS_DEFAULT)}")
    # root.minsize(params.WIDTH+2, params.HEIGHT)
    # root.maxsize(params.WIDTH+2, params.HEIGHT)
    root.geometry(
        f"{params.WIDTH}x{max(params.HEIGHT, const.HEIGHT_PARAMS_CONTROLS_DEFAULT)}"
    )
    root.minsize(params.WIDTH, params.HEIGHT)
    root.maxsize(params.WIDTH, params.HEIGHT)
    width_tmp = params.WIDTH
    height_tmp = params.HEIGHT
    root.update()
    root.minsize(params.WIDTH_MIN, params.HEIGHT_MIN)
    root.maxsize(10000, 10000)
    root.update()
    params.WIDTH = width_tmp
    params.HEIGHT = height_tmp


def draw_canvas():
    root.geometry(
        f"{variables.WIDTH_PARAMS+params.WIDTH+variables.WIDTH_CONTROLS+2}x{max(params.HEIGHT, const.HEIGHT_PARAMS_CONTROLS_DEFAULT)}"
    )
    canvas.config(
        width=variables.WIDTH_PARAMS + params.WIDTH + variables.WIDTH_CONTROLS + 2,
        height=max(params.HEIGHT, const.HEIGHT_PARAMS_CONTROLS_DEFAULT),
        bg=variables.CANVAS_BG,
    )


def is_maximized():
    if root.tk.call("tk", "windowingsystem") == "aqua":
        return bool(root.attributes("-fullscreen"))
    if root.state() == "zoomed":
        return True
    try:
        if root.attributes("-zoomed"):
            return True
    except tk.TclError:
        pass
    return (
        root.winfo_width() >= root.winfo_screenwidth()
        and root.winfo_height() >= root.winfo_screenheight()
    )


def draw_points():
    fill = variables.FILL_COLOR
    outline = variables.OUTLINE_COLOR
    size = params.SIZE
    cos_150 = math.cos(math.radians(150))
    sin_150 = math.sin(math.radians(150))    

    triangle_size = 6 * size
    triangle_width = 4 * size

    if not variables.POINTS_ID:
        # Création initiale
        for (x, y), (vx, vy) in zip(reynolds.birds, reynolds.velocities):
            if not params.TRIANGLES:
                pid = canvas.create_oval(x - size, y - size, x + size, y + size, fill=fill, outline=outline)
            else:
                pid = canvas.create_polygon(0,0,0,0,0,0, fill=fill, outline=outline)
            variables.POINTS_ID.append(pid)

    for pid, (x, y), (vx, vy) in zip(variables.POINTS_ID, reynolds.birds, reynolds.velocities):
        if not params.TRIANGLES:
            canvas.coords(pid, x - size, y - size, x + size, y + size)
        else:
            angle = math.atan2(vy, vx)
            cos_a, sin_a = math.cos(angle), math.sin(angle)

            tip_x = x + cos_a * triangle_size
            tip_y = y + sin_a * triangle_size

            left_x = x + (cos_a * cos_150 - sin_a * sin_150) * triangle_width
            left_y = y + (sin_a * cos_150 + cos_a * sin_150) * triangle_width

            right_x = x + (cos_a * cos_150 + sin_a * sin_150) * triangle_width
            right_y = y + (sin_a * cos_150 - cos_a * sin_150) * triangle_width

            canvas.coords(pid, tip_x, tip_y, left_x, left_y, right_x, right_y)


def maximize_minimize(force):
    if is_maximized():
        root.state("normal")
        try:
            root.attributes("-zoomed", False)
        except tk.TclError:
            pass
        if not force:
            params.WIDTH = const.WIDTH_BEFORE_MAXIMIZED
            params.HEIGHT = const.HEIGHT_BEFORE_MAXIMIZED
    else:
        const.WIDTH_BEFORE_MAXIMIZED = params.WIDTH
        const.HEIGHT_BEFORE_MAXIMIZED = params.HEIGHT

        wm = root.tk.call("tk", "windowingsystem")
        if wm == "aqua":  # macOS
            root.attributes("-fullscreen", True)
        elif wm == "win32":  # Windows
            root.state("zoomed")
        else:  # Linux
            try:
                root.attributes("-zoomed", True)
            except tk.TclError:
                root.attributes("-fullscreen", True)
    root.focus_force()
    root.focus_set()


def show_tip(widget, text, event=None, dx=10, dy=10, wraplength=200):

    # Si un tooltip est déjà affiché → le détruire
    if variables.TIP_WINDOW is not None:
        try:
            variables.TIP_WINDOW.destroy()
        except:
            pass
        variables.TIP_WINDOW = None

    if not text:
        return

    # Position du tooltip
    if event:  # cas des événements <Enter> sur un Canvas
        x = widget.winfo_rootx() + event.x + dx
        y = widget.winfo_rooty() + event.y + dy
    else:  # cas d’un widget normal
        x = widget.winfo_rootx() + dx
        y = widget.winfo_rooty() + widget.winfo_height() + dy

    variables.TIP_WINDOW = tw = tk.Toplevel(widget)
    tw.wm_overrideredirect(True)
    tw.wm_geometry(f"+{x}+{y}")
    label = tk.Label(
        tw,
        text=text,
        background="yellow",
        relief="solid",
        borderwidth=1,
        font=(params.FONT_TYPE, params.FONT_SIZE),
        wraplength=wraplength,
    )
    label.pack(ipadx=4, ipady=2)


def hide_tip(event=None):
    if variables.TIP_WINDOW:
        variables.TIP_WINDOW.destroy()
        variables.TIP_WINDOW = None


def add_canvas_tooltip(item, text):
    canvas.tag_bind(item, "<Enter>", lambda e: show_tip(canvas, text, e))
    canvas.tag_bind(item, "<Leave>", hide_tip)


def add_widget_tooltip(widget, text):
    widget.bind("<Enter>", lambda e: show_tip(widget, text))
    widget.bind("<Leave>", hide_tip)


def on_resize(on_other_key, start_repeat, stop_repeat, event):
    if variables.TRANS_HIDDEN:
        params.WIDTH = max(
            event.width - variables.WIDTH_PARAMS - variables.WIDTH_CONTROLS,
            params.WIDTH_MIN,
        )
        params.HEIGHT = max(event.height, const.HEIGHT_PARAMS_CONTROLS_DEFAULT)
        generate_points_and_facultative_move(False, False)
        draw_points()
        draw_rectangle()
        draw_fps()
        variables.TRANS_HIDDEN = False
        return
    # TODO BUGIFX
    params.WIDTH = max(
        event.width - variables.WIDTH_PARAMS - variables.WIDTH_CONTROLS - 2,
        params.WIDTH_MIN,
    )
    params.HEIGHT = max(event.height, const.HEIGHT_PARAMS_CONTROLS_DEFAULT)
    # params.WIDTH = max(event.width - variables.WIDTH_PARAMS - variables.WIDTH_CONTROLS,params.WIDTH_MIN)
    # params.HEIGHT = max(event.height,const.HEIGHT_PARAMS_CONTROLS_DEFAULT)
    generate_points_and_facultative_move(False, False)
    draw_controls_and_params(True, on_other_key, start_repeat, stop_repeat)
    draw_points()
    draw_rectangle()
    draw_fps()
