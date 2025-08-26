# dev_check_tools.py
import asyncio
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

async def main():
    url = "http://localhost:8000/mcp"
    async with streamablehttp_client(url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("Tools:", [t.name for t in tools.tools])
            # sanity: call ping
            resp = await session.call_tool("ping", {})
            print("ping ->", resp.content[0].text if resp.content else resp)

asyncio.run(main())
