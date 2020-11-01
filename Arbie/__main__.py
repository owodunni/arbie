"""Arbie.

Arbie is configured through a Yaml file.

Usage:
  Arbie -f config.yml
  Arbie (-h | --help)
  Arbie (-v | --version)

Options:
  -f --file=config.yml Load configuration file.
  -h --help     Show this screen.
  -v --version     Show version.
"""
import logging

import yaml
from docopt import docopt

import Arbie
from Arbie.arbie import App


def setup_logging(severity=logging.INFO):
    logging.basicConfig(
        level=severity,
        format="%(name)-12s: %(levelname)-8s %(message)s",  # noqa: WPS323
        datefmt="%m-%d %H:%M",  # noqa: WPS323
    )


def main(argv=None):
    setup_logging()
    arguments = docopt(__doc__, argv, version=Arbie.__version__)  # noqa: WPS609
    path_to_file = str(arguments["--file"])

    config = None
    with open(path_to_file, "r") as file:
        config = yaml.safe_load(file)
    app = App(config)
    app.run()
