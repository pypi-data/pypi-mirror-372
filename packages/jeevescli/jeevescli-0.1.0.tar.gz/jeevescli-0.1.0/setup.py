#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="jeevescli",
    version="0.1.0",
    author="Daniel Losey",

    description="Stateless, small context, high leverage AI assistant",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dadukhankevin/jeevescli",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "openai",
        "pydantic",
        "python-dotenv",
        "pysublime",
        "flask",
    ],
    entry_points={
        "console_scripts": [
            "jeeves=jeevescli.jeeves:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Utilities",
    ],
    keywords="ai assistant cli developer tools",
    project_urls={
        "Bug Reports": "https://github.com/dadukhankevin/jeevescli/issues",
        "Source": "https://github.com/dadukhankevin/jeevescli",
    },
)
