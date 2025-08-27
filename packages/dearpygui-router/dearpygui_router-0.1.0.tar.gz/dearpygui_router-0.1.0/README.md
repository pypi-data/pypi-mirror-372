# dearpygui-router

A router library for [DearPyGui](https://github.com/hoffstadt/dearpygui), designed to make screen navigation and multi-view applications easier to build and manage — with minimal boilerplate.

Inspired by the way DPG uses context managers (`with` blocks), this router library introduces a stack-based, nested routing system that supports:
- Multiple screens
- Nested routers
- Declarative layout

---

## 🚀 Installation

```bash
pip install dearpygui-router
```

## Motivation

Managing multiple "screens" in DearPyGui typically requires manually hiding/showing groups or rebuilding the UI on each view switch. dearpygui-router simplifies this by letting you declare a route hierarchy that can be navigated like a state machine.

## Features

- ✅ Simple navigation: `navigate("route")`
- ✅ Nested routers: `navigate("parent/child/screen")`
- ✅ Screens as reusable classes or functions
- ✅ Familiar DPG-style API: with `dpgr.router()`, with `dpgr.screen()`

## Basic Usage

dearpygui-router has a a few different ways to setup a Router and Screens

### Declarative Screens

```python
import dearpygui.dearpygui as dpg
import dearpygui_router as dpgr

dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

with dpg.window(tag="_main_window", label="Router Demo"):
    # Nav Buttons
    with dpg.group(horizontal=True):
        dpg.add_button(label="Go To 1", callback=lambda: dpgr.navigate("screen1"))
        dpg.add_button(label="Go To 2", callback=lambda: dpgr.navigate("screen2"))

    # Router with two screens
    with dpgr.router(tag="main"):
        with dpgr.screen(route_name="screen1", is_initial=True):
            dpg.add_text("This is screen 1")

        with dpgr.screen(route_name="screen2"):
            dpg.add_text("This is screen 2")

dpg.show_viewport()
dpg.set_primary_window("_main_window", True)
dpg.start_dearpygui()
dpg.destroy_context()
```

### Function Screens

```python
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

# Create router
router = Router("top")
router.register_screen_function("screen1", screen1, is_initial=True)
router.register_screen_function("screen2", screen2)

with dpg.window(tag="_main_window", label="Router Demo"):
    # Nav Buttons
    with dpg.group(horizontal=True):
        dpg.add_button(label="Go To 1", callback=lambda: router.navigate("screen1"))
        dpg.add_button(label="Go To 2", callback=lambda: router.navigate("screen2"))
    
    # Add router to window
    router.add_to_context()

dpg.show_viewport()
dpg.set_primary_window("_main_window", True)
dpg.start_dearpygui()
dpg.destroy_context()

```

### Class Screens

```python
import dearpygui.dearpygui as dpg
from dearpygui_router import Router

class Screen1:
    def add_to_context(self):
        dpg.add_text("Screen 1")
        dpg.add_button(label="Go To 2", callback=lambda: router.navigate("screen2"))

class Screen2:
    def add_to_context(self):
        dpg.add_text("Screen 2")
        dpg.add_button(label="Go To 1", callback=lambda: router.navigate("screen1"))

dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

# Create router
router = Router("top")
router.register_screen_object("screen1", Screen1(), is_initial=True)
router.register_screen_object("screen2", Screen2())

with dpg.window(tag="_main_window", label="Router Demo"):
    # Nav Buttons
    with dpg.group(horizontal=True):
        dpg.add_button(label="Go To 1", callback=lambda: router.navigate("screen1"))
        dpg.add_button(label="Go To 2", callback=lambda: router.navigate("screen2"))
    
    # Add router to window
    router.add_to_context()

dpg.show_viewport()
dpg.set_primary_window("_main_window", True)
dpg.start_dearpygui()
dpg.destroy_context()
```

## API Overview

`dpgr.router(tag: Optional[str])`  
Creates a router context. All screens defined inside belong to this router.

`dpgr.screen(tag: str)`  
Declares a screen (rendered as a dpg.group). Everything inside is shown/hidden together based on navigation route

`dpgr.navigate(path: str)`  
Switches to the screen at the specified path.  
Nested routes use / to separate levels (e.g., "settings/audio").

### Router Protocol
`dpgr.Router(name: str)`  Create a router instance

- `register(self, route_name: str, screen: ScreenHandler, is_initial=False)`  
- `register_screen_function(self, route_name: str, fn: Callable, is_initial=False)`  
- `register_screen_object(self, route_name: str, obj: Screen, is_initial=False)`  
- `register_screen_item(self, route_name: str, item_tag: Tag, is_initial=False)`  
- `register_screen_factory(self, route_name: str, factory: Callable, is_initial=False)`  
- `navigate(self, route_name: str) -> None`
- `home(self)`  Go back to the initial screen, if one was set.
- `add_to_context(self) -> None` Add this router to the current DPG context. A dpg.child_window will be added.
- `add_nested(self, router: "RouterProtocol") -> None` Add a nested `Router` instance.


## Roadmap

- Optional back stack
- Navigation history
- Lifecycle management
- Route Parameters

## License

MIT License. See LICENSE file for details.