# MCP SVG Diagram Generator Server

## Overview

An MCP (Model Context Protocol) server that provides tools for generating various types of SVG diagrams, both static and animated. The server uses specialized Python libraries for different diagram types, exposing each as separate tools that Claude (or other MCP clients) can invoke.

## Core Concept

Rather than forcing a single library to handle all diagram types, use multiple specialized libraries and expose each as dedicated MCP tools. This approach:

- Leverages each library's strengths
- Simplifies implementation (no library conflicts)
- Allows incremental development
- Provides clear tool boundaries for Claude to understand

## Architecture

### Basic Structure

```
mcp-svg-server/
├── server.py                 # Main MCP server
├── generators/
│   ├── flowcharts.py        # Block diagrams, flowcharts
│   ├── circuits.py          # Electronic circuit diagrams
│   ├── animations.py        # Animated SVG diagrams
│   ├── charts.py            # Data visualization charts
│   └── general.py           # Custom/general SVG creation
└── requirements.txt
```

### Tool Dispatch Pattern

```python
@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    if name == "create_flowchart":
        return generate_flowchart(arguments)
    elif name == "create_circuit":
        return generate_circuit(arguments)
    elif name == "create_animated_diagram":
        return generate_animated(arguments)
    elif name == "create_chart":
        return generate_chart(arguments)
    # ... etc
```

## Python Libraries by Use Case

### General SVG Creation

**svgwrite**
- Most established library for programmatic SVG generation
- Clean API with good documentation
- Supports all SVG elements including SMIL animations
- Direct control over SVG structure
- Installation: `pip install svgwrite`
- Repository: https://github.com/mozman/svgwrite
- Documentation: https://svgwrite.readthedocs.io/

**drawsvg**
- Modern library with native animation support
- High-level, intuitive API
- Can render to PNG/video via Cairo
- Excellent for animated diagrams
- Installation: `pip install drawsvg`
- Repository: https://github.com/cduck/drawsvg
- Documentation: https://drawsvg.readthedocs.io/

**svg.py**
- Lightweight and Pythonic
- Fluent interface
- Good for simpler diagrams
- Installation: `pip install svg.py`
- Repository: https://github.com/orsinium-labs/svg.py

### Specialized Diagram Types

**blockdiag / seqdiag / nwdiag / actdiag**
- Family of libraries for specific diagram types:
  - blockdiag: Block diagrams, flowcharts
  - seqdiag: Sequence diagrams
  - nwdiag: Network diagrams
  - actdiag: Activity diagrams
- Text-based DSL that compiles to SVG
- Installation: `pip install blockdiag seqdiag nwdiag actdiag`
- Repository: https://github.com/blockdiag/blockdiag
- Documentation: http://blockdiag.com/

**schemdraw**
- Electronic circuit diagrams
- Schematic drawing library
- Extensive component library
- Installation: `pip install schemdraw`
- Repository: https://github.com/cdelker/schemdraw
- Documentation: https://schemdraw.readthedocs.io/

**Pygal**
- Charts and graphs with built-in interactivity
- Beautiful default styling
- Supports animations
- Installation: `pip install pygal`
- Repository: https://github.com/Kozea/pygal
- Documentation: https://www.pygal.org/

**diagrams**
- Cloud architecture diagrams
- Supports AWS, Azure, GCP, Kubernetes icons
- Uses Graphviz underneath
- Installation: `pip install diagrams`
- Repository: https://github.com/mingrammer/diagrams
- Documentation: https://diagrams.mingrammer.com/

## Animation Support

### Using drawsvg (Recommended for animations)

```python
import drawsvg as draw

d = draw.Drawing(200, 100)
circle = draw.Circle(50, 50, 20, fill='blue')
circle.append_anim(draw.Animate('cx', '0s', '50;150;50', dur='2s', repeatCount='indefinite'))
d.append(circle)
d.save_svg('animated.svg')
```

### Using svgwrite (More control)

