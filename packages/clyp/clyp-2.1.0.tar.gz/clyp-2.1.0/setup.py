from setuptools import setup
from pathlib import Path

# Package is in ./clyp directory

# Read the README file for the long description
long_description = Path("README.md").read_text(encoding="utf-8")

setup(
    name="clyp",
    version="2.1.0",
    author="CodeSoft",
    packages=["clyp"],
    install_requires=["typeguard", "click", "requests", "ycpm", "cython", "black", "orjson"],
    license="MIT",
    description="Clyp is a programming language that transpiles to Python.",
    url="https://clyp.codesft.dev/",
    project_urls={
        "Source": "https://github.com/clyplang/clyp",
    },
    entry_points={
        "console_scripts": [
            "clyp=clyp.cli:main",
        ],
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
)
