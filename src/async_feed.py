"""Async helpers for feed loading and persistent storage."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

import aiofiles
import aiohttp
import feedparser


class AsyncFeedLoader:
    """Loads RSS/Atom feeds asynchronously."""

    def __init__(self, timeout: int = 15) -> None:
        self.timeout = aiohttp.ClientTimeout(total=timeout)

    async def load_feed(self, url: str) -> dict:
        """Fetch and parse a feed, raising clear exceptions on failure."""
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"HTTP {resp.status}: {resp.reason}")
                text = await resp.text()

        feed = feedparser.parse(text)

        if feed.bozo and getattr(feed, "bozo_exception", None):
            raise RuntimeError(f"Parse error: {feed.bozo_exception}")

        return feed


class AsyncFileHandler:
    """Handles persistent JSON storage in ~/.config/rss-feed-tui."""

    @staticmethod
    def _config_dir() -> Path:
        path = Path.home() / ".config" / "rss-feed-tui"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def _feeds_path() -> Path:
        return AsyncFileHandler._config_dir() / "feeds.json"

    @staticmethod
    def _discover_path() -> Path:
        return AsyncFileHandler._config_dir() / "discover.json"

    @staticmethod
    async def load_feeds() -> Dict[str, str]:
        path = AsyncFileHandler._feeds_path()
        if not path.exists():
            return {}
        async with aiofiles.open(path, "r", encoding="utf-8") as f:
            content = await f.read()
            return json.loads(content)

    @staticmethod
    async def save_feeds(feeds: Dict[str, str]) -> None:
        path = AsyncFileHandler._feeds_path()
        async with aiofiles.open(path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(feeds, indent=4, ensure_ascii=False))

    @staticmethod
    async def load_discover_feeds() -> Dict[str, str]:
        path = AsyncFileHandler._discover_path()
        if not path.exists():
            await AsyncFileHandler._create_default_discover()
        async with aiofiles.open(path, "r", encoding="utf-8") as f:
            content = await f.read()
            return json.loads(content)

    @staticmethod
    async def _create_default_discover() -> None:
        default = {
            "Hacker News": "https://hnrss.org/frontpage",
            "Reddit Python": "https://www.reddit.com/r/Python/.rss",
            "BBC News": "http://feeds.bbci.co.uk/news/rss.xml",
            "Engadget": "https://www.engadget.com/rss.xml",
            "The Verge": "https://www.theverge.com/rss/index.xml",
            "Wired": "https://www.wired.com/feed/rss",
            "TechCrunch": "https://techcrunch.com/feed/",
            "NYT World": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        }
        path = AsyncFileHandler._discover_path()
        async with aiofiles.open(path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(default, indent=4, ensure_ascii=False))
