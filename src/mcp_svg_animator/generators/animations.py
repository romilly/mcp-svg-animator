"""Animated SVG diagram generator using drawsvg."""

from typing import Annotated, Literal, cast

import drawsvg as draw
from pydantic import BaseModel, Field

from .position_resolver import resolve_positions
from .specs.animation_spec import AnimationSpec
from .specs.circle_spec import CircleSpec
from .specs.element_spec import ElementSpec
from .specs.rectangle_spec import RectangleSpec
from .specs.transform_animation_spec import TransformAnimationSpec


class LineSpec(BaseModel):
    """Specification for a line element."""

    id: str | None = None
    type: Literal["line"] = "line"
    x1: float = 0
    y1: float = 0
    x2: float = 100
    y2: float = 100
    stroke: str = "black"
    stroke_width: float = Field(default=2, alias="stroke_width")
    marker_end: str | None = None
    animations: list[AnimationSpec] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class TextSpec(BaseModel):
    """Specification for a text element."""

    id: str | None = None
    type: Literal["text"] = "text"
    text: str = ""
    font_size: float = 16
    x: float = 0
    y: float = 0
    fill: str = "black"
    text_anchor: str | None = None
    animations: list[AnimationSpec] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class MoveToSpec(BaseModel):
    """Move to a point without drawing."""

    type: Literal["move_to"] = "move_to"
    x: float
    y: float

    def to_path_data(self) -> str:
        return f"M{self.x},{self.y}"


class LineToSpec(BaseModel):
    """Draw a line to a point."""

    type: Literal["line_to"] = "line_to"
    x: float
    y: float

    def to_path_data(self) -> str:
        return f"L{self.x},{self.y}"


class CubicBezierSpec(BaseModel):
    """Draw a cubic bezier curve."""

    type: Literal["cubic_bezier"] = "cubic_bezier"
    x1: float  # First control point
    y1: float
    x2: float  # Second control point
    y2: float
    x: float  # End point
    y: float

    def to_path_data(self) -> str:
        return f"C{self.x1},{self.y1} {self.x2},{self.y2} {self.x},{self.y}"


class QuadraticBezierSpec(BaseModel):
    """Draw a quadratic bezier curve."""

    type: Literal["quadratic_bezier"] = "quadratic_bezier"
    x1: float  # Control point
    y1: float
    x: float  # End point
    y: float

    def to_path_data(self) -> str:
        return f"Q{self.x1},{self.y1} {self.x},{self.y}"


class ArcSpec(BaseModel):
    """Draw an elliptical arc."""

    type: Literal["arc"] = "arc"
    rx: float  # X radius
    ry: float  # Y radius
    rotation: float = 0  # X-axis rotation in degrees
    large_arc: bool = False  # Large arc flag
    sweep: bool = True  # Sweep direction (True = clockwise)
    x: float  # End point
    y: float

    def to_path_data(self) -> str:
        large = 1 if self.large_arc else 0
        sweep = 1 if self.sweep else 0
        return f"A{self.rx},{self.ry} {self.rotation} {large} {sweep} {self.x},{self.y}"


class CloseSpec(BaseModel):
    """Close the path back to the start."""

    type: Literal["close"] = "close"

    def to_path_data(self) -> str:
        return "Z"


SegmentSpec = Annotated[
    MoveToSpec | LineToSpec | CubicBezierSpec | QuadraticBezierSpec | ArcSpec | CloseSpec,
    Field(discriminator="type"),
]


def _segments_to_path_data(segments: list[SegmentSpec]) -> str:
    """Convert a list of segment specs to SVG path data."""
    return " ".join(seg.to_path_data() for seg in segments)


class PathSpec(BaseModel):
    """Specification for a path element."""

    id: str | None = None
    type: Literal["path"] = "path"
    d: str | None = None  # SVG path data (raw)
    segments: list[SegmentSpec] = Field(default_factory=list)  # Segment-based path
    fill: str = "none"
    stroke: str = "black"
    stroke_width: float = Field(default=1, alias="stroke_width")
    animations: list[AnimationSpec] = Field(default_factory=list)

    model_config = {"populate_by_name": True}

    def get_path_data(self) -> str:
        """Get the SVG path data, either from d or by converting segments."""
        if self.d is not None:
            return self.d
        if self.segments:
            return _segments_to_path_data(self.segments)
        raise ValueError("PathSpec requires either 'd' or 'segments'")


class GroupSpec(BaseModel):
    """Specification for a group element."""

    id: str | None = None
    type: Literal["group"] = "group"
    transform: str | None = None
    transform_animations: list[TransformAnimationSpec] = Field(default_factory=list)
    elements: list[dict] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


