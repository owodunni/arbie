"""Event filter is a helpter class for filtering events with asyncio."""
import asyncio
import logging


class EventFilter(object):
    def __init__(self, event, from_block, to_block, steps):
        self.from_block = from_block
        self.to_block = to_block
        self.steps = steps
        self.event = event

    async def find_events(self):
        events = []
        for from_block in range(self.from_block, self.to_block, self.steps):
            to_block = from_block + self.steps - 1
            if to_block > self.to_block:
                to_block = self.to_block
            logging.getLogger().info(
                f"Searching for Pools in block range [{from_block}:{to_block}], total pools found: {len(events)}"
            )
            events.extend(await self._get_entries(from_block, to_block))
        return events

    async def _get_entries(self, from_block, to_block):
        event_filter = self.event.createFilter(
            fromBlock=int(from_block), toBlock=int(to_block)
        )

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, event_filter.get_all_entries)
