"""Arbie.

Usage:
  Arbie -f config.yml
  Arbie (-h | --help)
  Arbie (-v | --version)

Options:
  -f --file=config.yml Load configuration file.
  -h --help     Show this screen.
  -v --version     Show version.
"""
import yaml
from docopt import docopt

import Arbie
from Arbie.arbie import App


def main(argv=None):
    arguments = docopt(__doc__, argv, version=Arbie.__version__)  # noqa: WPS609
    path_to_file = str(arguments["--file"])

    config = None
    with open(path_to_file, "r") as file:
        config = yaml.safe_load(file)
    App(config)
