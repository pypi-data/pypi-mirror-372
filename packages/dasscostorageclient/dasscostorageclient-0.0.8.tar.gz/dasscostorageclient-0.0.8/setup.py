from setuptools import setup, find_packages
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

version = os.getenv('PACKAGE_VERSION')
description = 'DaSSCo Storage API SDK'

# Setting up
setup(
    name="dasscostorageclient",
    version=version,
    author="DaSSCo",
    author_email="dassco@ku.dk",
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=['requests', 'pydantic'],
    python_requires=">=3.10",
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ]
)
