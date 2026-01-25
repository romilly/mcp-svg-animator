# Using the SVG Animator in Claude Code

The `svg-animator` MCP server is registered globally and available in all your Claude Code sessions.

## Quick Start

In any Claude Code session, ask Claude to create an SVG animation:

> "Create an animated SVG of a red circle that pulses"

Claude will use the `create_svg_from_yaml` tool automatically.

## Example Prompts

**Simple shape:**
> "Create an SVG with a blue rectangle"

**Animation:**
> "Create an SVG with a circle that moves from left to right"

**Complex animation:**
> "Create two stick figures, one walking toward the other"

## YAML Format Reference

You can also provide YAML directly:

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
```

### Supported Shapes

- `circle` - cx, cy, r, fill, stroke
- `rectangle` - x, y, width, height, fill, stroke
- `line` - x1, y1, x2, y2, stroke, stroke_width
- `text` - content, x, y, font_size, fill
- `path` - d (raw SVG path) or segments (list of move_to, line_to, cubic_bezier, etc.)
- `group` - elements, transform, transform_animations

### Animations

**Attribute animations** (on shapes):
```yaml
- type: circle
  cx: 50
  cy: 50
  r: 20
  animations:
    - attribute: r
      from_value: "20"
      to_value: "40"
      dur: 1s
      repeatCount: indefinite
```

**Transform animations** (on groups):
```yaml
- type: group
  transform: translate(100, 100)
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
```

### Reusable Definitions

Define once, use many times:
```yaml
definitions:
  button:
    type: group
    elements:
      - type: rectangle
        width: 80
        height: 30
        fill: blue

elements:
  - use: button
    id: btn1
    transform: translate(50, 50)
  - use: button
    id: btn2
    transform: translate(50, 100)
```

## Saving the Output

Ask Claude to save the SVG:
> "Create a bouncing ball animation and save it to animation.svg"
## Direct Python API

You can also use the SVG generation functionality directly from Python code, without the MCP server.

For the complete YAML schema reference, see [specification.md](specification.md).

### Basic Usage

```python
from mcp_svg_animator import yaml_to_svg, yaml_to_svg_file

# Generate SVG content from YAML string
yaml_spec = '''
width: 400
height: 300
elements:
  - type: circle
    cx: 200
    cy: 150
    r: 50
    fill: blue
'''
svg_content = yaml_to_svg(yaml_spec)

# Or save directly to file
yaml_to_svg_file(yaml_spec, "output.svg")
```

### Load from YAML Files

```python
from mcp_svg_animator import yaml_file_to_svg, yaml_file_to_svg_file

# Load YAML from file and get SVG content
svg_content = yaml_file_to_svg("diagram.yaml")

# Load YAML and save SVG directly
yaml_file_to_svg_file("diagram.yaml", "output.svg")
```

### Build Specs Programmatically

```python
from mcp_svg_animator import dict_to_svg, dict_to_svg_file

# Create from a Python dictionary
spec = {
    "width": 200,
    "height": 200,
    "elements": [
        {"type": "circle", "cx": 100, "cy": 100, "r": 50, "fill": "green"}
    ]
}
svg_content = dict_to_svg(spec)
dict_to_svg_file(spec, "circle.svg")
```

### Generate PNG Images

```python
from mcp_svg_animator import yaml_to_png

yaml_to_png('''
width: 200
height: 200
elements:
  - type: circle
    cx: 100
    cy: 100
    r: 50
    fill: red
''', "circle.png")
```

### Generate Videos from Animations

```python
from mcp_svg_animator import yaml_to_video

yaml_to_video('''
width: 200
height: 200
elements:
  - type: circle
    cx: 100
    cy: 100
    r: 50
    fill: red
    animations:
      - attribute: r
        values: "50;30;50"
        dur: 1s
        repeatCount: indefinite
''', "animation.webm", duration_ms=5000)
```

### Available Functions

| Function | Description |
|----------|-------------|
| `yaml_to_svg(yaml_spec)` | Convert YAML string to SVG content |
| `yaml_to_svg_file(yaml_spec, path)` | Convert YAML string and save to file |
| `yaml_file_to_svg(yaml_path)` | Load YAML file and convert to SVG content |
| `yaml_file_to_svg_file(yaml_path, svg_path)` | Load YAML file and save SVG to file |
| `dict_to_svg(spec)` | Convert Python dict to SVG content |
| `dict_to_svg_file(spec, path)` | Convert Python dict and save to file |
| `yaml_to_png(yaml_spec, path)` | Convert YAML to PNG image |
| `yaml_to_video(yaml_spec, path, duration_ms)` | Convert animated YAML to video |