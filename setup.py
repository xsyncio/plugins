from pathlib import Path

from setuptools import find_packages
from setuptools import setup


def parse_requirements(filename: str):
    with open(filename, encoding="utf-8") as f:
        lines = f.read().splitlines()
        return [line for line in lines if line and not line.startswith("#")]


setup(
    name="osintbuddy",
    version="0.2.0",
    author="jerlendds",
    author_email="osintbuddy@proton.me",
    description="OSINTBuddy - mine, merge, and map data for novel insights",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/osintbuddy/plugins",
    project_urls={
        "Documentation": "https://docs.osintbuddy.com/",
        "Source": "https://github.com/osintbuddy/plugins",
        "Tracker": "https://github.com/osintbuddy/osintbuddy/issues",
    },
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    packages=find_packages(exclude=["tests*", "scripts*", "build*", "dist*"]),
    include_package_data=True,
    install_requires=parse_requirements("requirements.txt"),
    extras_require={
        "test": parse_requirements("requirements-test.txt")
        if Path("requirements-test.txt").exists()
        else [],
    },
    entry_points={
        "console_scripts": [
            "ob=osintbuddy.ob:main",
        ],
    },
)
