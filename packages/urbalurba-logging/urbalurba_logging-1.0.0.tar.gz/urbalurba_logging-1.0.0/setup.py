"""
Setup script for Urbalurba Logging Python package
"""

from setuptools import setup, find_packages

with open("README-python.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="urbalurba-logging",
    version="1.0.0",
    author="Terje Christensen",
    author_email="integration-platform@redcross.no",
    description="Professional structured logging library following 'Loggeloven av 2025' requirements",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/terchris/urbalurba-logging",
    project_urls={
        "Bug Tracker": "https://github.com/terchris/urbalurba-logging/issues",
        "Documentation": "https://github.com/terchris/urbalurba-logging/blob/main/python/README-python.md",
        "Source Code": "https://github.com/terchris/urbalurba-logging/tree/main/python",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Logging",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "structlog>=23.1.0",
        "opentelemetry-api>=1.21.0",
        "opentelemetry-sdk>=1.21.0",
        "opentelemetry-exporter-otlp>=1.21.0",
        "opentelemetry-exporter-otlp-proto-http>=1.21.0",
        "opentelemetry-semantic-conventions>=0.44b0",
        "requests>=2.31.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "python-dotenv>=1.0.0",
            "aiohttp>=3.8.0",
        ],
        "examples": [
            "python-dotenv>=1.0.0",
            "aiohttp>=3.8.0",
            "requests>=2.31.0",
        ],
    },
    keywords="logging, structured-logging, json, opentelemetry, azure-monitor, observability",
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "urbalurba-lib-test=urbalurba_logging.lib_test:main",
        ],
    },
)