# Arbie

[![CodeFactor](https://www.codefactor.io/repository/github/owodunni/arbie/badge?s=26f81a3989ea34700be306a9bbd3b90735e9c5ce)](https://www.codefactor.io/repository/github/owodunni/arbie) [![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide) [![codecov](https://codecov.io/gh/owodunni/Arbie/branch/master/graph/badge.svg?token=76NI0XBSH1)](https://codecov.io/gh/owodunni/Arbie) [![Actions Status](https://github.com/owodunni/arbie/workflows/Python%20Branch%20Workflow/badge.svg)](https://github.com/owodunni/arbie) [![License](https://img.shields.io/github/license/owodunni/GaugeRnR)](https://github.com/owodunni/GageRnR/blob/master/LICENSE)
[![PyPi](https://img.shields.io/pypi/v/Arbie)](https://pypi.org/project/Arbie/)


Arbie is a greedy crypto pirate!

![Arbie](./assets/icon/arbie-icon-192x192.png)

## Deploy

Deploy Brig to the local docker swarm with the following command:

```
docker stack deploy --compose-file Brig/docker-compose.yml birka
```

## Getting started

## Develop

Instructions for developing arbie using docker or virual-env.

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

Install requirment:
```
./gradlew pip
```

lint:
```
./gradlew lint
```
