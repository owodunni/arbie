"""Helper functions for working with async."""

import asyncio
from concurrent.futures import ThreadPoolExecutor

thread_pool = ThreadPoolExecutor(max_workers=15)  # noqa: WPS432


def chunked(seq, chunk_size):
    yield from (
        seq[index : index + chunk_size]
        for index in range(0, len(seq), chunk_size)  # noqa: WPS518
    )


async def async_map_chunk(function, seq):
    tasks = [function(i) for i in seq]
    return await asyncio.gather(*tasks)


async def async_map(function, seq, chunk_size=100, wait_time=0):
    res = []
    for chunk in chunked(seq, chunk_size):
        res.extend(await async_map_chunk(function, chunk))
        await asyncio.sleep(wait_time)
    return res


async def run_async(function, *args):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(thread_pool, function, *args)
