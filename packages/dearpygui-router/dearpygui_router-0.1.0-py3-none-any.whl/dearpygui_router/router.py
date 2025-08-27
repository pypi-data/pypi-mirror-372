from typing import Dict, Optional, Union, Callable
import dearpygui.dearpygui as dpg

from dearpygui_router.stack import pop_router, push_router
from dearpygui_router.screen import (
    Screen, 
    ScreenFactory, 
    ScreenFunction, 
    ScreenHandler, 
    ScreenInstance, 
    ScreenItemTag
)
from dearpygui_router.types import RouterProtocol

SPECIAL_CHARACTERS = ['/', ':', '#', '*']

Tag = Union[int, str]

class Router(RouterProtocol):
    def __init__(self, name:str):
        self.name = name
        self.container_tag = dpg.generate_uuid()
        self.current_screen:Optional[ScreenHandler] = None
        self.current_route:Optional[str] = None
        self.initial_screen:Optional[str] = None

        self.route_handlers: Dict[str, ScreenHandler] = {}
        self.nested_router: Optional[Router] = None

    def register(self, route_name: str, screen: ScreenHandler, is_initial=False):
        """Register a screen at a named route

        Args:
            route_name (str): Route name. Cannot contain special characters: ['/', ':', '#', '*']
            screen (ScreenHandler): Many types of ScreenHandlers are available based on how the UI is constructed
            is_initial: if True, this screen will be shown on initial render 
        """
        print(f"Register route: {route_name}")
        if route_name in self.route_handlers:
            raise ValueError(f"Route [{route_name}] already exists on this router")
        
        for char in SPECIAL_CHARACTERS:
            if char in route_name:
                raise ValueError(f"Route name cannot contain '{char}'. Character is reserved")
        
        self.route_handlers[route_name] = screen
        
        if is_initial:
            print(f"Set initial route: {route_name}")
            self.initial_screen = route_name

    def register_screen_function(self, route_name: str, fn: Callable, is_initial=False):
        """Register a screen at a named route

        Args:
            route_name (str): Route name. Cannot contain special characters: ['/', ':', '#', '*']
            screen (Callable): A function the sets up the DPG UI elements
            is_initial: if True, this screen will be shown on initial render 
        """
        self.register(route_name, ScreenFunction(fn), is_initial)

    def register_screen_object(self, route_name: str, obj: Screen, is_initial=False):
        """Register a screen at a named route

        Args:
            route_name (str): Route name. Cannot contain special characters: ['/', ':', '#', '*']
            screen (Screen): An object that implements the Screen protocol
            is_initial: if True, this screen will be shown on initial render 
        """
        self.register(route_name, ScreenInstance(obj), is_initial)

    def register_screen_item(self, route_name: str, item_tag: Tag, is_initial=False):
        """Register a screen at a named route

        Args:
            route_name (str): Route name. Cannot contain special characters: ['/', ':', '#', '*']
            screen (int | str): A DPG item, like a group or child_window
            is_initial: if True, this screen will be shown on initial render 
        """
        screen = ScreenItemTag(item_tag)
        self.register(route_name, screen, is_initial)
        if is_initial:
            self.current_screen = screen
            self.current_route = route_name

    def register_screen_factory(self, route_name: str, factory: Callable, is_initial=False):
        """Register a screen at a named route

        Args:
            route_name (str): Route name. Cannot contain special characters: ['/', ':', '#', '*']
            screen (Callable): A function that creates and returns a Screen instance
            is_initial: if True, this screen will be shown on initial render 
        """
        self.register(route_name, ScreenFactory(factory), is_initial)

    def navigate(self, route_name: str) -> None:
        route_first, _, route_rest = route_name.partition("/")
        route_rest = route_rest or None

        print("nav", route_first, route_rest)

        if route_first not in self.route_handlers:
            raise ValueError(f"Route '{route_first}' not found on this router.")

        screen = self.route_handlers[route_first]

        # Hide or remove previous screen
        if self.current_screen:
            # TODO: add a cleanup/remove hook to `Screen`
            pass

        if self.current_screen is not None:
            self.current_screen.hide(self.container_tag)


        push_router(self)
        screen.show(self.container_tag)
        self.current_screen = screen
        self.current_route = route_first

        if route_rest and self.nested_router:
            self.nested_router.navigate(route_rest)
        pop_router()

    def home(self):
        if self.initial_screen is not None:
            self.navigate(self.initial_screen)

    def add_to_context(self) -> None:
        print("Add router UI to context")
        with dpg.child_window(tag=self.container_tag, border=False):
            pass

        if self.initial_screen is not None:
            self.navigate(self.initial_screen)

    def add_nested(self, router: "Router") -> None:
        self.nested_router = router