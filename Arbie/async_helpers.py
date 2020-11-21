"""Helper functions for working with async."""

import asyncio
from concurrent.futures import ThreadPoolExecutor

thread_pool = ThreadPoolExecutor(max_workers=15)  # noqa: WPS432


async def async_map(function, iterator):
    tasks = [function(i) for i in iterator]
    return await asyncio.gather(*tasks)


async def run_async(function, *args):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(thread_pool, function, *args)
