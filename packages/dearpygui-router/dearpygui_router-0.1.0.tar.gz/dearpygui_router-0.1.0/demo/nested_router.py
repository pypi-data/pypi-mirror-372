import dearpygui.dearpygui as dpg
from dearpygui_router import Router

def screen1():
    dpg.add_text("Screen 1")
    dpg.add_button(label="Go To 2", callback=lambda: router_top.navigate("screen2"))

def screen2():
    dpg.add_text("Screen 2")
    dpg.add_button(label="Go To 1", callback=lambda: router_top.navigate("screen1"))

    with dpg.group(horizontal=True):
        with dpg.child_window(width=200):
            dpg.add_text("Left")
            router_left.add_to_context()
        with dpg.child_window(width=200):
            dpg.add_text("Right")
            router_right.add_to_context()

def left1():
    dpg.add_text("Left 1")
def left2():
    dpg.add_text("Left 2")
def right1():
    dpg.add_text("Right 1")
def right2():
    dpg.add_text("Right 2")

dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

router_top = Router("top")
router_top.register_screen_function("screen1", screen1, is_initial=True)
router_top.register_screen_function("screen2", screen2)

router_left = Router("left")
router_left.register_screen_function("p1", left1, is_initial=True)
router_left.register_screen_function("p2", left2)

router_right = Router("right")
router_right.register_screen_function("p1", right1, is_initial=True)
router_right.register_screen_function("p2", right2)

router_top.add_nested(router_right)


with dpg.window(tag="_main_window", label="Router Demo"):
    with dpg.group(horizontal=True):
        dpg.add_button(label="Go To 1", callback=lambda: router_top.navigate("screen1"))
        dpg.add_button(label="Go To 2", callback=lambda: router_top.navigate("screen2"))
        dpg.add_button(label="Jump to screen2 right p2", callback=lambda: router_top.navigate("screen2/p2"))
        dpg.add_button(label="Jump to screen2 right p1", callback=lambda: router_top.navigate("screen2/p1"))
    
    router_top.add_to_context()

dpg.show_viewport()
dpg.set_primary_window("_main_window", True)
dpg.start_dearpygui()
dpg.destroy_context()
