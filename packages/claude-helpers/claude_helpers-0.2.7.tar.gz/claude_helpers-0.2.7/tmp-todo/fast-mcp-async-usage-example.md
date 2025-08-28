# Fast-mcp Docs example

> Source: https://gofastmcp.com/deployment/running-server

## Async Usage

FastMCP servers are built on async Python, but the framework provides both synchronous and asynchronous APIs to fit your application’s needs. The run() method we’ve been using is actually a synchronous wrapper around the async server implementation.
For applications that are already running in an async context, FastMCP provides the run_async() method:

```
from fastmcp import FastMCP
import asyncio


mcp = FastMCP(name="MyServer")

@mcp.tool
def hello(name: str) -> str:
    return f"Hello, {name}!"

async def main():
    # Use run_async() in async contexts
    await mcp.run_async(transport="http", port=8000)

if __name__ == "__main__":
    asyncio.run(main())
```

> The run() method cannot be called from inside an async function because it creates its own async event loop internally. If you attempt to call run() from inside an async function, you’ll get an error about the event loop already running. Always use run_async() inside async functions and run() in synchronous contexts.

Both run() and run_async() accept the same transport arguments, so all the examples above apply to both methods.
