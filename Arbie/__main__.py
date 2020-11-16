"""Arbie.

Arbie is configured through a Yaml file.

Usage:
  Arbie -f config.yml [-l arbie.log.txt]
  Arbie (-h | --help)
  Arbie (-v | --version)

Options:
  -f --file=config.yml  Load configuration file.

  -l --log=arbie.log    Path to log files [default: arbie.log]

  -h --help             Show this screen.
  -v --version          Show version.

"""
import logging
from logging import handlers

import yaml
from docopt import docopt

import Arbie
from Arbie.arbie import App

max_log_size = int(10e6)  # noqa: WPS432


def setup_logging(log_file: str, severity=logging.INFO):
    formater = "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
    logging.basicConfig(
        level=severity, format=formater, datefmt="%m-%d %H:%M"
    )  # noqa: WPS323

    root_logger = logging.getLogger()

    file_handler = handlers.RotatingFileHandler(
        log_file, maxBytes=max_log_size, backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(formater))
    file_handler.setLevel(severity)
    root_logger.addHandler(file_handler)


async def main(argv=None):
    arguments = docopt(__doc__, argv, version=Arbie.__version__)  # noqa: WPS609

    logging.getLogger().info(f"arguments: {arguments}")

    setup_logging(str(arguments["--log"]))

    config_path = str(arguments["--file"])
    config = None
    with open(config_path, "r") as config_file:
        config = yaml.safe_load(config_file)

    app = App(config)

    try:
        await app.run()
    except Exception as ex:
        logging.getLogger().error(ex)
        raise ex
