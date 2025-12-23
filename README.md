# rss-feed-tui

A modern, terminal-based RSS reader built with [Textual](https://textual.textualize.io/).  
This is a fork of the original [RssTUI](https://github.com/yehorscode/RssTUI) project, rebranded and actively developed.

## Features

- Clean and responsive TUI interface
- Parses RSS/Atom feeds with HTML-to-text conversion for readable articles
- Built-in example feeds (TechCrunch, The Verge, NYT, xkcd, and more)
- Simple and intuitive keyboard navigation
- Full support for adding and managing your own feeds (coming soon)

## Installation

<!-- ### From PyPI (recommended)

```bash
pip install rss-feed-tui
```

Run:

```bash
rss-feed-tui
``` -->

### From source (development)

```bash
git clone https://github.com/whaiman/rss-feed-tui.git
cd rss-feed-tui
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

Run:

```bash
rss-feed-tui
```

## Supported platforms

- Linux - fully tested and works great
- macOS - should work out of the box
- Windows - fully tested and works great

## Usage

When you first launch the app, it loads a set of built-in example feeds.
Future versions will allow you to:

- Add your own RSS/Atom feeds directly in the app or via a config file
- Organize feeds into custom categories
- Edit or remove feeds at any time
- Import feeds from OPML files (common export format from other readers)

## Roadmap

This project is actively developed. Here are the main planned features:

- [ ] Persistent feed list via config file (TOML/JSON)
- [ ] Marking articles as read/unread (local SQLite database)
- [ ] Search and filtering across feeds
- [ ] Better full-article fetching (beyond just summary)
- [ ] Vim-style keybindings (j/k, gg, G, etc.)
- [ ] Offline reading mode with caching
- [ ] Improved error handling and offline mode
- [ ] Optional image previews (via kitty protocol or chafa)
- [ ] OPML import/export for easy feed migration
- [ ] Customizable themes and colors

Contributions are welcome! Feel free to open issues or pull requests.

## License

MIT License - same as the original project.
