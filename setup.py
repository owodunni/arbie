"""Packaging logic for arbie."""
from setuptools import setup, find_packages

with open('pip/requirements.txt') as f:
    requirements = f.read().splitlines()

with open('pip/requirements-dev.txt') as f:
    test_requirements = f.read().splitlines()

setup(
    packages=find_packages(),
    package_data={'': ["resources/*"]},
    install_requires=requirements,
    tests_require=test_requirements
)
