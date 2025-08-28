import logging

# Set up a logger for my code to use
LOGGER = logging.getLogger("mkdocs.plugins.anti_ai_scraper")

import os
# pip dependency
from mkdocs.config.config_options import Type
from mkdocs.plugins import BasePlugin
from mkdocs.config.base import Config
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.pages import Page
from mkdocs.structure.files import Files
from mkdocs.exceptions import PluginError


class AntiScraperPluginConfig(Config):
    robots_txt = Type(bool, default=True)


class AntiScraperPlugin(BasePlugin[AntiScraperPluginConfig]):
    def on_config(self, config: MkDocsConfig, **kwargs) -> MkDocsConfig:
        """
        Called once when the config is loaded.
        It will make modify the config and initialize this plugin.
        """
        
        return config

    # @event_priority(50)
    # Earlier than most other plugins to update the tags properly. Did not work
    # SEE https://www.mkdocs.org/dev-guide/plugins/#event-priorities
    def on_page_markdown(self, markdown: str, page: Page, config: MkDocsConfig, files: Files) -> str:
        """
        The page_markdown event is called after the page's markdown is loaded from file and can be used to alter the Markdown source text. The meta- data has been stripped off and is available as page.meta at this point.
        See: https://www.mkdocs.org/dev-guide/plugins/#on_page_markdown
        """
        
        return markdown

    def on_post_build(self, config: MkDocsConfig) -> None:
        """
        Add a robots.txt if the user wants it
        """
        if self.config.robots_txt:
            robots_path = os.path.join(config.site_dir, "robots.txt")
            if not os.path.exists(robots_path):
                with open(robots_path, "w") as f:
                    f.write("User-agent: *\nDisallow: /\n")

