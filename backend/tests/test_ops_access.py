"""Ops access helpers (no DB)."""

import os

from app.ops_access import is_ops_owner_username, ops_console_path, ops_owner_usernames


def test_default_owner_is_sharath(monkeypatch):
    monkeypatch.delenv("OPS_OWNER_USERNAMES", raising=False)
    assert ops_owner_usernames() == {"sharath"}
    assert is_ops_owner_username("sharath")
    assert is_ops_owner_username("SHARATH")
    assert not is_ops_owner_username("testits")


def test_owner_env_override(monkeypatch):
    monkeypatch.setenv("OPS_OWNER_USERNAMES", "testits, sharath")
    assert ops_owner_usernames() == {"testits", "sharath"}
    assert is_ops_owner_username("testits")


def test_console_path(monkeypatch):
    monkeypatch.delenv("OPS_CONSOLE_PATH", raising=False)
    assert ops_console_path() == "/bx-ops"
    monkeypatch.setenv("OPS_CONSOLE_PATH", "hq-9f3k-console")
    assert ops_console_path() == "/hq-9f3k-console"
    monkeypatch.setenv("OPS_CONSOLE_PATH", "/admin")
    assert ops_console_path() == "/bx-ops"
