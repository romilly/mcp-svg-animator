"""Tests for relative position resolution."""

import pytest
from hamcrest import assert_that, equal_to

from mcp_svg_animator.generators.position_resolver import resolve_positions


class TestResolvePositions:
    """Tests for resolve_positions function."""

    def test_resolves_simple_reference(self):
        elements = [
            {"id": "box1", "type": "rectangle", "x": 10, "y": 20},
            {"id": "box2", "type": "rectangle", "x": "box1.x", "y": "box1.y"},
        ]

        resolved = resolve_positions(elements)

        assert_that(resolved[1]["x"], equal_to(10))
        assert_that(resolved[1]["y"], equal_to(20))

    def test_resolves_reference_with_addition(self):
        elements = [
            {"id": "box1", "type": "rectangle", "x": 10, "y": 20},
            {"id": "box2", "type": "rectangle", "x": "box1.x + 70", "y": "box1.y"},
        ]

        resolved = resolve_positions(elements)

        assert_that(resolved[1]["x"], equal_to(80))

    def test_resolves_reference_with_subtraction(self):
        elements = [
            {"id": "box1", "type": "rectangle", "x": 100, "y": 50},
            {"id": "box2", "type": "rectangle", "x": "box1.x - 30", "y": "box1.y - 10"},
        ]

        resolved = resolve_positions(elements)

        assert_that(resolved[1]["x"], equal_to(70))
        assert_that(resolved[1]["y"], equal_to(40))

    def test_resolves_circle_position(self):
        elements = [
            {"id": "circle1", "type": "circle", "cx": 100, "cy": 150},
            {"id": "circle2", "type": "circle", "cx": "circle1.cx + 50", "cy": "circle1.cy"},
        ]

        resolved = resolve_positions(elements)

        assert_that(resolved[1]["cx"], equal_to(150))
        assert_that(resolved[1]["cy"], equal_to(150))

    def test_leaves_numeric_values_unchanged(self):
        elements = [
            {"id": "box1", "type": "rectangle", "x": 10, "y": 20, "width": 100},
        ]

        resolved = resolve_positions(elements)

        assert_that(resolved[0]["x"], equal_to(10))
        assert_that(resolved[0]["y"], equal_to(20))
        assert_that(resolved[0]["width"], equal_to(100))

    def test_raises_error_for_unknown_element_reference(self):
        elements = [
            {"id": "box1", "type": "rectangle", "x": "unknown.x", "y": 20},
        ]

        with pytest.raises(ValueError, match="Unknown element reference: unknown"):
            resolve_positions(elements)

    def test_raises_error_for_unknown_attribute_reference(self):
        elements = [
            {"id": "box1", "type": "rectangle", "x": 10, "y": 20},
            {"id": "box2", "type": "rectangle", "x": "box1.unknown", "y": 20},
        ]

        with pytest.raises(ValueError, match="Unknown attribute 'unknown' on element 'box1'"):
            resolve_positions(elements)

    def test_resolves_chained_references(self):
        elements = [
            {"id": "box1", "type": "rectangle", "x": 10, "y": 20},
            {"id": "box2", "type": "rectangle", "x": "box1.x + 50", "y": 20},
            {"id": "box3", "type": "rectangle", "x": "box2.x + 50", "y": 20},
        ]

        resolved = resolve_positions(elements)

        assert_that(resolved[1]["x"], equal_to(60))
        assert_that(resolved[2]["x"], equal_to(110))
