import os
from setuptools import setup

from undate import __version__

# load the readme contents and use for package long description
with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    README = readme.read()

REQUIREMENTS = ["python-dateutil"]
TEST_REQUIREMENTS = ["pytest>=7.2"]
DEV_REQUIREMENTS = ["wheel", "black>=22.10.0", "pre-commit>=2.20.0"]

setup(
    name="undate",
    version=__version__,
    description="library for working with uncertain, fuzzy, or "
    + "partially unknown dates and date intervals",
    long_description=README,
    url="https://github.com/dh-tech/hackathon-2022",
    author="DHTech",
    author_email="dhtech.community@gmail.com",
    license="Apache License, Version 2.0",
    packages=["undate"],
    install_requires=REQUIREMENTS,
    tests_require=TEST_REQUIREMENTS,
    extras_require={
        "test": TEST_REQUIREMENTS,
        "dev": TEST_REQUIREMENTS + DEV_REQUIREMENTS,
    },
    classifiers=[
        # any relevant environment classifiers ?
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
)
