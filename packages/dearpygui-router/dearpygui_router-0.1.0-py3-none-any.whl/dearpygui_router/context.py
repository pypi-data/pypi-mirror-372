import dearpygui.dearpygui as dpg
from typing import Callable, Optional

from dearpygui_router.screen import Screen
from dearpygui_router.stack import pop_router, push_router, top_router
from dearpygui_router.router import Router

_ROOT_ROUTERS = []

def root_router() -> Router:
    if not _ROOT_ROUTERS:
        raise RuntimeError("No router defined")
    return _ROOT_ROUTERS[0]

def navigate(path: str):
    router = root_router()
    router.navigate(path)

def router(tag: Optional[str] = None):
    """Start a router context"""
    router_id = tag or dpg.generate_uuid()
    r = Router(router_id)
    return _RouterContext(r)

def screen(route_name: str, is_initial=False):
    """Start a screen context"""
    router = top_router()
    if not router:
        raise RuntimeError("screen() must be called inside router context")
    
    return _ScreenContext(router, route_name, show=is_initial)

def add_screen_object(route_name, obj: Screen, is_initial=False):
    """Add a screen object to the current router context"""
    router = top_router()
    if not router:
        raise RuntimeError("add_screen() must be called inside router context")
    
    router.register_screen_object(route_name, obj, is_initial)

def add_screen_function(route_name, fn: Callable, is_initial=False):
    """Add a screen object to the current router context"""
    router = top_router()
    if not router:
        raise RuntimeError("add_screen() must be called inside router context")
    
    router.register_screen_function(route_name, fn, is_initial)

class _RouterContext:
    def __init__(self, router: Router):
        self.router = router

    def __enter__(self):
        parent = top_router()
        if parent:
            parent.add_nested(self.router)
        else:
            _ROOT_ROUTERS.append(self.router)

        push_router(self.router)
        self.router.add_to_context()
        dpg.push_container_stack(self.router.container_tag)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pop_router()
        dpg.pop_container_stack()
        self.router.home()

class _ScreenContext:
    def __init__(self, router: Router, route_name: str, show=False):
        self.router = router
        self.route_name = route_name
        self.group_id = dpg.generate_uuid()
        self.show = show

    def __enter__(self):
        group = dpg.add_group(tag=self.group_id, show=self.show)
        dpg.push_container_stack(group)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.router.register_screen_item(self.route_name, self.group_id, is_initial=self.show)
        dpg.pop_container_stack()