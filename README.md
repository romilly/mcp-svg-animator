# MCP SVG Animator

An MCP server for creating animated SVG diagrams.
You can create a diagram from text input, photos of sketches and YAML specifications.

You don't normally need to use YAML; just tell Claude code what you want, upload photos of sketches,
and then iterate until you've got what you want.

You can see some sample inputs and outputs on the [Demo Page](https://htmlpreview.github.io/?https://github.com/romilly/mcp-svg-animator/blob/main/examples/demo.html)

## Features

- **YAML-based specification** - Define diagrams in readable YAML
- **Multiple shape types** - circle, rectangle, line, text, path, group
- **Path segments** - Build curves with move_to, line_to, cubic_bezier, quadratic_bezier, arc
- **SMIL animations** - Animate attributes and transforms
- **Reusable definitions** - Define once, use many times
- **Library imports** - Share definitions across diagrams
- **Relative positioning** - Reference other elements' positions
- **Video export** - Record animations to .webm video

## Installation

```bash
# Clone the repository
git clone https://github.com/romilly/mcp-svg-animator.git
cd mcp-svg-animator

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (for video generation)
playwright install chromium
```

## Usage with Claude Code

Register the MCP server globally:

```bash
claude mcp add --scope user svg-animator -- /path/to/venv/bin/python -m mcp_svg_animator
```

Then in any Claude Code session, **ask Claude code to create animations**:

> "Create an animated SVG of a red circle that pulses"

See [docs/usage.md](docs/usage.md) for more details.

## YAML Example

```yaml
width: 400
height: 300

definitions:
  person:
    type: group
    elements:
      - type: circle
        cx: 0
        cy: 0
        r: 20
        stroke: black
        fill: none

elements:
  - use: person
    id: person1
    transform: translate(80, 120)
    transform_animations:
      - type: translate
        from: "80 120"
        to: "250 120"
        dur: 3s
        repeatCount: indefinite

  - use: person
    id: person2
    transform: translate(320, 120)
```

See [docs/specification.md](docs/specification.md) for the complete YAML format reference.

## MCP Tools

You don't need to explicitly invoke these. Ask Claude code to create the animation you describe,
and it will invoke the relevant tools.

| Tool | Description |
|------|-------------|
| `create_svg_from_yaml` | Generate SVG from YAML specification |
| `create_animation_video` | Record SVG animation to .webm video |

## Development

```bash
# Install test dependencies (after following Installation steps above)
pip install -r requirements-test.txt

# Run tests
pytest

# Type checking
pyright src/
```

## Examples

See the `examples/` directory for sample YAML files and generated SVGs:

- `demo.yaml` - Basic shapes
- `stick_figure.yaml` - Static stick figure
- `stick_figure_waving.yaml` - Animated waving
- `curves.yaml` - Bezier curves and arcs
- `meeting.yaml` - Two figures, one walks to meet the other

## License

MIT
