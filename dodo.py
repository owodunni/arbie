buildDir = "build"


def task_test():
    outDir = "build/coverage"
    return {
        'actions': ['pytest -v --pyargs Arbie '
                    f"--cov-report html:{outDir} "
                    f"--cov=Arbie Arbie/tests/ "
                    f"--junit-xml={buildDir}/test_results.xml"]}


def task_lint():
    return {'actions': ['flake8 . ']}


def task_stylefix():
    return {'actions': ['autopep8 --in-place --recursive .']}


def task_pip_install():
    return {'actions': ['pip install -r pip/requirements.txt']}


def task_pip_install_dev():
    return {'actions': ['pip install -r pip/requirements-dev.txt']}
