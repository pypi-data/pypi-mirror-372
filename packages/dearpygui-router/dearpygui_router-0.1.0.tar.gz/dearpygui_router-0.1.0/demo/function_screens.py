import dearpygui.dearpygui as dpg
from dearpygui_router import Router

def screen1():
    dpg.add_text("Screen 1")
    dpg.add_button(label="Go To 2", callback=lambda: router.navigate("screen2"))

def screen2():
    dpg.add_text("Screen 2")
    dpg.add_button(label="Go To 1", callback=lambda: router.navigate("screen1"))

dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

router = Router("top")
router.register_screen_function("screen1", screen1, is_initial=True)
router.register_screen_function("screen2", screen2)

with dpg.window(tag="_main_window", label="Router Demo"):
    with dpg.group(horizontal=True):
        dpg.add_button(label="Go To 1", callback=lambda: router.navigate("screen1"))
        dpg.add_button(label="Go To 2", callback=lambda: router.navigate("screen2"))
    
    router.add_to_context()

dpg.show_viewport()
dpg.set_primary_window("_main_window", True)
dpg.start_dearpygui()
dpg.destroy_context()
