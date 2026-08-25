"""DEF-008: SPA document navigations vs same-origin API paths."""

from app.spa_serve import spa_shell_allowed, wants_spa_document


def test_browser_refresh_wants_spa():
    assert (
        wants_spa_document(
            method="GET",
            headers={
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "accept": "text/html,application/xhtml+xml",
            },
        )
        is True
    )


def test_spa_fetch_keeps_api():
    assert (
        wants_spa_document(
            method="GET",
            headers={
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "accept": "application/json",
            },
        )
        is False
    )


def test_accept_html_without_sec_fetch_still_spa():
    assert (
        wants_spa_document(
            method="GET",
            headers={"accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8"},
        )
        is True
    )


def test_shell_skips_docs_and_health():
    assert spa_shell_allowed("/notifications") is True
    assert spa_shell_allowed("/arenas") is True
    assert spa_shell_allowed("/messages") is True
    assert spa_shell_allowed("/health") is False
    assert spa_shell_allowed("/docs") is False
    assert spa_shell_allowed("/assets/index.js") is False
    assert spa_shell_allowed("/ops") is False
    assert spa_shell_allowed("/ops/config") is False
    assert spa_shell_allowed("/public") is False
    assert spa_shell_allowed("/public/config") is False
