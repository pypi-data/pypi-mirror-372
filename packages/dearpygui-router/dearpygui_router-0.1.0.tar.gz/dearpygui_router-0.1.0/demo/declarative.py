import dearpygui.dearpygui as dpg
import dearpygui_router as router

dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

with dpg.window(tag="_main_window", label="Router Demo"):
    with dpg.group(horizontal=True):
        dpg.add_button(label="Go To 1", callback=lambda: router.navigate("screen1"))
        dpg.add_button(label="Go To 2", callback=lambda: router.navigate("screen2"))

    with router.router(tag="main"):
        with router.screen(route_name="screen1", is_initial=True):
            dpg.add_text("This is screen 1")

        with router.screen(route_name="screen2"):
            dpg.add_text("This is screen 2")

dpg.show_viewport()
dpg.set_primary_window("_main_window", True)
dpg.start_dearpygui()
dpg.destroy_context()
