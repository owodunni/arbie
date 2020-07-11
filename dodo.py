"""Doit file for defining tasks."""

import os

project_dir = os.getcwd()

build_dir = f"{project_dir}/build"
project_name = "Arbie"
sorce_dir = f"{project_dir}/{project_name}"
test_dir = f"{sorce_dir}/tests"

pip = "pip"
pip_dir = f"{project_dir}/{pip}"

actions = "actions"


def task_test():
    test_result_dir = f"{build_dir}/tests"

    return {
        actions:
            [f"pytest -v --pyargs {project_name} "  # noqa: WPS221
             f"--cov-report html:{test_result_dir}/cov "
             f"--cov={sorce_dir} {test_dir} "
             f"--junit-xml={test_result_dir}/test_results.xml",
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
