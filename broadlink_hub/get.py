"""Simple asynchronous HTTP get"""

import asyncio
import logging
import aiohttp

from timeit import default_timer as timer

_LOGGER = logging.getLogger(__name__)

async def get(url, headers = None):
    start = timer()
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            status = resp.status
            body = await resp.text()
    end = timer()
    _LOGGER.info('HTTP query duration: %.6fs', end - start)
    if status != 200:
        _LOGGER.warning('HTTP query %s status: %d', url, status)
    return status
