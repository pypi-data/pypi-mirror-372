from typing import List

from dearpygui_router.types import RouterProtocol

_ROUTER_STACK: List[RouterProtocol] = []

def push_router(router: RouterProtocol):
    _ROUTER_STACK.append(router)

def pop_router() -> RouterProtocol:
    return _ROUTER_STACK.pop()

def top_router() -> RouterProtocol:
    if not _ROUTER_STACK:
        return None
    return _ROUTER_STACK[-1]