def create_animated_diagram(arguments: dict) -> str:
    """Create an animated SVG diagram.

    Args:
        arguments: Dictionary containing:
            - width: Canvas width (default 400)
            - height: Canvas height (default 300)
            - elements: List of shape specifications. Position attributes
                can use relative references like "element_id.x + 70".

    Returns:
        SVG content as a string.
    """
    width = arguments.get("width", 400)
    height = arguments.get("height", 300)
    elements = arguments.get("elements", [])

    # Resolve relative position references before creating elements
    resolved_elements = resolve_positions(elements)

    d = draw.Drawing(width, height)

    for element in resolved_elements:
        shape = _create_element(element)
        d.append(shape)

    return cast(str, d.as_svg())


def _create_circle(spec: CircleSpec):
    return draw.Circle(
        spec.cx,
        spec.cy,
        spec.r,
        fill=spec.fill,
        stroke=spec.stroke,
        stroke_width=spec.stroke_width,
    )


def _create_rectangle(spec: RectangleSpec):
    kwargs: dict[str, float] = {}
    if spec.rx is not None:
        kwargs["rx"] = spec.rx
    if spec.ry is not None:
        kwargs["ry"] = spec.ry
    return draw.Rectangle(
        spec.x,
        spec.y,
        spec.width,
        spec.height,
        fill=spec.fill,
        stroke=spec.stroke,
        stroke_width=spec.stroke_width,
        **kwargs,
    )


def _create_arrow_marker(color: str = "black"):
    """Create an arrow marker for line endings."""
    arrow = draw.Marker(-0.1, -0.5, 0.9, 0.5, scale=4, orient="auto", id="arrow")
    arrow.append(draw.Lines(-0.1, -0.5, -0.1, 0.5, 0.9, 0, fill=color, close=True))
    return arrow


def _create_line(spec: LineSpec):
    kwargs = {}
    if spec.marker_end == "arrow":
        kwargs["marker_end"] = _create_arrow_marker(spec.stroke)
    return draw.Line(
        spec.x1,
        spec.y1,
        spec.x2,
        spec.y2,
        stroke=spec.stroke,
        stroke_width=spec.stroke_width,
        **kwargs,
    )


def _create_text(spec: TextSpec):
    kwargs: dict[str, str] = {}
    if spec.text_anchor:
        kwargs["text_anchor"] = spec.text_anchor
    return draw.Text(
        spec.text,
        spec.font_size,
        spec.x,
        spec.y,
        fill=spec.fill,
        **kwargs,
    )


def _create_path(spec: PathSpec):
    return draw.Path(
        d=spec.get_path_data(),
        fill=spec.fill,
        stroke=spec.stroke,
        stroke_width=spec.stroke_width,
    )


_ELEMENT_CREATORS = {
    "circle": (CircleSpec, _create_circle),
    "rectangle": (RectangleSpec, _create_rectangle),
    "line": (LineSpec, _create_line),
    "text": (TextSpec, _create_text),
    "path": (PathSpec, _create_path),
}


def _apply_animations(element, animations: list[AnimationSpec]):
    """Apply animations to an SVG element."""
    for spec in animations:
        anim = draw.Animate(
            spec.attribute,
            spec.dur,
            from_or_values=spec.from_value,
            to=spec.to_value,
            repeatCount=spec.repeat_count,
        )
        element.append_anim(anim)


def _create_group(spec: GroupSpec):
    """Create a group element with its children."""
    kwargs = {}
    if spec.transform:
        kwargs["transform"] = spec.transform

    group = draw.Group(**kwargs)

    for child_dict in spec.elements:
        child = _create_element(child_dict)
        group.append(child)

    # Apply transform animations
    for anim in spec.transform_animations:
        group.append(_create_transform_animation(anim))

    return group


def _create_transform_animation(spec: TransformAnimationSpec):
    """Create an animateTransform element."""
    attrs = [
        'attributeName="transform"',
        f'type="{spec.type}"',
        f'dur="{spec.dur}"',
    ]
    if spec.values:
        attrs.append(f'values="{spec.values}"')
    if spec.from_value:
        attrs.append(f'from="{spec.from_value}"')
    if spec.to_value:
        attrs.append(f'to="{spec.to_value}"')
    if spec.repeat_count:
        attrs.append(f'repeatCount="{spec.repeat_count}"')
    if spec.additive:
        attrs.append(f'additive="{spec.additive}"')

    return draw.Raw(f'<animateTransform {" ".join(attrs)}/>')


def _create_element(spec_dict: dict):
    """Create a single SVG element from a specification."""
    element_type = spec_dict.get("type")
    if element_type is None:
        raise ValueError("Element spec missing 'type' key")

    # Handle groups specially due to recursive nature
    if element_type == "group":
        spec = GroupSpec.model_validate(spec_dict)
        return _create_group(spec)

    creator_info = _ELEMENT_CREATORS.get(element_type)
    if creator_info is None:
        raise ValueError(f"Unknown element type: {element_type}")

    spec_class, creator = creator_info
    spec = spec_class.model_validate(spec_dict)
    element = creator(spec)

    if spec.animations:
        _apply_animations(element, spec.animations)

    return element
