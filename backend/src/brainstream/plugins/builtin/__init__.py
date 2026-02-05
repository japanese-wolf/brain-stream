"""Built-in data source plugins."""

from brainstream.plugins.builtin.anthropic_changelog import AnthropicChangelogPlugin
from brainstream.plugins.builtin.aws_whatsnew import AWSWhatsNewPlugin
from brainstream.plugins.builtin.gcp_release_notes import GCPReleaseNotesPlugin
from brainstream.plugins.builtin.github_releases import GitHubReleasesPlugin
from brainstream.plugins.builtin.openai_changelog import OpenAIChangelogPlugin

__all__ = [
    "AWSWhatsNewPlugin",
    "GCPReleaseNotesPlugin",
    "OpenAIChangelogPlugin",
    "AnthropicChangelogPlugin",
    "GitHubReleasesPlugin",
]
