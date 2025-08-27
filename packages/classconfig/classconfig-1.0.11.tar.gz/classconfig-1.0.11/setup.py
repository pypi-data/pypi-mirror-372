# -*- coding: UTF-8 -*-
""""
Created on 26.04.23

:author:     Martin Dočekal
"""
from setuptools import setup, find_packages


def is_requirement(line):
    return not (line.strip() == "" or line.strip().startswith("#"))


with open('README.md') as readme_file:
    README = readme_file.read()

with open("requirements.txt") as f:
    REQUIREMENTS = [line.strip() for line in f if is_requirement(line)]


setup_args = dict(
    name='classconfig',
    version='1.0.11',
    description='Package for creating configuration files automatically and loading objects from those configuration files.',
    long_description_content_type="text/markdown",
    long_description=README,
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    author='Martin Dočekal',
    keywords=['configuration', 'auto config', 'config', 'configurable', 'configurable class', 'configurable object',
              'configurable attribute'],
    url='https://github.com/mdocekal/classconfig',
    python_requires='>=3.9',
    install_requires=REQUIREMENTS
)

if __name__ == '__main__':
    setup(**setup_args)
