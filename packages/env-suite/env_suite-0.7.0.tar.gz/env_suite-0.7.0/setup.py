#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: diable=line-too-long,missing-module-docstring,missing-function-docstring,missing-class-docstring,exec-used
import setuptools

# DO NOT EDIT THIS NUMBER
# It is changed automatically by python-semantic-release
__version__ = "0.7.0"

with open("README.md", "r") as file:
    long_description = file.read()

setuptools.setup(
        name="env_suite",
        version=__version__,
        author="Chilton Group",
        author_email="nicholas.chilton@manchester.ac.uk",
        description="A suite of tools for including enviroment effects in first principal calculations",
        long_description=long_description,
        long_description_content_type="text/markdown",
        project_url={
            "Bug Tracker": "https://github.com/chilton-group/env/issues",
            "Documentation": "https://chilton-group.gitlab.io/env_suite",
            "Source": "https://github.com/chilton-group/env_suite",
        },
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Operating System :: OS Independent",
        ],
        packages=setuptools.find_packages(),
        python_requires=">=3.9",
        install_requires=[
            "numpy<=1.26.4",
            "scipy",
            "matplotlib",
            "hpc_suite>=1.9.0",
            "phonopy",
            "pymatgen",
            "gaussian_suite",
        ],
        entry_points={
            "console_scripts": [
                "env_suite=env_suite.cli:main"
                ]
            },
        )
