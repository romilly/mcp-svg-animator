"""Animated SVG diagram generator using drawsvg."""

from typing import Literal, cast

import drawsvg as draw
from pydantic import BaseModel, Field


class AnimationSpec(BaseModel):
    """Specification for an SVG animation."""

    attribute: str
    dur: str
    from_value: str | None = None
    to_value: str | None = None
    repeat_count: str | None = Field(default=None, alias="repeatCount")

    model_config = {"populate_by_name": True}


class ElementSpec(BaseModel):
    """Base specification for SVG elements."""

    id: str | None = None
    fill: str = "blue"
    stroke: str = "none"
    stroke_width: float = Field(default=0, alias="stroke_width")
    animations: list[AnimationSpec] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class CircleSpec(ElementSpec):
    """Specification for a circle element."""

    type: Literal["circle"] = "circle"
    cx: float = 50
    cy: float = 50
    r: float = 25


class RectangleSpec(ElementSpec):
    """Specification for a rectangle element."""

    type: Literal["rectangle"] = "rectangle"
    x: float = 0
    y: float = 0
    width: float = 100
    height: float = 50


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
    animations: list[AnimationSpec] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class TextSpec(BaseModel):
    """Specification for a text element."""

    id: str | None = None
    type: Literal["text"] = "text"
    content: str = ""
    font_size: float = 16
    x: float = 0
    y: float = 0
    fill: str = "black"
    animations: list[AnimationSpec] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


def create_animated_diagram(arguments: dict) -> str:
    """Create an animated SVG diagram.

    Args:
        arguments: Dictionary containing:
            - width: Canvas width (default 400)
            - height: Canvas height (default 300)
            - elements: List of shape specifications

    Returns:
        SVG content as a string.
    """
    width = arguments.get("width", 400)
    height = arguments.get("height", 300)
    elements = arguments.get("elements", [])

    d = draw.Drawing(width, height)

    for element in elements:
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
    return draw.Rectangle(
        spec.x,
        spec.y,
        spec.width,
        spec.height,
        fill=spec.fill,
        stroke=spec.stroke,
        stroke_width=spec.stroke_width,
    )


def _create_line(spec: LineSpec):
    return draw.Line(
        spec.x1,
        spec.y1,
        spec.x2,
        spec.y2,
        stroke=spec.stroke,
        stroke_width=spec.stroke_width,
    )


def _create_text(spec: TextSpec):
    return draw.Text(
        spec.content,
        spec.font_size,
        spec.x,
        spec.y,
        fill=spec.fill,
    )


_ELEMENT_CREATORS = {
    "circle": (CircleSpec, _create_circle),
    "rectangle": (RectangleSpec, _create_rectangle),
    "line": (LineSpec, _create_line),
    "text": (TextSpec, _create_text),
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


def _create_element(spec_dict: dict):
    """Create a single SVG element from a specification."""
    element_type = spec_dict.get("type")
    if element_type is None:
        raise ValueError("Element spec missing 'type' key")

    creator_info = _ELEMENT_CREATORS.get(element_type)
    if creator_info is None:
        raise ValueError(f"Unknown element type: {element_type}")

    spec_class, creator = creator_info
    spec = spec_class.model_validate(spec_dict)
    element = creator(spec)

    if spec.animations:
        _apply_animations(element, spec.animations)

    return element
