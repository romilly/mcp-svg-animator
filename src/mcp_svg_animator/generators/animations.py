"""Animated SVG diagram generator using drawsvg."""

from typing import cast

import drawsvg as draw


def create_animated_diagram(arguments: dict) -> str:
    """Create an animated SVG diagram.

    Args:
        arguments: Dictionary containing:
            - width: Canvas width (default 400)
            - height: Canvas height (default 300)
            - elements: List of shape specifications
            - animations: List of animation specifications

    Returns:
        SVG content as a string.
    """
    width = arguments.get("width", 400)
    height = arguments.get("height", 300)
    elements = arguments.get("elements", [])
    animations = arguments.get("animations", [])

    d = draw.Drawing(width, height)

    for element in elements:
        shape = _create_element(element)
        d.append(shape)

    return cast(str, d.as_svg())


def _create_circle(spec: dict):
    return draw.Circle(
        spec.get("cx", 50),
        spec.get("cy", 50),
        spec.get("r", 25),
        fill=spec.get("fill", "blue"),
        stroke=spec.get("stroke", "none"),
        stroke_width=spec.get("stroke_width", 0),
    )


def _create_rectangle(spec: dict):
    return draw.Rectangle(
        spec.get("x", 0),
        spec.get("y", 0),
        spec.get("width", 100),
        spec.get("height", 50),
        fill=spec.get("fill", "blue"),
        stroke=spec.get("stroke", "none"),
        stroke_width=spec.get("stroke_width", 0),
    )


def _create_line(spec: dict):
    return draw.Line(
        spec.get("x1", 0),
        spec.get("y1", 0),
        spec.get("x2", 100),
        spec.get("y2", 100),
        stroke=spec.get("stroke", "black"),
        stroke_width=spec.get("stroke_width", 2),
    )


def _create_text(spec: dict):
    return draw.Text(
        spec.get("content", ""),
        spec.get("font_size", 16),
        spec.get("x", 0),
        spec.get("y", 0),
        fill=spec.get("fill", "black"),
    )


_ELEMENT_CREATORS = {
    "circle": _create_circle,
    "rectangle": _create_rectangle,
    "line": _create_line,
    "text": _create_text,
}


def _create_element(spec: dict):
    """Create a single SVG element from a specification."""
    element_type = spec.get("type")
    if element_type is None:
        raise ValueError("Element spec missing 'type' key")
    creator = _ELEMENT_CREATORS.get(element_type)
    if creator is None:
        raise ValueError(f"Unknown element type: {element_type}")
    return creator(spec)
