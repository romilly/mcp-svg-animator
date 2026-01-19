"""Spec classes for SVG elements and animations."""

from .animation_spec import AnimationSpec
from .circle_spec import CircleSpec
from .element_spec import ElementSpec
from .line_spec import LineSpec
from .rectangle_spec import RectangleSpec
from .text_spec import TextSpec
from .transform_animation_spec import TransformAnimationSpec

__all__ = [
    "AnimationSpec",
    "CircleSpec",
    "ElementSpec",
    "LineSpec",
    "RectangleSpec",
    "TextSpec",
    "TransformAnimationSpec",
]
