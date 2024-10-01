from setuptools import find_packages, setup

setup(
    name="ibwebapi",
    version="0.2.1",
    packages=find_packages(),
    install_requires=[
        "aiohttp",  # Add your project dependencies here
    ],
    author="Lorenzo Lazzeri",
    author_email="dev@lazerlabs.pro",
    description="A Python client for Interactive Brokers Web API",
    url="https://github.com/lazerlabs/ibwebapi",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "ibwebapi=ibwebapi.cli:main",
        ],
    },
)
