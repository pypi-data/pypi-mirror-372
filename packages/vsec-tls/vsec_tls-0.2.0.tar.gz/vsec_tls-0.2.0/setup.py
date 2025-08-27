#!/usr/bin/env python
from setuptools import setup, find_packages
from codecs import open
import os

about = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "vsec_tls", "__version__.py"), "r", "utf-8") as f:
    exec(f.read(), about)

with open("README.md", "r", "utf-8") as f:
    readme = f.read()

setup(
    name=about["__title__"],  # "vsec_tls"
    version=about["__version__"],
    author=about["__author__"],
    description=about["__description__"],
    license="Proprietary",
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    package_data={
        'vsec_tls': ['dependencies/*', 'dependencies/**/*'],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries",
        "Natural Language :: English",
    ],
    python_requires=">=3.8",
    project_urls={
        "Source": "https://github.com/ferrumlegis/velum-secure",
    }
)
