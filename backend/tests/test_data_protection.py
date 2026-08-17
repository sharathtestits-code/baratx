"""Tests for India DPDP data-protection helpers."""

from app import data_protection


def test_notice_version_set():
    assert data_protection.PRIVACY_NOTICE_VERSION.startswith("2026")
    assert "dpdp" in data_protection.PRIVACY_NOTICE_VERSION


def test_grievance_contacts():
    assert "@barathx.com" in data_protection.GRIEVANCE_EMAIL
    assert data_protection.GRIEVANCE_RESPONSE_DAYS <= 90
