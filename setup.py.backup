#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# Read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="rsstui",
    version="0.1.0",
    author="yehorscode",
    author_email="your-email@example.com",  # You should update this
    description="RSS reader TUI application built with Textual",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yehorscode/RssTUI",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary",
        "Topic :: Terminals",
        "Environment :: Console :: Curses",
    ],
    python_requires=">=3.8",
    install_requires=[
        "textual>=0.41.0",
        "feedparser>=6.0.0",
        "aiofiles>=23.0.0",
        "aiohttp>=3.8.0",
    ],
    extras_require={
        "dev": [
            "textual-dev>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "rsstui=rsstui.app:main",
        ],
    },
    package_data={
        "rsstui": ["styles/*.tcss"],
    },
    include_package_data=True,
    keywords="rss feed reader tui terminal textual news",
    project_urls={
        "Bug Reports": "https://github.com/yehorscode/RssTUI/issues",
        "Source": "https://github.com/yehorscode/RssTUI",
    },
)
