"""Simple built-in tools for agents."""
from __future__ import annotations
import aiohttp
import asyncio
from typing import Optional


class HttpGetTool:
    name = "http_get"
    description = "Fetches text content from a URL (GET)."

    async def run(self, input_text: str) -> str:
        url = input_text.strip()
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
                async with session.get(url) as resp:
                    txt = await resp.text()
                    return txt[:800]
        except Exception as e:
            return f"ERROR fetching {url}: {e}"  # tool errors become content


class SleepTool:
    name = "sleep"
    description = "Sleep for N seconds (integer)."

    async def run(self, input_text: str) -> str:
        try:
            n = int(input_text.strip())
        except ValueError:
            n = 1
        n = max(0, min(n, 10))
        await asyncio.sleep(n)
        return f"Slept {n} seconds"