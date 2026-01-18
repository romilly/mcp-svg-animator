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
        Tool(
            name="create_animation_video",
            description="""Create a video file from an SVG animation.

Takes an SVG with SMIL animations and records it to a .webm video file.
The SVG can be created using create_svg_from_yaml first.

Example usage:
1. First create an SVG with animations using create_svg_from_yaml
2. Then pass the SVG content to this tool to create a video""",
            inputSchema={
                "type": "object",
                "properties": {
                    "svg_content": {
                        "type": "string",
                        "description": "SVG content with animations",
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Path where the .webm video will be saved",
                    },
                    "duration_ms": {
                        "type": "number",
                        "description": "Duration of the video in milliseconds (default: 3000)",
                        "default": 3000,
                    },
                },
                "required": ["svg_content", "output_path"],
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

    if name == "create_animation_video":
        from .generators.video_generator import create_video_from_svg

        svg_content = arguments.get("svg_content", "")
        output_path = arguments.get("output_path", "animation.webm")
        duration_ms = int(arguments.get("duration_ms", 3000))

        create_video_from_svg(svg_content, output_path, duration_ms=duration_ms)
        return [TextContent(type="text", text=f"Video saved to {output_path}")]

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
