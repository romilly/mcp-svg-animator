# MCP SVG Animator Specification

A YAML-based specification for creating animated SVG diagrams.

## Document Structure

```yaml
width: 400          # Canvas width in pixels (default: 400)
height: 300         # Canvas height in pixels (default: 300)

libraries:          # Optional: external library files
  - path/to/shapes.yaml

definitions:        # Optional: reusable element definitions
  my_shape:
    type: circle
    r: 25

elements:           # List of elements to render
  - type: circle
    cx: 100
    cy: 100
```

## Element Types

### Circle

```yaml
- type: circle
  id: my_circle       # Optional identifier for references
  cx: 100             # Center x coordinate
  cy: 100             # Center y coordinate
  r: 50               # Radius
  fill: red           # Fill color (default: blue)
  stroke: black       # Stroke color (default: none)
  stroke_width: 2     # Stroke width (default: 0)
```

### Rectangle

```yaml
- type: rectangle
  id: my_rect
  x: 10               # Top-left x coordinate
  y: 20               # Top-left y coordinate
  width: 100          # Width
  height: 50          # Height
  rx: 10              # Horizontal corner radius (optional)
  ry: 10              # Vertical corner radius (optional)
  fill: green
  stroke: black
  stroke_width: 1
```

### Line

```yaml
- type: line
  x1: 0               # Start x
  y1: 0               # Start y
  x2: 100             # End x
  y2: 100             # End y
  stroke: black       # Stroke color (default: black)
  stroke_width: 2     # Stroke width (default: 2)
  marker_end: arrow   # Add arrowhead at end (optional)
```

### Text

```yaml
- type: text
  text: "Hello"       # Text content
  x: 50               # x position
  y: 75               # y position
  font_size: 24       # Font size (default: 16)
  fill: black         # Text color (default: black)
  text_anchor: middle # Alignment: start, middle, end (optional)
```

### Path

Paths can be defined with raw SVG path data or using segment specs.

**Raw path data:**
```yaml
- type: path
  d: "M10,10 C20,20 40,20 50,10"
  stroke: black
  fill: none
```

**Segment-based path:**
```yaml
- type: path
  segments:
    - type: move_to
      x: 10
      y: 20
    - type: line_to
      x: 50
      y: 20
    - type: cubic_bezier
      x1: 60        # First control point
      y1: 20
      x2: 70        # Second control point
      y2: 50
      x: 50         # End point
      y: 60
    - type: close
  stroke: black
  fill: lightblue
```

**Available segment types:**

| Segment | Parameters | Description |
|---------|------------|-------------|
| `move_to` | x, y | Move without drawing |
| `line_to` | x, y | Draw line to point |
| `cubic_bezier` | x1, y1, x2, y2, x, y | Cubic Bézier curve |
| `quadratic_bezier` | x1, y1, x, y | Quadratic Bézier curve |
| `arc` | rx, ry, rotation, large_arc, sweep, x, y | Elliptical arc |
| `close` | (none) | Close path to start |

### Group

Groups contain child elements and can have transforms and animations.

```yaml
- type: group
  id: my_group
  transform: translate(100, 100)
  elements:
    - type: circle
      cx: 0
      cy: 0
      r: 25
    - type: rectangle
      x: -20
      y: 30
      width: 40
      height: 20
```

## Animations

### Attribute Animations

Animate any attribute of an element using SMIL animation.

```yaml
- type: circle
  cx: 50
  cy: 50
  r: 20
  fill: blue
  animations:
    - attribute: r           # Attribute to animate
      from_value: "20"       # Starting value
      to_value: "40"         # Ending value
      dur: 1s                # Duration
      repeatCount: indefinite  # Repeat (or a number)
```

### Transform Animations

Animate transforms on groups (rotate, translate, scale, skew).

```yaml
- type: group
  transform: translate(100, 100)
  transform_animations:
    - type: rotate           # rotate, translate, scale, skewX, skewY
      values: "0;360"        # Keyframe values
      dur: 2s
      repeatCount: indefinite
      additive: sum          # Optional: sum or replace
  elements:
    - type: rectangle
      x: -25
      y: -25
      width: 50
      height: 50
```

**Transform animation with from/to:**
```yaml
transform_animations:
  - type: translate
    from: "0 0"
    to: "100 0"
    dur: 3s
    repeatCount: indefinite
```

## Definitions and Reuse

### Local Definitions

Define reusable elements within a document.

```yaml
definitions:
  red_circle:
    type: circle
    r: 25
    fill: red

elements:
  - use: red_circle
    id: circle1
    cx: 50
    cy: 50
  - use: red_circle
    id: circle2
    cx: 150
    cy: 50
    fill: blue          # Override properties
```

### Library Files

Import definitions from external files.

**Library file (shapes.yaml):**
```yaml
stick_figure:
  type: group
  elements:
    - type: circle
      cx: 0
      cy: 0
      r: 20
    # ... more elements

arrow:
  type: path
  d: "M0,0 L20,10 L0,20 Z"
  fill: black
```

**Using libraries:**
```yaml
libraries:
  - shapes.yaml

elements:
  - use: stick_figure
    id: person1
    transform: translate(100, 150)
```

Local definitions override library definitions with the same name.

## Relative Positioning

Reference other elements' positions using expressions.

```yaml
elements:
  - id: box1
    type: rectangle
    x: 10
    y: 20
    width: 100
    height: 50

  - id: box2
    type: rectangle
    x: "box1.x + 120"      # Relative to box1
    y: "box1.y"            # Same y as box1
    width: 100
    height: 50
```

Supported attributes: `x`, `y`, `cx`, `cy`, `x1`, `y1`, `x2`, `y2`, `width`, `height`, `r`

## Video Generation

SVG animations can be converted to video using the `create_animation_video` tool.

```
Input: SVG content with SMIL animations
Output: .webm video file
Parameters:
  - output_path: Where to save the video
  - duration_ms: Recording duration in milliseconds (default: 3000)
```

## Complete Example

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
        fill: none
        stroke: black
        stroke_width: 2
      - type: line
        x1: 0
        y1: 20
        x2: 0
        y2: 80
        stroke: black
        stroke_width: 2
      - type: line
        x1: 0
        y1: 40
        x2: -30
        y2: 60
        stroke: black
        stroke_width: 2
      - type: line
        x1: 0
        y1: 40
        x2: 30
        y2: 60
        stroke: black
        stroke_width: 2

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
