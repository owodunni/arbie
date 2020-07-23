"""Packaging logic for arbie."""
from setuptools import find_packages, setup


def read(path):
    with open(path) as req:
        return req.read().splitlines()


setup(
    packages=find_packages(exclude=['tests', 'unit']),
    package_data={'': ['resources/*']},
    install_requires=read('pip/requirements.txt'),
    tests_require=read('pip/requirements-dev.txt'),
)
