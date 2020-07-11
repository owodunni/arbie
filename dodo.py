"""Doit file for defining tasks."""

import os

project_dir = os.getcwd()

build_dir = f"{project_dir}/build"
project_name = "Arbie"
sorce_dir = f"{project_dir}/{project_name}"

test_dir = f"{sorce_dir}/tests"
test_result_dir = f"{build_dir}/tests"

pip = "pip"
pip_dir = f"{project_dir}/{pip}"

actions = "actions"


def task_test():
    return {
        actions:
            [f"pytest -v --pyargs {project_name} "  # noqa: WPS221
             f"--cov-report html:{test_result_dir}/cov/html "
             f"--cov-report xml:{test_result_dir}/cov/coverage.xml "
             f"--cov={sorce_dir} {test_dir} ",
             ],
    }


def task_lint():
    return {actions: ["flake8 . "]}


def task_isort():
    return {actions: ["isort **/*.py "]}


def task_stylefix():
    return {actions: ["autopep8 --in-place --recursive ."]}


def task_pip():
    return {actions: [f"{pip} install -r {pip_dir}/requirements.txt"]}


def task_pip_dev():
    return {actions: [f"{pip} install -r {pip_dir}/requirements-dev.txt"]}


def task_codecov():
    """Upload coverage report to codecov.

    This task requires that CODECOV_TOKEN env variable is set.
    Read more here: https://docs.codecov.io/v4.3.0/docs/about-the-codecov-bash-uploader
    """
    return {
        actions:
            [f"tools/codecov.sh -f "
                f"{test_result_dir}/cov/coverage.xml",
             ],
    }
