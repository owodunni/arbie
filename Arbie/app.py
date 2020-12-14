"""Main application."""

import logging

from Arbie.settings_parser import SettingsParser

logger = logging.getLogger()


class App(object):
    """App is used for configuring and running Arbie."""

    def __init__(self, config):
        sp = SettingsParser(config)
        self.store = sp.setup_store()
        self.action_tree = sp.action_tree(self.store)

    async def run(self):
        if self.action_tree is None:
            logger.warning("No actions given in configuration")
            return
        try:
            await self.action_tree.run()
        except Exception as e:
            logger.fatal(e, exc_info=True)
            raise e

    def stop(self):
        self.action_tree.stop()
