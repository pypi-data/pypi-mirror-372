import dearpygui.dearpygui as dpg
from dearpygui_router import navigate

def add_nav_button(route_name: str, label=None, **kwargs):
    label = label or route_name.split("/")[-1]
    dpg.add_button(label=label, callback=lambda: navigate(route_name), **kwargs)