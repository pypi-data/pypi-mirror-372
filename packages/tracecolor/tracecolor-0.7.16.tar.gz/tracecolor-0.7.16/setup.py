from setuptools import setup, find_packages
import os
import re

# Read version from __init__.py
def get_version():
    init_path = os.path.join(os.path.dirname(__file__), "tracecolor", "__init__.py")
    with open(init_path, "r", encoding="utf-8") as f:
        content = f.read()
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
        raise RuntimeError("Unable to find version string in __init__.py")

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tracecolor",
    version=get_version(),
    author="Marco Del Pin",
    author_email="marco.delpin@gmail.com",
    description="Enhanced Python logger with colorized output, TRACE/PROGRESS levels, UDP monitoring, and Loguru backend.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/marcodelpin/tracecolor",
    packages=find_packages(exclude=["tests.*", "tests"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "loguru>=0.7.2",
        "colorlog>=6.0.0",  # Fallback for when loguru is not available
    ],
    extras_require={
        "yaml": [
            "pyyaml>=6.0",
        ],
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=22.0",
            "flake8>=5.0",
            "mypy>=0.990",
        ]
    },
    entry_points={
        "console_scripts": [
            "tracecolor-monitor=tracecolor.monitor:main",
        ],
    },
)