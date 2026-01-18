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
