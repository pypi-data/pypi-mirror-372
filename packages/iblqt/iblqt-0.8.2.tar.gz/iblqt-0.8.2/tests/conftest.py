"""General use fixtures for pytest."""

import builtins

import pytest


@pytest.fixture
def missing_module(monkeypatch):
    """Temporarily makes a module unavailable during a test."""
    real_import = builtins.__import__
    blocked_modules = set()

    def _missing(module_name: str):
        blocked_modules.add(module_name)

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        for mod in blocked_modules:
            if name == mod or name.startswith(mod + '.'):
                raise ModuleNotFoundError(f"No module named '{name}'")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, '__import__', fake_import)
    yield _missing
