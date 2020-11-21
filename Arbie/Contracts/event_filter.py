"""Event filter is a helpter class for filtering events with asyncio."""
import asyncio
import logging

from asyncstdlib.builtins import list as alist
from asyncstdlib.builtins import map as amap


class EventFilter(object):
    def __init__(self, event, from_block, to_block, steps):
        self.from_block = from_block
        self.to_block = to_block
        self.steps = steps
        self.event = event

    async def find_events(self):
        nmb_event_chunks = int((self.to_block - self.from_block) / self.steps) + 1
        results = await alist(amap(self._get_entries, range(nmb_event_chunks)))
        # results is a list of lists, that we need to flatten
        # https://stackoverflow.com/questions/952914/how-to-make-a-flat-list-out-of-list-of-lists
        return [item for sublist in results for item in sublist]

    async def _get_entries(self, index):
        from_block = index * self.steps + self.from_block
        to_block = from_block + self.steps - 1
        if index % 10 == 0:
            logging.getLogger().info(
                f"Searching for Pools in block range [{from_block}:{to_block}]"
            )
        if to_block > self.to_block:
            to_block = self.to_block
        return await self._get_entries_range(from_block, to_block)

    async def _get_entries_range(self, from_block, to_block):
        event_filter = self.event.createFilter(
            fromBlock=int(from_block), toBlock=int(to_block)
        )

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, event_filter.get_all_entries)
