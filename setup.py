#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

setup(
    python_requires=">=3.10",
    description="Back-end data processing API",
    install_requires=[
        "fastapi",
        "numpy",
        "attrs",
        "cattrs",
        "uvicorn",
        "rich_click",
    ],
    include_package_data=True,
    keywords="thrills_api",
    name="frf-thrills_api",
    packages=find_packages(
        include=[
            "thrills_api",
            "thrills_api.*",
        ]
    ),
    entry_points={
        "console_scripts": [
            "thrills_api = thrills_api.main:cli",
        ],
    },
    version="1.3.9",
    zip_safe=False,
)
