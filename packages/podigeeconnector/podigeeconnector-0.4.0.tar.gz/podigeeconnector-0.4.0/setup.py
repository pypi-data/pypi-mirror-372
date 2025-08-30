"""
Podigee Connector for Podcast Data

This package allows you to fetch data from the unofficial Podigee Podcast API.
The API is not documented and may change at any time. Use at your own risk.
"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="podigeeconnector",
    packages=find_packages(include=["podigeeconnector"]),
    version="0.4.0",
    description="Podigee Connector for Podcast Data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Open Podcast",
    license="MIT",
    entry_points={
        "console_scripts": [
            "podigeeconnector = podigeeconnector.__main__:main",
        ]
    },
    install_requires=["requests", "loguru", "PyYAML", "tenacity", "beautifulsoup4"],
)
