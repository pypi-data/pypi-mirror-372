import sys
import types
import pytest
from unittest.mock import MagicMock
from itertools import count

_id_generator = count(1)
def generate_uuid():
    return next(_id_generator)

@pytest.fixture(autouse=True)
def mock_dpg(monkeypatch):
    assert "dearpygui.dearpygui" not in sys.modules, "DPG was imported too early!"
    fake_dpg = MagicMock()
    fake_dpg.generate_uuid = MagicMock(side_effect=generate_uuid)

    # Insert fake module before import happens
    monkeypatch.setitem(sys.modules, "dearpygui", types.SimpleNamespace(dearpygui=fake_dpg))
    monkeypatch.setitem(sys.modules, "dearpygui.dearpygui", fake_dpg)

    yield fake_dpg
