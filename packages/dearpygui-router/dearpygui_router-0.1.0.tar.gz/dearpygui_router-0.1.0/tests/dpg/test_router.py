from typing import Callable
from unittest.mock import MagicMock

def test_router_calls_screen_function_on_nav(mock_dpg):
    from dearpygui_router import Router
    
    router = Router("main")
    screen_fn_1 = MagicMock(spec=Callable)
    screen_fn_2 = MagicMock(spec=Callable)
    router.register_screen_function("screen1", screen_fn_1)
    router.register_screen_function("screen2", screen_fn_2)

    router.navigate("screen1")

    screen_fn_1.assert_called_once()
    screen_fn_2.assert_not_called()

def test_router_navigates_to_initial(mock_dpg):
    from dearpygui_router import Router
    
    router = Router("main")
    screen_fn_1 = MagicMock(spec=Callable)
    screen_fn_2 = MagicMock(spec=Callable)
    router.register_screen_function("screen1", screen_fn_1, is_initial=True)
    router.register_screen_function("screen2", screen_fn_2)

    router.add_to_context()

    screen_fn_1.assert_called_once()
    screen_fn_2.assert_not_called()

def test_router_navigates_to_nested(mock_dpg):
    from dearpygui_router import Router
    
    router1 = Router("main")
    router2 = Router("nested")
    screen_fn_1 = MagicMock(spec=Callable)
    router1.register_screen_function("screen1", screen_fn_1, is_initial=True)

    screen_fn_2 = MagicMock(spec=Callable)
    router2.register_screen_function("screen2", screen_fn_2)
    router1.add_nested(router2)

    router1.navigate("screen1")
    screen_fn_1.assert_called_once()
    screen_fn_2.assert_not_called()

    router1.navigate("screen1/screen2")
    screen_fn_1.assert_called()
    screen_fn_2.assert_called_once()
