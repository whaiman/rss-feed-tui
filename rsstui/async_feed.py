import aiohttp
import asyncio
import feedparser
import json
import aiofiles
import os
from pathlib import Path
from typing import Dict, Any, Optional

class AsyncFeedLoader:
    def __init__(self, timeout: int = 10):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
    
    async def load_feed(self, url: str) -> Optional[Dict[str, Any]]:
        """Load RSS feed asynchronously"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        raise Exception(f"HTTP {response.status}: {response.reason}")
                    
                    content = await response.text()
                    loop = asyncio.get_event_loop()
                    feed = await loop.run_in_executor(None, feedparser.parse, content)
                    
                    if feed.bozo and hasattr(feed, 'bozo_exception'):
                        raise Exception(f"Feed parsing error: {feed.bozo_exception}")
                    
                    return feed
                    
        except asyncio.TimeoutError:
            raise Exception("Feed loading timeout")
        except aiohttp.ClientError as e:
            raise Exception(f"Network error: {e}")
        except Exception as e:
            raise Exception(f"Failed to load feed: {e}")


class AsyncFileHandler:
    """Async file operations for feeds.json"""
    
    @staticmethod
    def _get_config_dir() -> Path:
        """Get the configuration directory for RssTUI"""
        config_dir = Path.home() / ".config" / "rsstui"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
    
    @staticmethod
    def _get_feeds_file() -> Path:
        """Get the feeds.json file path"""
        return AsyncFileHandler._get_config_dir() / "feeds.json"
    
    @staticmethod
    def _get_discover_file() -> Path:
        """Get the discover.json file path"""
        return AsyncFileHandler._get_config_dir() / "discover.json"
    
    @staticmethod
    async def load_feeds() -> Dict[str, str]:
        """Load feeds from feeds.json asynchronously"""
        feeds_file = AsyncFileHandler._get_feeds_file()
        try:
            async with aiofiles.open(feeds_file, "r") as f:
                content = await f.read()
                return json.loads(content)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            raise Exception("Invalid feeds.json format")
    
    @staticmethod
    async def save_feeds(feeds: Dict[str, str]) -> None:
        """Save feeds to feeds.json asynchronously"""
        feeds_file = AsyncFileHandler._get_feeds_file()
        async with aiofiles.open(feeds_file, "w") as f:
            await f.write(json.dumps(feeds, indent=4))
    
    @staticmethod
    async def load_discover_feeds() -> Dict[str, str]:
        """Load discover feeds asynchronously"""
        discover_file = AsyncFileHandler._get_discover_file()
        try:
            async with aiofiles.open(discover_file, "r") as f:
                content = await f.read()
                return json.loads(content)
        except FileNotFoundError:
            # Create default discover feeds if file doesn't exist
            await AsyncFileHandler._create_default_discover_feeds()
            async with aiofiles.open(discover_file, "r") as f:
                content = await f.read()
                return json.loads(content)
        except json.JSONDecodeError:
            raise Exception("Invalid discover.json format")
    
    @staticmethod
    async def _create_default_discover_feeds() -> None:
        """Create default discover feeds file"""
        default_feeds = {
            "Hacker News": "https://feeds.feedburner.com/oreilly/radar",
            "Wired": "https://www.wired.com/feed/rss",
            "Reddit Python": "https://www.reddit.com/r/Python/.rss",
            "BBC News": "http://feeds.bbci.co.uk/news/rss.xml",
            "TechCrunch": "https://techcrunch.com/feed/"
        }
        discover_file = AsyncFileHandler._get_discover_file()
        async with aiofiles.open(discover_file, "w") as f:
            await f.write(json.dumps(default_feeds, indent=4))
