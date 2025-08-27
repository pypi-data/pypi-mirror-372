import abc
from typing import Callable, Protocol, Union, runtime_checkable
import dearpygui.dearpygui as dpg

Tag = Union[int, str]

@runtime_checkable
class Screen(Protocol):
    def add_to_context(self) -> None: ...

class ScreenHandler(abc.ABC):
    def show(self, container: Tag) -> None: ...
    def hide(self, container: Tag) -> None: ...

class ScreenFunction(ScreenHandler):
    def __init__(self, fn: Callable):
        self.fn = fn

    def show(self, container: Tag) -> None:
        with dpg.group(parent=container):
            self.fn()

    def hide(self, container: Tag) -> None:
        dpg.delete_item(container, children_only=True)

class ScreenInstance(ScreenHandler):
    def __init__(self, screen: Screen):
        self.instance = screen

    def show(self, container: Tag) -> None:
        print("Show screen instance")
        with dpg.group(parent=container):
            self.instance.add_to_context()

    def hide(self, container: Tag) -> None:
        dpg.delete_item(container, children_only=True)

class ScreenFactory(ScreenHandler):
    def __init__(self, factory: Callable[[None], Screen]):
        self.factory = factory

    def show(self, container: Tag) -> None:
        screen:Screen = self.factory()
        with dpg.group(parent=container):
            screen.add_to_context()

    def hide(self, container: Tag) -> None:
        dpg.delete_item(container, children_only=True)

class ScreenItemTag(ScreenHandler):
    def __init__(self, tag: Tag):
        self.tag = tag

    def show(self, container: Tag) -> None:
        dpg.show_item(self.tag)

    def hide(self, container: Tag) -> None:
        dpg.hide_item(self.tag)