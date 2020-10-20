"""Main application."""

from Arbie.Actions import ActionTree, Store

default_store = Store()


class App(object):
    """App is used for configuring and running Arbie."""

    def __init__(self, config, store=default_store):
        self.config = config
        self.store = store
        self.action_tree = ActionTree.create(self.config['actions'], self.store)

    def run(self):
        self.action_tree.run()
