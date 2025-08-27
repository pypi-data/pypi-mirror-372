"""
Setup script for riddles-solver package
"""

from setuptools import setup, find_packages
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
readme_path = os.path.join(current_dir, "README.md")

with open(readme_path, "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="riddles-solver",
    version="1.0.0",
    author="Towux",
    description="A Python library for solving riddles using repixify.com API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Towux/riddles_solver",
    project_urls={
        "Bug Reports": "https://github.com/Towux/riddles_solver/issues",
        "Source": "https://github.com/Towux/riddles_solver",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Games/Entertainment :: Puzzle Games",
        "Topic :: Education",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Text Processing",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Environment :: Web Environment",
        "Natural Language :: English",
        "Framework :: AsyncIO",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.28.0",
        "playwright>=1.40.0",
    ],
    extras_require={
        "async": ["aiohttp>=3.8.0"],
        "user-agent": ["user-agents>=2.2.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.991",
        ],
    },
    entry_points={
        "console_scripts": [
            "riddles-get-key=riddles_solver.cli:main",
        ],
    },
    keywords="riddles puzzle solver api repixify ai artificial-intelligence automation nlp text-processing",
    include_package_data=True,
    zip_safe=False,
)
