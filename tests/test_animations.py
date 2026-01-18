"""Tests for the animations generator."""

import pytest
from hamcrest import assert_that, contains_string

from mcp_svg_animator.generators.animations import create_animated_diagram


class TestCreateAnimatedDiagram:
    """Tests for create_animated_diagram function."""

    def test_creates_svg_with_default_dimensions(self):
        result = create_animated_diagram({})

        assert_that(result, contains_string('width="400"'))
        assert_that(result, contains_string('height="300"'))

    def test_creates_svg_with_custom_dimensions(self):
        result = create_animated_diagram({"width": 800, "height": 600})

        assert_that(result, contains_string('width="800"'))
        assert_that(result, contains_string('height="600"'))

    def test_creates_circle_element(self):
        result = create_animated_diagram({
            "elements": [{"type": "circle", "cx": 100, "cy": 150, "r": 25, "fill": "red"}]
        })

        assert_that(result, contains_string('<circle'))
        assert_that(result, contains_string('cx="100'))
        assert_that(result, contains_string('cy="150'))
        assert_that(result, contains_string('r="25'))
        assert_that(result, contains_string('fill="red"'))

    def test_creates_rectangle_element(self):
        result = create_animated_diagram({
            "elements": [{"type": "rectangle", "x": 10, "y": 20, "width": 100, "height": 50, "fill": "green"}]
        })

        assert_that(result, contains_string('<rect'))
        assert_that(result, contains_string('x="10'))
        assert_that(result, contains_string('y="20'))
        assert_that(result, contains_string('width="100'))
        assert_that(result, contains_string('height="50'))
        assert_that(result, contains_string('fill="green"'))

    def test_creates_line_element(self):
        result = create_animated_diagram({
            "elements": [{"type": "line", "x1": 0, "y1": 0, "x2": 100, "y2": 100, "stroke": "black"}]
        })

        # drawsvg renders lines as path elements with M (move) and L (line) commands
        assert_that(result, contains_string('<path'))
        assert_that(result, contains_string('M0'))
        assert_that(result, contains_string('L100'))
        assert_that(result, contains_string('stroke="black"'))

    def test_creates_text_element(self):
        result = create_animated_diagram({
            "elements": [{"type": "text", "content": "Hello", "x": 50, "y": 75, "font_size": 24}]
        })

        assert_that(result, contains_string('<text'))
        assert_that(result, contains_string('Hello'))

    def test_handles_empty_elements_list(self):
        result = create_animated_diagram({"elements": []})

        assert_that(result, contains_string('<svg'))
        assert_that(result, contains_string('</svg>'))

    def test_raises_error_for_unknown_element_type(self):
        with pytest.raises(ValueError, match="Unknown element type: unknown_shape"):
            create_animated_diagram({
                "elements": [{"type": "unknown_shape", "x": 10}]
            })

    def test_raises_error_for_missing_type_key(self):
        with pytest.raises(ValueError, match="Element spec missing 'type' key"):
            create_animated_diagram({
                "elements": [{"x": 10, "y": 20}]
            })

    def test_creates_multiple_elements(self):
        result = create_animated_diagram({
            "elements": [
                {"type": "circle", "cx": 50, "cy": 50, "r": 20, "fill": "blue"},
                {"type": "rectangle", "x": 100, "y": 100, "width": 50, "height": 30, "fill": "red"},
            ]
        })

        assert_that(result, contains_string('<circle'))
        assert_that(result, contains_string('<rect'))

    def test_creates_circle_with_animation(self):
        result = create_animated_diagram({
            "elements": [{
                "type": "circle",
                "cx": 50,
                "cy": 50,
                "r": 20,
                "fill": "blue",
                "animations": [{
                    "attribute": "cx",
                    "from_value": "50",
                    "to_value": "150",
                    "dur": "2s",
                    "repeatCount": "indefinite",
                }]
            }]
        })

        assert_that(result, contains_string('<circle'))
        assert_that(result, contains_string('<animate'))
        assert_that(result, contains_string('attributeName="cx"'))
        assert_that(result, contains_string('from="50"'))
        assert_that(result, contains_string('to="150"'))
        assert_that(result, contains_string('dur="2s"'))
        assert_that(result, contains_string('repeatCount="indefinite"'))
