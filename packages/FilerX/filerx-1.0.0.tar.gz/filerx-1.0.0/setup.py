from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="FilerX",
    version="1.0.0",
    author="ali-jafari",
    author_email="thealiapi@gmail.com",
    description="Universal config loader with auto-detect, nested keys, merge, and file watcher (JSON/YAML/TOML)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iTs-GoJo/FilerX",
    packages=find_packages(where="src"),
    package_dir={"": "filerx"},
    python_requires=">=3.8",
    install_requires=[
        "PyYAML>=6.0",
        "toml>=0.10.2"
    ],
    extras_require={
        "dev": ["pytest", "black", "mypy"],
        "watch": ["watchdog>=3.0.0"]
    },
    entry_points={
        "console_scripts": [
            "filerx=filerx.core:main",
        ],
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="config, loader, json, yaml, toml, nested keys, merge, watcher, settings, file manager, auto-detect, auto-fix, config parser, configuration, devops, python config, config utils, dynamic config, data loader, config merger, json yaml toml, config handler, nested config, file watcher, configuration manager, python library, config editor, config automation, file parser, config toolkit",
    license="MIT",
)
