# Arbie

[![CodeFactor](https://www.codefactor.io/repository/github/owodunni/arbie/badge?s=26f81a3989ea34700be306a9bbd3b90735e9c5ce)](https://www.codefactor.io/repository/github/owodunni/arbie) [![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide) [![codecov](https://codecov.io/gh/owodunni/Arbie/branch/master/graph/badge.svg?token=76NI0XBSH1)](https://codecov.io/gh/owodunni/Arbie) [![Actions Status](https://github.com/owodunni/arbie/workflows/Python%20Branch%20Workflow/badge.svg)](https://github.com/owodunni/arbie) [![License](https://img.shields.io/github/license/owodunni/GaugeRnR)](https://github.com/owodunni/GageRnR/blob/master/LICENSE)
[![PyPi](https://img.shields.io/pypi/v/Arbie)](https://pypi.org/project/Arbie/)


Arbie is a greedy crypto pirate!

![Arbie](./assets/icon/arbie-icon-192x192.png)

## Run

Run Brig with docker-compose:

```
cd Brig && docker-compose up -d
```

## Getting started

## Develop

Instructions for developing arbie using docker or virual-env.

To setup the development environment run:

```
./gradlew venv && source .venv/bin/activate && ./gradlew setup
```

It will run the steps bellow and make sure that all tools required for Arbie
are setup.

### Docker

The arbie repository can be built using docker. This is probably the simplest
approach if you just want to get things building.

```
docker build . -t arbie
```

You can now use the newly created docker image to build and test with.

test:
```
docker-compose run --rm arbie ./gradlew tAL
```

### Virtual-env

Create a virtual env:
```
./gradlew venv
```

Run virual env:
```
source .venv/bin/activate
```

Install requirements:
```
./gradlew pip
```

lint:
```
./gradlew lint
```

### Commits

Arbie works with [semantic-release](https://python-semantic-release.readthedocs.io/en/latest/)
and therefore has a special commit style. We use [Angular style](https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#commits) commits. A helpful tool for ensuring the correct commit style is [commitizen](https://github.com/commitizen/cz-cli).

Simply run when commiting:
```
cz c
```

### Pre commit hooks

To enforce code standard we use [pre-commit](https://pre-commit.com/) it manages
pre commit hooks.

Run to setup:
```
pre-commit install
```
