"""MCP server for SVG diagram generation."""

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("mcp-svg-animator")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available SVG generation tools."""
    return [
        Tool(
            name="create_animated_diagram",
            description="Create an animated SVG diagram with custom shapes and animations",
            inputSchema={
                "type": "object",
                "properties": {
                    "width": {
                        "type": "number",
                        "description": "Width of the SVG canvas",
                        "default": 400,
                    },
                    "height": {
                        "type": "number",
                        "description": "Height of the SVG canvas",
                        "default": 300,
                    },
                    "elements": {
                        "type": "array",
                        "description": "List of shapes to draw",
                        "items": {"type": "object"},
                    },
                    "animations": {
                        "type": "array",
                        "description": "Animation specifications",
                        "items": {"type": "object"},
                    },
                },
                "required": [],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls for SVG generation."""
    if name == "create_animated_diagram":
        from .generators.animations import create_animated_diagram

        svg_content = create_animated_diagram(arguments)
        return [TextContent(type="text", text=svg_content)]

    raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
