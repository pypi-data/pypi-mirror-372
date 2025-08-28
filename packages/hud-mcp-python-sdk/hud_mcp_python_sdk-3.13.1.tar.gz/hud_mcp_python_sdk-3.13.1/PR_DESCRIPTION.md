# Fix: Propagate HTTP errors to client

## Motivation and Context
HTTP request failures were not being properly communicated to clients, causing silent failures. This fix ensures errors are sent through the read stream so clients are notified when requests fail.

## How Has This Been Tested?
Has been tested in production environments (used by https://github.com/hud-evals/hud-python with a remote server).

## Breaking Changes
None - this is a backwards-compatible error handling improvement.

## Types of changes
- [x] Bug fix (non-breaking change which fixes an issue)

## Checklist
- [x] I have read the [MCP Documentation](https://modelcontextprotocol.io)
- [x] My code follows the repository's style guidelines
- [x] New and existing tests pass locally
- [x] I have added appropriate error handling
- [x] Documentation not needed for this internal fix

## Additional context
This change wraps the `handle_request_async` function in a try-catch block and sends any exceptions to `ctx.read_stream_writer` to ensure proper error propagation in the streamable HTTP transport layer.

### Example scenario where this fix is critical:

**HTTP Error Codes (502, 503, 504, etc.)**
```python
# Without this fix: Client hangs when server returns 502 Bad Gateway
# With this fix: Client receives the HTTP error
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.session import ClientSession

async with streamablehttp_client(server_url) as (read_stream, write_stream):
    async with ClientSession(read_stream, write_stream) as session:
        await session.initialize()
        try:
            result = await session.call_tool("api_operation", arguments={})
        except Exception as e:
            print(f"Error received: {e}")  # Now properly catches 502, 503, 504 errors
```
