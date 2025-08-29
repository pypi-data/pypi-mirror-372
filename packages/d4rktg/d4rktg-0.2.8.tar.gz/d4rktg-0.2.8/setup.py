from setuptools import setup, find_packages
from pathlib import Path
import os

VERSION_FILE = "VERSION.txt"

def read_version():
    version_path = Path(VERSION_FILE)
    version = version_path.read_text(encoding="utf-8").strip()
    return version

def get_setup_kwargs(raw: bool = False):
    version = read_version()
    with open('README.rst') as r:
        readme = r.read()
    with open('requirements.txt') as f:
        requirements = f.read().splitlines()
    return {
        "name": "d4rktg",
        "version": version,
        "author": "D4rkShell",
        "author_email": "premiumqtrst@gmail.com",
        "packages": find_packages(),
        "install_requires": requirements,
        "keywords": ['python', 'telegram bot', 'D4rkShell'],
        "description": "A module for create with easy and fast",
        "long_description": readme,
        "long_description_content_type": "text/x-rst",
        "classifiers": [
            "Development Status :: 1 - Planning",
            "Intended Audience :: Developers",
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent",
        ],
    }

if __name__ == '__main__':
    version = read_version()
    setup(**get_setup_kwargs(raw=False))

