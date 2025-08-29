from pathlib import Path

from setuptools import find_packages, setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="ekacare",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
        "requests==2.25.0",
        "pyjwt==2.0.0",
        "boto3==1.37.0"
    ],
    author="Eka Care SDK Developer",
    author_email="developer@eka.care",
    description="Python SDK for Eka Care APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="healthcare, eka care, api, sdk, health records, abdm",
    url="https://developer.eka.care",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.6",
)
