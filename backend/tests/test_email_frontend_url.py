"""FRONTEND_URL hardening for verify/reset emails (DEF-001)."""

import importlib
import os


def _reload_email(env: dict):
    for key in (
        "ENVIRONMENT",
        "FRONTEND_URL",
        "CORS_ORIGINS",
        "RAILWAY_ENVIRONMENT",
        "RAILWAY_SERVICE_NAME",
        "RAILWAY_PROJECT_NAME",
        "RAILWAY_ENVIRONMENT_NAME",
    ):
        os.environ.pop(key, None)
    os.environ.update(env)
    import app.email as email_mod

    return importlib.reload(email_mod)


def test_qa_rewrites_production_railway_frontend_url():
    mod = _reload_email(
        {
            "ENVIRONMENT": "qa",
            "FRONTEND_URL": "https://baratx-production-f8ce.up.railway.app",
        }
    )
    assert mod.FRONTEND_URL == "https://qa.barathx.com"
    assert "qa.barathx.com" in mod.build_reset_url("tok")


def test_qa_detected_via_cors_even_if_environment_production():
    mod = _reload_email(
        {
            "ENVIRONMENT": "production",
            "FRONTEND_URL": "https://baratx-production.up.railway.app",
            "CORS_ORIGINS": "https://qa.barathx.com",
        }
    )
    assert mod.FRONTEND_URL == "https://qa.barathx.com"


def test_production_rewrites_railway_to_public_web():
    mod = _reload_email(
        {
            "ENVIRONMENT": "production",
            "FRONTEND_URL": "https://baratx-production.up.railway.app",
            "CORS_ORIGINS": "https://barathx.com",
        }
    )
    assert mod.FRONTEND_URL == "https://barathx.com"


def test_dev_keeps_localhost():
    mod = _reload_email(
        {
            "ENVIRONMENT": "development",
            "FRONTEND_URL": "http://localhost:5173",
        }
    )
    assert mod.FRONTEND_URL == "http://localhost:5173"
