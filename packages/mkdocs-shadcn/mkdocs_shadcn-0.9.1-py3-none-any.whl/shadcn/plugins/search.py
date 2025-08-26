import re
from typing import Set, Union

from git import Repo
from mkdocs.config import Config
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.contrib.search import SearchPlugin as BaseSearchPlugin
from mkdocs.structure.files import Files
from mkdocs.structure.nav import Navigation, Section
from mkdocs.structure.pages import Page

from shadcn.filters import (
    active_section,
    first_page,
    iconify,
    parse_author,
    setattribute,
)


def find_repo(abs_src_file: str) -> Union[Repo, None]:
    """
    Find the git repository for the given source file.
    Returns None if no repository is found.
    """
    try:
        return Repo(abs_src_file, search_parent_directories=True)
    except Exception:
        print(f"Could not find git repository starting from {abs_src_file}")
        return None


class SearchPlugin(BaseSearchPlugin):
    """⚠️ HACK ⚠️
    Custom plugin. As search is loaded by default, we subclass it so as
    to inject what we want (and without adding a list of additional plugins)
    """

    page_index = 0
    """Internal page index for orderning purpose"""
    page_indices: Set[int] = set()
    """Internal set of pages that have hard-coded order"""

    def on_startup(self, *, command, dirty):
        self.is_dev_server = command == "serve"

    def configure_mkdocstrings(self, config: MkDocsConfig, **kwargs):
        mkdocstrings_config = {
            "handlers": {
                "python": {
                    "options": {
                        "show_root_heading": True,
                    }
                },
            },
            "default_handler": "python",
        }

        plugin = config["plugins"].get("mkdocstrings", None)

        if plugin:
            options = (
                plugin.config.get("handlers", {})
                .get("python", {})
                .get("options", {})
            )
            show_root_heading = options.get("show_root_heading", None)
            if show_root_heading is None:
                plugin.config.update(mkdocstrings_config)

    def on_config(self, config: MkDocsConfig, **kwargs):
        """Called when the config is loaded.

        Attributes:
            config (dict): The MkDocs configuration dictionary.

        """
        # dev server detection
        config["is_dev_server"] = self.is_dev_server
        config["git_repository"] = find_repo(config.config_file_path)

        # mkdocstrings configuration
        self.configure_mkdocstrings(config, **kwargs)

        return super().on_config(config, **kwargs)

    def on_env(self, env, /, *, config: MkDocsConfig, files: Files):
        # custom jinja2 filter
        env.filters["setattribute"] = setattribute
        env.filters["iconify"] = iconify
        env.filters["parse_author"] = parse_author
        env.filters["active_section"] = active_section
        env.filters["first_page"] = first_page
        # add custom global variables
        env.globals["is_dev_server"] = self.is_dev_server
        return env

    def on_nav(
        self, nav: Navigation, /, *, config: Config, files: Files
    ) -> Navigation:
        # if we create folders with 00_name_of_the_folder we remove the prepended number
        # from the title. It is a common hack to have the folders ordered in the navigation
        rex = re.compile(r"^[0-9]+[ _]")
        for item in nav.items:
            if isinstance(item, Section) and rex.match(item.title):
                item.title = rex.sub("", item.title).capitalize()
        return nav

    def on_page_markdown(
        self,
        markdown: str,
        /,
        *,
        page: Page,
        config: MkDocsConfig,
        files: Files,
    ):
        # add git timestamps to page metadata
        repo = config.get("git_repository", None)
        if isinstance(repo, Repo) and page.file.abs_src_path:
            dates = [
                commit.committed_datetime
                for commit in repo.iter_commits(paths=page.file.abs_src_path)
            ]
            if len(dates) > 0:
                page.meta["created_at"] = dates[-1]
                page.meta["updated_at"] = dates[0]

        # add order to page if not defined
        page.meta["order"] = page.meta.get("order", self.page_index)
        self.page_indices.add(self.page_index)
        # increment page index
        while self.page_index in self.page_indices:
            self.page_index += 1

        # remove first plain h1 if provided
        markdown = re.sub(r"^#\s+(.+)", r"", markdown, count=1)
        return markdown
