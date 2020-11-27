"""Event filter is a helpter class for filtering events with asyncio."""
import logging

from prometheus_async.aio import time

from Arbie.async_helpers import async_map, run_async
from Arbie.prometheus import get_prometheus

GET_ENTRIES = get_prometheus().summary(
    "event_filter_get_entries", "Time for getting entries"
)


class EventTransform(object):
    def __init__(self, event_filter, event_transform):
        self.event_filter = event_filter
        self.event_transform = event_transform

    def run(self):
        events = self.event_filter.get_all_entries()
        return self.event_transform(events)


class EventFilter(object):
    def __init__(self, event, event_transform, from_block, to_block, steps):
        self.from_block = from_block
        self.to_block = to_block
        self.steps = steps
        self.event = event
        self.event_transform = event_transform

    async def find_events(self):
        nmb_event_chunks = int((self.to_block - self.from_block) / self.steps) + 1
        results = await async_map(self._get_entries, range(nmb_event_chunks))

        # results is a list of lists, that we need to flatten
        # https://stackoverflow.com/questions/952914/how-to-make-a-flat-list-out-of-list-of-lists
        return [item for sublist in results for item in sublist]

    async def _get_entries(self, index):
        from_block = index * self.steps + self.from_block
        to_block = from_block + self.steps - 1
        if to_block > self.to_block:
            to_block = self.to_block
        logging.getLogger().info(
            f"Searching for Pools in block range [{from_block}:{to_block}]"
        )
        return await self._get_entries_range(from_block, to_block)

    @time(GET_ENTRIES)
    async def _get_entries_range(self, from_block, to_block):
        event_filter = self.event.createFilter(
            fromBlock=int(from_block), toBlock=int(to_block)
        )
        ev = EventTransform(event_filter, self.event_transform)
        return await run_async(ev.run)
