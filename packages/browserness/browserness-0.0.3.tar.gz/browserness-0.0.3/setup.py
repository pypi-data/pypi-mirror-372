from setuptools import setup, find_packages

# Read the contents of README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="browserness",
    version="0.0.3",
    description="Python SDK for Browserness API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Browserness",
    author_email="support@browserness.com",
    url="https://github.com/browserness/sdk-python",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.23.0",
        "pydantic>=1.9.0,<3",
    ],
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
)