"""Main application module for rss-feed-tui."""

from __future__ import annotations

import html
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, List

import html2text
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Center, Horizontal, Vertical, VerticalScroll
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Input, Static

from async_feed import AsyncFeedLoader, AsyncFileHandler

# =============================================================================
# HTML Cleaning Utilities
# =============================================================================


def _is_html_content(content: str | None) -> bool:
    """Check if content likely contains HTML tags."""
    if not content:
        return False
    return bool(re.search(r"<[^>]+>", content))


class _SimpleHTMLParser(HTMLParser):
    """Minimal fallback parser for basic HTML cleanup."""

    def __init__(self) -> None:
        super().__init__()
        self.text: List[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"br", "p"}:
            self.text.append("\n")
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.text.append("\n## ")
        elif tag == "a":
            for attr, value in attrs:
                if attr == "href" and value:
                    self.text.append("[")
                    break

    def handle_endtag(self, tag: str) -> None:
        if tag == "a":
            self.text.append("]")
        elif tag in {"p", "div"}:
            self.text.append("\n")

    def handle_data(self, data: str) -> None:
        stripped = data.strip()
        if stripped:
            self.text.append(stripped)

    def get_text(self) -> str:
        return "".join(self.text)


def clean_html_content(content: str | None) -> str:
    """Convert HTML content to clean readable text."""
    if not content:
        return "No content available."

    if not _is_html_content(content):
        return content.strip()

    try:
        h = html2text.HTML2Text()
        h.ignore_links = True
        h.ignore_images = True
        h.ignore_tables = True
        h.body_width = 0

        cleaned = h.handle(content)
        cleaned = re.sub(r"\[/?[^\]]*\]", "", cleaned)  # remove leftover markdown
        cleaned = re.sub(r"\n\s*\n", "\n\n", cleaned)  # normalize paragraphs
        cleaned = re.sub(r" +", " ", cleaned)  # collapse spaces
        return cleaned.strip()
    except Exception:
        # Fallback: strip tags manually
        parser = _SimpleHTMLParser()
        parser.feed(content)
        return html.unescape(parser.get_text()).strip()


# =============================================================================
# Sidebar
# =============================================================================


