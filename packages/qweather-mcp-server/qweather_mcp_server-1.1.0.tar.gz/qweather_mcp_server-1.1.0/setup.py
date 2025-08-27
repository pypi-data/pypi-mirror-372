#!/usr/bin/env python3
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="qweather-mcp-server",
    version="1.1.0",
    author="Weather MCP Server",
    author_email="",
    description="中国天气查询 MCP 服务器",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/modelcontextprotocol/weather-mcp-server",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    py_modules=["weather_server", "config_template"],
    entry_points={
        "console_scripts": [
            "qweather-mcp-server=weather_server:main",
        ],
    },
)