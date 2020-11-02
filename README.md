# Arbie

[![CodeFactor](https://www.codefactor.io/repository/github/owodunni/arbie/badge)](https://www.codefactor.io/repository/github/owodunni/arbie) [![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide) [![codecov](https://codecov.io/gh/owodunni/Arbie/branch/master/graph/badge.svg)](https://codecov.io/gh/owodunni/Arbie) [![Actions Status](https://github.com/owodunni/arbie/workflows/Python%20Branch%20Workflow/badge.svg)](https://github.com/owodunni/arbie) [![License](https://img.shields.io/github/license/owodunni/GaugeRnR)](https://github.com/owodunni/GageRnR/blob/master/LICENSE)
[![PyPi](https://img.shields.io/pypi/v/Arbie)](https://pypi.org/project/Arbie/)


Arbie is a greedy crypto pirate!

![Arbie](./assets/icon/arbie-icon-192x192.png)

## Getting started

### Jupyter notebook

It is possible to test arbie in a Jupyter notebook. It is even encoraged for
gettign a hang of what Arbie can do!

Run Jupyter:
```
./gradlew startJupyter
```

Now go ahead and open one of the notebooks under examples.

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
docker run -v $(pwd):/arbie arbie ./gradlew test
```

lint:
```
docker run -v $(pwd):/arbie arbie ./gradlew lint
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

test:
```
./gradlew startGanache test
```

lint:
```
./gradlew lint
```
