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
from docopt import docopt

import Arbie


class App(object):
    """Main Application."""

    def __init__(self, argv=None):
        arguments = docopt(__doc__, argv, version=Arbie.__version__)  # noqa: WPS609
        self.config_file = str(arguments['--file'])
