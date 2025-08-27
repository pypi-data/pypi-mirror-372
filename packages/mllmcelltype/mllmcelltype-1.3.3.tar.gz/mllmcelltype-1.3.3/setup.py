import os

from setuptools import find_packages, setup

# Read the contents of the README file
this_directory = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "mLLMCelltype: A Python module for cell type annotation using various LLMs."

setup(
    name="mllmcelltype",
    version="1.3.3",
    packages=find_packages(),
    description="A Python module for cell type annotation using various LLMs.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="mLLMCelltype Team",
    author_email="cafferychen777@tamu.edu",
    url="https://github.com/cafferychen777/mLLMCelltype",
    python_requires=">=3.9",
    install_requires=[
        "pandas>=1.0.0",
        "numpy>=1.19.0",
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
        "jsonschema>=4.0.0",
        # LLM Provider APIs are in extras_require
    ],
    extras_require={
        "all": [
            "openai>=1.0.0",
            "anthropic>=0.5.0",
            "google-genai>=1.0.0",
            "python-dotenv>=0.19.0",
            # Visualization libraries for user's own plotting needs
            "matplotlib>=3.3.0",
            "seaborn>=0.11.0",
        ],
        # Visualization libraries (not used in core package, but useful for users)
        # Note: If using with scanpy, these are already included as scanpy dependencies
        "visualization": [
            "matplotlib>=3.3.0",
            "seaborn>=0.11.0",
        ],
        "examples": [
            "matplotlib>=3.3.0",
            "scanpy>=1.8.0",
            "python-dotenv>=0.19.0",
        ],
        "openai": ["openai>=1.0.0"],
        "anthropic": ["anthropic>=0.5.0"],
        "gemini": ["google-genai>=1.0.0"],
        "grok": ["x-ai>=0.1.0"],
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "pre-commit>=2.16.0",
            "ruff>=0.11.0",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