class Sidebar(Vertical):
    """Left sidebar with feed list and management buttons."""

    feed_data: reactive[Dict[str, str]] = reactive(dict)

    class FeedSelected(Message):
        """Message posted when a feed is selected."""

        def __init__(self, title: str) -> None:
            self.title = title
            super().__init__()

    class ModeSelected(Message):
        """Message posted when a management mode is selected."""

        def __init__(self, mode: str) -> None:  # "add" | "manage" | "discover"
            self.mode = mode
            super().__init__()

    async def on_mount(self) -> None:
        await self._refresh_feeds()

    async def _refresh_feeds(self) -> None:
        try:
            self.feed_data = await AsyncFileHandler.load_feeds()
        except Exception:
            self.feed_data = {}

    def compose(self) -> ComposeResult:
        yield Static("RSS Feeds", classes="sidebar-title")
        yield Center(Button("Add feed", id="add-feed", classes="action-btn"))
        yield Center(Button("Manage feeds", id="manage-feeds", classes="action-btn"))
        yield Center(
            Button("Discover feeds", id="discover-feeds", classes="action-btn")
        )

    async def watch_feed_data(self, feeds: Dict[str, str]) -> None:
        """Dynamically update feed buttons when feed_data changes."""
        for node in self.query(".feed-btn, .no-feeds-message"):
            await node.remove()

        if not feeds:
            await self.mount(
                Static("No feeds yet – add one!", classes="no-feeds-message"),
                before="#add-feed",
            )
            return

        for title in feeds:
            safe_id = title.replace(" ", "_").translate(
                str.maketrans("/.`'\"", "_____")
            )
            await self.mount(
                Button(title, id=f"feed-{safe_id}", classes="feed-btn"),
                before="#add-feed",
            )

    @on(Button.Pressed)
    def _handle_button_press(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""

        if button_id.startswith("feed-"):
            title = event.button.label.plain if event.button.label else ""
            if title in self.feed_data:
                self.post_message(self.FeedSelected(title))

        elif button_id == "add-feed":
            self.post_message(self.ModeSelected("add"))
        elif button_id == "manage-feeds":
            self.post_message(self.ModeSelected("manage"))
        elif button_id == "discover-feeds":
            self.post_message(self.ModeSelected("discover"))


# =============================================================================
# Main Content Area
# =============================================================================


class MainContent(VerticalScroll):
    """Central area showing welcome, feed articles, or management screens."""

    class FeedsChanged(Message):
        """Notify sidebar that feeds were modified."""

        pass

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.loader = AsyncFeedLoader()
        self.current_feed_title: str | None = None
        self.current_entries: List[Dict[str, Any]] = []

    def compose(self) -> ComposeResult:
        yield Vertical(id="content")

    # -------------------------------------------------------------------------
    # Screen Display Methods
    # -------------------------------------------------------------------------

    def show_welcome(self) -> None:
        self._clear_content()
        self.query_one("#content").mount(
            Static(
                r"""
$$$$$$$\   $$$$$$\   $$$$$$\      $$$$$$$$\ $$\   $$\ $$$$$$\ 
$$  __$$\ $$  __$$\ $$  __$$\     \__$$  __|$$ |  $$ |\_$$  _|
$$ |  $$ |$$ /  \__|$$ /  \__|       $$ |   $$ |  $$ |  $$ |  
$$$$$$$  |\$$$$$$\  \$$$$$$\ $$$$$$\ $$ |   $$ |  $$ |  $$ |  
$$  __$$<  \____$$\  \____$$\\______|$$ |   $$ |  $$ |  $$ |  
$$ |  $$ |$$\   $$ |$$\   $$ |       $$ |   $$ |  $$ |  $$ |  
$$ |  $$ |\$$$$$$  |\$$$$$$  |       $$ |   \$$$$$$  |$$$$$$\ 
\__|  \__| \______/  \______/        \__|    \______/ \______|
                                                              


A clean, modern terminal RSS reader.

→ Select a feed from the sidebar
→ Use 'Add feed' to include your own sources
→ Enjoy reading!

""",
                classes="welcome",
            )
        )

    async def show_feed(self, title: str) -> None:
        self._clear_content()
        self.current_feed_title = title
        self.current_entries = []

        container = self.query_one("#content")

        header = Horizontal(classes="feed-header-root")
        await container.mount(header)

        left_part = Vertical(
            Static(f"📻 {title}", classes="feed-title-big"),
            Static("Click article to read →", classes="feed-hint"),
            Static("↑↓ - navigation, • Enter - open • q - exit", classes="feed-hint"),
            classes="feed-info-left",
        )

        search_part = Vertical(
            # Horizontal(
            #     Static(f"Feed: {title}", classes="feed-title"),
            # ),
            Horizontal(
                Input(placeholder="Search articles…", id="search-input"),
                Button("Search", id="search-btn", classes="search-btn"),
                classes="search-box",
            ),
            classes="feed-header-right",
        )

        await header.mount(left_part)
        await header.mount(search_part)

        articles_area = VerticalScroll(classes="articles-list")
        container.mount(articles_area)
        articles_area.mount(Static("Loading feed…", classes="loading"))

        try:
            feed = await self.loader.load_feed(
                (await AsyncFileHandler.load_feeds())[title]
            )
            await articles_area.query_one(".loading").remove()

            entries = feed.get("entries", [])
            self.current_entries = entries

            for idx, entry in enumerate(entries):
                articles_area.mount(
                    Button(
                        entry.get("title", "Untitled"),
                        id=f"article-{idx}",
                        classes="article-btn",
                    )
                )
        except Exception as exc:
            await articles_area.query_one(".loading").remove()
            articles_area.mount(Static(f"Error loading feed: {exc}", classes="error"))

    def show_article(self, index: int) -> None:
        self._clear_content()
        container = self.query_one("#content")

        if index >= len(self.current_entries):
            container.mount(Static("Article not found.", classes="error"))
            return

        entry = self.current_entries[index]

        container.mount(Button("← Back to feed", id="back-btn", classes="back-btn"))

        if title := entry.get("title"):
            container.mount(Static(title, classes="article-title"))

        # Extract content
        content = ""
        for key in ("summary", "description", "content"):
            if raw := entry.get(key):
                if isinstance(raw, list) and raw:
                    content = raw[0].get("value", "")
                else:
                    content = str(raw)
                break

        cleaned = clean_html_content(content)
        container.mount(VerticalScroll(Static(cleaned, classes="article-content")))

        if link := entry.get("link"):
            container.mount(Static(f"\nFull article: {link}", classes="article-link"))

        meta = []
        if author := entry.get("author"):
            meta.append(f"By {author}")
        if published := entry.get("published"):
            meta.append(f"Published {published}")
        if meta:
            container.mount(Static(" • ".join(meta), classes="article-meta"))

    def show_add_feed(self) -> None:
        self._clear_content()
        container = self.query_one("#content")
        container.mount(Static("Add New Feed", classes="section-title"))
        container.mount(
            Input(placeholder="Feed name (e.g. Hacker News)", id="name-input")
        )
        container.mount(
            Input(placeholder="https://example.com/feed.xml", id="url-input")
        )
        container.mount(Button("Add Feed", id="submit-add", classes="primary-btn"))

    async def show_manage_feeds(self) -> None:
        self._clear_content()
        container = self.query_one("#content")
        container.mount(Static("Manage Feeds", classes="section-title"))

        feeds = await AsyncFileHandler.load_feeds()
        if not feeds:
            container.mount(Static("No feeds added yet.", classes="info"))
            return

        list_area = VerticalScroll(classes="manage-list")
        container.mount(list_area)

        for idx, (name, url) in enumerate(feeds.items()):
            list_area.mount(
                Horizontal(
                    Vertical(
                        Static(name, classes="manage-name"),
                        Static(url, classes="manage-url"),
                    ),
                    Button("Delete", id=f"delete-{idx}", classes="delete-btn"),
                    classes="manage-row",
                )
            )

    async def show_discover_feeds(self) -> None:
        self._clear_content()
        container = self.query_one("#content")
        container.mount(Static("Discover Popular Feeds", classes="section-title"))

        discover = await AsyncFileHandler.load_discover_feeds()
        if not discover:
            container.mount(Static("No discover list available.", classes="error"))
            return

        list_area = VerticalScroll(classes="discover-list")
        container.mount(list_area)

        for idx, (name, url) in enumerate(discover.items()):
            list_area.mount(
                Horizontal(
                    Vertical(
                        Static(name, classes="discover-name"),
                        Static(url, classes="discover-url"),
                    ),
                    Button("Add", id=f"discover-add-{idx}", classes="add-discover-btn"),
                    classes="discover-row",
                )
            )

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _clear_content(self) -> None:
        container = self.query_one("#content")
        for child in list(container.children):
            child.remove()

    # -------------------------------------------------------------------------
    # Event Handlers
    # -------------------------------------------------------------------------

    @on(Button.Pressed)
    async def _handle_buttons(self, event: Button.Pressed) -> None:
        btn_id = event.button.id or ""

        if btn_id == "back-btn" and self.current_feed_title:
            await self.show_feed(self.current_feed_title)

        elif btn_id == "submit-add":
            name = self.query_one("#name-input").value.strip()
            url = self.query_one("#url-input").value.strip()
            if not name or not url:
                return
            if not url.startswith(("http://", "https://")):
                self.query_one("#content").mount(
                    Static("URL must start with http:// or https://", classes="error")
                )
                return

            feeds = await AsyncFileHandler.load_feeds()
            feeds[name] = url
            await AsyncFileHandler.save_feeds(feeds)
            self.post_message(self.FeedsChanged())
            self.show_welcome()

        elif btn_id.startswith("article-"):
            idx = int(btn_id.split("-")[-1])
            self.show_article(idx)

        elif btn_id.startswith("delete-"):
            idx = int(btn_id.split("-")[-1])
            feeds = await AsyncFileHandler.load_feeds()

            keys = list(feeds.keys())
            if 0 <= idx < len(keys):
                feeds.pop(keys[idx])
                await AsyncFileHandler.save_feeds(feeds)
                self.post_message(self.FeedsChanged())
                await self.show_manage_feeds()

        elif btn_id.startswith("discover-add-"):
            idx = int(btn_id.split("-")[-1])
            discover = await AsyncFileHandler.load_discover_feeds()
            name, url = list(discover.items())[idx]
            feeds = await AsyncFileHandler.load_feeds()
            feeds[name] = url
            await AsyncFileHandler.save_feeds(feeds)
            self.post_message(self.FeedsChanged())
            await self.show_discover_feeds()

        elif btn_id == "search-btn":
            query = self.query_one("#search-input").value.lower()
            await self._filter_articles(query)

    async def _filter_articles(self, query: str) -> None:
        articles_area = self.query_one(".articles-list")
        for child in list(articles_area.children):
            await child.remove()

        for idx, entry in enumerate(self.current_entries):
            if query in entry.get("title", "").lower():
                articles_area.mount(
                    Button(
                        entry.get("title", "Untitled"),
                        id=f"article-{idx}",
                        classes="article-btn",
                    )
                )


# =============================================================================
# Main App
# =============================================================================


class RssFeedTUI(App):
    """Main application class."""

    CSS_PATH = Path(__file__).parent / "styles" / "app.tcss"

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit"),
        ("h", "go_home", "Home"),
        ("slash", "focus_search", "Focus search"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Horizontal(Sidebar(id="sidebar"), MainContent(id="main-content"))
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(MainContent).show_welcome()
        self.add_class("light")

    @on(Sidebar.FeedSelected)
    async def _on_feed_selected(self, message: Sidebar.FeedSelected) -> None:
        await self.query_one(MainContent).show_feed(message.title)

    @on(Sidebar.ModeSelected)
    async def _on_mode_selected(self, message: Sidebar.ModeSelected) -> None:
        content = self.query_one(MainContent)
        if message.mode == "add":
            content.show_add_feed()
        elif message.mode == "manage":
            await content.show_manage_feeds()
        elif message.mode == "discover":
            await content.show_discover_feeds()

    @on(MainContent.FeedsChanged)
    async def _on_feeds_changed(self) -> None:
        await self.query_one(Sidebar)._refresh_feeds()

    def action_toggle_dark(self) -> None:
        self.toggle_class("dark")

    def action_go_home(self) -> None:
        self.query_one(MainContent).show_welcome()

    def action_focus_search(self) -> None:
        """Фокус на поле поиска по клавише /"""
        try:
            search_input = self.query_one("#search-input", Input)
            search_input.focus()
        except:
            pass


def main() -> None:
    RssFeedTUI().run()


if __name__ == "__main__":
    main()
