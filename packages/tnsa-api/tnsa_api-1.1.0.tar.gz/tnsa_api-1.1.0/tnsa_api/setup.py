"""
Setup script for TNSA API Python Client
"""

from setuptools import setup, find_packages

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tnsa-api",
    version="1.0.0",
    author="TNSA AI",
    author_email="info@tnsaai.com",
    description="A powerful, OpenAI-compatible Python SDK for TNSA NGen3 Pro and Lite Models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.tnsaai.com",
    project_urls={
        "Documentation": "https://docs.tnsaai.com",
        "Source": "https://github.com/tnsaai/tnsa-api-python",
        "Bug Tracker": "https://github.com/tnsaai/tnsa-api-python/issues",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "aiohttp>=3.8.0",
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
    },
    keywords="ai api tnsa ngen3 llm chat completion",
)