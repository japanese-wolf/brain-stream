"""Tests for AWS What's New plugin."""

import pytest
from datetime import datetime, timezone

from brainstream.plugins.builtin.aws_whatsnew import AWSWhatsNewPlugin
from brainstream.plugins.base import SourceType


class TestAWSWhatsNewPlugin:
    """Test suite for AWS What's New plugin."""

    def test_plugin_info(self):
        """Test that plugin info is correctly defined."""
        plugin = AWSWhatsNewPlugin()
        info = plugin.info

        assert info.name == "aws-whatsnew"
        assert info.vendor == "AWS"
        assert info.source_type == SourceType.RSS
        assert "lambda" in info.supported_tech_stack

    def test_validate_config(self):
        """Test configuration validation."""
        plugin = AWSWhatsNewPlugin()
        assert plugin.validate_config() is True

    @pytest.mark.asyncio
    async def test_fetch_updates(self):
        """Test fetching updates from live RSS feed."""
        plugin = AWSWhatsNewPlugin()
        articles = await plugin.fetch_updates()

        # Should return some articles
        assert len(articles) > 0

        # Check first article structure
        article = articles[0]
        assert article.vendor == "AWS"
        assert article.primary_source_url.startswith("http")
        assert article.original_title != ""
        assert article.external_id != ""

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check."""
        plugin = AWSWhatsNewPlugin()
        is_healthy = await plugin.health_check()
        assert is_healthy is True
