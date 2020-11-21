"""Helper functions for working with async."""

import asyncio


async def async_map(function, iterator):
    tasks = [function(i) for i in iterator]
    return await asyncio.gather(*tasks)
