import logging
import subprocess
# pip install self-unzip-html
import self_unzip_html

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
    sitemap_xml = Type(bool, default=True)
    encode_html = Type(bool, default=True)
    debug = Type(bool, default=False)


class AntiScraperPlugin(BasePlugin[AntiScraperPluginConfig]):
    def on_config(self, config: MkDocsConfig, **kwargs) -> MkDocsConfig:
        """
        Called once when the config is loaded.
        It will make modify the config and initialize this plugin.
        """
        
        return config
    
    def debug(self, message: str) -> None:
        if self.config.debug:
            LOGGER.info(f"[anti-ai-scraper] {message}")

    # @event_priority(-90)
    # Later than most other plugins to update the tags properly. Did not work
    # SEE https://www.mkdocs.org/dev-guide/plugins/#event-priorities
    def on_post_page(self, html: str, page: Page, config: MkDocsConfig) -> str:
        """
        The post_page event is called after the template is rendered, but before it is written to disc and can be used to alter the output of the page. If an empty string is returned, the page is skipped and nothing is written to disc.
        See: https://www.mkdocs.org/dev-guide/plugins/#on_post_page
        """
        try:
            # @TODO: expose this in self-unzip-html library to not have to call a separate process
            html = subprocess.check_output(["self-unzip-html", "-c", "gzip", "-e", "ascii85", "--replace", "-"], stderr=subprocess.DEVNULL, input=html.encode()).decode()
        except Exception as ex:
            logging.warning(f"Failed to call self-unzip-html: {ex}")
        return html
    
    def on_post_build(self, config: MkDocsConfig) -> None:
        """
        Add a robots.txt if the user wants it
        """
        if self.config.robots_txt:
            robots_path = os.path.join(config.site_dir, "robots.txt")
            if not os.path.exists(robots_path):
                with open(robots_path, "w") as f:
                    f.write("User-agent: *\nDisallow: /\n")
                self.debug(f"Created {robots_path}")
            else:
                self.debug(f"File {robots_path} already exists, skipped creating it")
        
        if self.config.sitemap_xml:
            for file_name in ["sitemap.xml", "sitemap.xml.gz"]:
                file_path = os.path.join(config.site_dir, file_name)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    self.debug(f"Removed {file_path}")
                else:
                    self.debug(f"Skipped removing {file_path}, since it does not exist")

