#!/usr/bin/env python3
"""
Setup script for upstox-option-chain package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="theoprice",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python CLI application for fetching real-time options trading data from Upstox API with Black-Scholes Greeks calculations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/theoprice",
    packages=find_packages(include=["src", "src.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=[
        "upstox-python-sdk==2.17.0",
        "rich>=13.7.0",
        "inquirer>=3.2.4",
        "python-dotenv>=1.0.0",
        "scipy>=1.11.4",
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "theoprice=src.option_chain_app:main",
        ],
    },
    keywords="upstox options trading black-scholes greeks indian-markets cli",
    project_urls={
        "Documentation": "https://github.com/yourusername/theoprice#readme",
        "Source": "https://github.com/yourusername/theoprice",
        "Tracker": "https://github.com/yourusername/theoprice/issues",
    },
)