```python
import svgwrite

dwg = svgwrite.Drawing('animated.svg', size=(200, 100))
circle = dwg.circle(center=(50, 50), r=20, fill='blue')
circle.add(dwg.animate('cx', values='50;150;50', dur='2s', repeatCount='indefinite'))
dwg.add(circle)
dwg.save()
```

## Implementation Considerations

### Tool Design

Each tool should:
1. Have a clear, descriptive name (e.g., `create_flowchart`, `create_circuit_diagram`)
2. Accept well-defined parameters (diagram spec, styling options, etc.)
3. Return SVG in a consistent format
4. Provide good error messages

### Return Format Options

Consider how to return the generated SVG:
- **Raw SVG XML string** — Simple, client can handle it
- **Base64 encoded** — For binary transport if needed
- **File path** — If server has accessible file system
- **Data URI** — Ready for embedding

### Tool Discovery

Provide clear descriptions in the MCP tool definitions so Claude knows:
- What each tool does
- What parameters it accepts
- What kind of output it produces
- Examples of appropriate use cases

### Dependency Management

Some considerations:
- **Cairo** (for drawsvg PNG rendering) — Optional, only if you need raster output
- **Graphviz** (for diagrams library) — System dependency
- Most pure-Python libraries have minimal dependencies
- Use virtual environment for development

### Error Handling

Handle common failure modes:
- Invalid diagram specifications
- Missing required parameters
- Library-specific errors
- Resource limits (very large diagrams)

## Development Approach

### Phase 1: MVP with Single Library
- Set up basic MCP server structure
- Implement one tool with one library (e.g., drawsvg for general diagrams)
- Test with Claude Code
- Establish return format and error handling patterns

### Phase 2: Add Specialized Libraries
- Add tools for specific diagram types
- Implement consistent error handling across all tools
- Document each tool's capabilities

### Phase 3: Polish and Extend
- Add styling options
- Support for themes/templates
- Animation presets
- Batch generation capabilities

## Example Tool Definitions

```python
tools = [
    {
        "name": "create_animated_diagram",
        "description": "Create an animated SVG diagram with custom shapes and animations",
        "inputSchema": {
            "type": "object",
            "properties": {
                "elements": {"type": "array", "description": "List of shapes to draw"},
                "animations": {"type": "array", "description": "Animation specifications"},
                "width": {"type": "number", "default": 400},
                "height": {"type": "number", "default": 300}
            }
        }
    },
    {
        "name": "create_flowchart",
        "description": "Create a flowchart or block diagram from a specification",
        "inputSchema": {
            "type": "object",
            "properties": {
                "spec": {"type": "string", "description": "Diagram specification in blockdiag syntax"},
                "style": {"type": "string", "description": "Optional styling preset"}
            }
        }
    },
    # ... more tools
]
```

## Resources

### MCP Documentation
- MCP Specification: https://modelcontextprotocol.io/
- Python MCP SDK: https://github.com/modelcontextprotocol/python-sdk
- MCP Servers Examples: https://github.com/modelcontextprotocol/servers

### SVG References
- MDN SVG Tutorial: https://developer.mozilla.org/en-US/docs/Web/SVG
- SMIL Animation: https://developer.mozilla.org/en-US/docs/Web/SVG/SVG_animation_with_SMIL
- SVG Specification: https://www.w3.org/TR/SVG2/

### Additional Tools
- SVG Optimizer (SVGO): https://github.com/svg/svgo (for production)
- SVG Path Editor: https://yqnn.github.io/svg-path-editor/ (for testing)

## Next Steps

1. Set up project structure with Python virtual environment
2. Install MCP Python SDK
3. Choose starting library (recommend drawsvg for versatility)
4. Implement basic server with one tool
5. Test with Claude Code
6. Iterate and expand tool set

## Notes

- Each library is independent — no conflicts between them
- Start simple, add complexity as needed
- Focus on clear tool descriptions for Claude to understand capabilities
- Consider caching/performance for complex diagrams
- Think about security if accepting arbitrary diagram specifications
