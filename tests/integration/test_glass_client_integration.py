"""Integration tests for the GlassClient against a real Glass server.

These tests are intentionally gated on environment variables so that CI can
skip them when no Glass server is available.
"""

from __future__ import annotations

import os

import pytest


@pytest.mark.integration
class TestGlassClientIntegration:
    async def test_real_glass_smoke(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Smoke-test the three APIs against a real Glass server.

        Required env vars:
        - GLASS_URL
        - GLASS_TEST_REPO_ID
        - GLASS_TEST_PATH
        - GLASS_TEST_SYMBOL_ID
        """

        glass_url = os.environ.get("GLASS_URL")
        repo_id = os.environ.get("GLASS_TEST_REPO_ID")
        path = os.environ.get("GLASS_TEST_PATH")
        symbol_id = os.environ.get("GLASS_TEST_SYMBOL_ID")

        if not (glass_url and repo_id and path and symbol_id):
            pytest.skip(
                "Real Glass integration not configured; set GLASS_URL, "
                "GLASS_TEST_REPO_ID, GLASS_TEST_PATH, and GLASS_TEST_SYMBOL_ID",
            )

        # Ensure settings picks up the environment.
        from app.config import get_settings

        get_settings.cache_clear()
        monkeypatch.setenv("GLASS_URL", glass_url)

        from app.glass.client import GlassClient, GlassClientConfig

        client = GlassClient(config=GlassClientConfig(base_url=glass_url))
        symbols = await client.list_symbols(repo_id, path)
        assert isinstance(symbols, dict)

        desc = await client.describe_symbol(symbol_id)
        assert isinstance(desc, dict)

        refs = await client.find_references(symbol_id)
        assert isinstance(refs, dict)
