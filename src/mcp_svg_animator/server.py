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
            name="create_svg_from_yaml",
            description="""Create an animated SVG diagram from a YAML specification.

Supports shapes: circle, rectangle, line, text, path, group
Supports animations: attribute animations and transform animations (rotate, translate, scale)
Supports reusable definitions and library imports.

Example YAML:
```yaml
width: 400
height: 300
definitions:
  my_circle:
    type: circle
    r: 25
    fill: red
elements:
  - use: my_circle
    cx: 100
    cy: 150
  - type: group
    transform: translate(200, 150)
    transform_animations:
      - type: rotate
        values: "0;360"
        dur: 2s
        repeatCount: indefinite
    elements:
      - type: rectangle
        x: -25
        y: -25
        width: 50
        height: 50
        fill: blue
```""",
            inputSchema={
                "type": "object",
                "properties": {
                    "yaml_spec": {
                        "type": "string",
                        "description": "YAML specification for the SVG diagram",
                    },
                },
                "required": ["yaml_spec"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls for SVG generation."""
    if name == "create_svg_from_yaml":
        from .generators.yaml_loader import create_diagram_from_yaml

        yaml_spec = arguments.get("yaml_spec", "")
        svg_content = create_diagram_from_yaml(yaml_spec)
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
