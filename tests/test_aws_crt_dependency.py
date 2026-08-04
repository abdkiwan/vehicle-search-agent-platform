"""Ensure botocore CRT is available for AWS login credential provider."""

from __future__ import annotations

from pathlib import Path


REQUIREMENTS = Path(__file__).resolve().parents[1] / "requirements.txt"


def test_requirements_declares_botocore_crt() -> None:
    contents = REQUIREMENTS.read_text(encoding="utf-8")
    assert 'botocore[crt]' in contents


def test_awscrt_is_importable() -> None:
    import awscrt  # noqa: F401


def test_botocore_reports_crt_available() -> None:
    from botocore.compat import HAS_CRT

    assert HAS_CRT is True
