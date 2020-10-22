"""Packaging logic for arbie."""
import os

from setuptools import find_packages, setup


def read(path):
    with open(path) as req:
        return req.read().splitlines()


def package_files(directory, file_filter):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            if any(substring in filename for substring in file_filter):
                paths.append(os.path.join("..", path, filename))
    return paths


extra_files = package_files("Arbie/resources", [".json"])

setup(
    packages=find_packages(exclude=["tests", "unit", "system"]),
    package_data={"": extra_files},
    install_requires=read("pip/requirements.txt"),
    tests_require=read("pip/requirements-dev.txt"),
    entry_points={"console_scripts": ["Arbie = Arbie.__main__:main"]},
)
