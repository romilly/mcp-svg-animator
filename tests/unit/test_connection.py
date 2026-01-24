"""Tests for connection elements."""

import pytest
from hamcrest import assert_that, equal_to, contains_string

from mcp_svg_animator.generators.specs.connection_spec import ConnectionSpec
from mcp_svg_animator.generators.position_resolver import get_element_center


class TestGetElementCenter:
    """Tests for get_element_center function."""

    def test_returns_center_for_circle(self):
        element = {"type": "circle", "cx": 100, "cy": 150, "r": 25}

        center = get_element_center(element)

        assert_that(center, equal_to((100, 150)))

    def test_returns_center_for_ellipse(self):
        element = {"type": "ellipse", "cx": 200, "cy": 100, "rx": 50, "ry": 25}

        center = get_element_center(element)

        assert_that(center, equal_to((200, 100)))

    def test_returns_center_for_rectangle(self):
        element = {"type": "rectangle", "x": 50, "y": 50, "width": 100, "height": 60}

        center = get_element_center(element)

        assert_that(center, equal_to((100, 80)))  # 50+100/2, 50+60/2

    def test_returns_position_for_text(self):
        element = {"type": "text", "x": 200, "y": 150}

        center = get_element_center(element)

        assert_that(center, equal_to((200, 150)))

    def test_raises_error_for_unsupported_type(self):
        element = {"type": "group"}

        with pytest.raises(ValueError, match="Cannot calculate center for element type: group"):
            get_element_center(element)

    def test_raises_error_for_open_path_with_segments(self):
        element = {
            "type": "path",
            "segments": [
                {"type": "move_to", "x": 0, "y": 0},
                {"type": "line_to", "x": 100, "y": 0},
                {"type": "line_to", "x": 100, "y": 100},
            ]
        }

        with pytest.raises(ValueError, match="Cannot calculate center for open path"):
            get_element_center(element)

    def test_raises_error_for_open_path_with_raw_d(self):
        element = {"type": "path", "d": "M0,0 L100,0 L100,100"}

        with pytest.raises(ValueError, match="Cannot calculate center for open path"):
            get_element_center(element)

    def test_returns_centroid_for_closed_path_with_segments(self):
        # Triangle: (0,0), (100,0), (50,100)
        element = {
            "type": "path",
            "segments": [
                {"type": "move_to", "x": 0, "y": 0},
                {"type": "line_to", "x": 100, "y": 0},
                {"type": "line_to", "x": 50, "y": 100},
                {"type": "close"},
            ]
        }

        center = get_element_center(element)

        # Centroid = average of vertices: (0+100+50)/3, (0+0+100)/3
        assert_that(center, equal_to((50.0, 100 / 3)))

    def test_returns_centroid_for_closed_path_with_raw_d(self):
        # Triangle: (0,0), (100,0), (50,100)
        element = {"type": "path", "d": "M0,0 L100,0 L50,100 Z"}

        center = get_element_center(element)

        # Centroid = average of vertices
        assert_that(center, equal_to((50.0, 100 / 3)))

    def test_returns_centroid_for_closed_path_with_lowercase_z(self):
        element = {"type": "path", "d": "M0,0 L100,0 L50,100 z"}

        center = get_element_center(element)

        assert_that(center, equal_to((50.0, 100 / 3)))


class TestTwoPhaseResolution:
    """Tests for two-phase connection resolution."""

    def test_connection_can_reference_element_defined_later(self):
        from mcp_svg_animator.generators.position_resolver import resolve_positions

        elements = [
            {"type": "connection", "from": "box1", "to": "box2"},
            {"id": "box1", "type": "rectangle", "x": 50, "y": 50, "width": 100, "height": 60},
            {"id": "box2", "type": "circle", "cx": 300, "cy": 80, "r": 40},
        ]

        resolved = resolve_positions(elements)

        # Connection should have resolved coordinates
        connection = resolved[0]
        assert_that(connection["x1"], equal_to(100))  # box1 center: 50+100/2
        assert_that(connection["y1"], equal_to(80))   # box1 center: 50+60/2
        assert_that(connection["x2"], equal_to(300))  # box2 center: cx
        assert_that(connection["y2"], equal_to(80))   # box2 center: cy

    def test_connections_appear_first_in_resolved_list(self):
        from mcp_svg_animator.generators.position_resolver import resolve_positions

        elements = [
            {"id": "box1", "type": "rectangle", "x": 50, "y": 50, "width": 100, "height": 60},
            {"type": "connection", "from": "box1", "to": "box2"},
            {"id": "box2", "type": "circle", "cx": 300, "cy": 80, "r": 40},
        ]

        resolved = resolve_positions(elements)

        # Connection should be moved to front
        assert_that(resolved[0]["type"], equal_to("connection"))
        assert_that(resolved[1]["type"], equal_to("rectangle"))
        assert_that(resolved[2]["type"], equal_to("circle"))

    def test_connection_preserves_other_attributes(self):
        from mcp_svg_animator.generators.position_resolver import resolve_positions

        elements = [
            {"type": "connection", "from": "box1", "to": "box2", "stroke": "red", "stroke-width": 3},
            {"id": "box1", "type": "circle", "cx": 100, "cy": 100, "r": 25},
            {"id": "box2", "type": "circle", "cx": 200, "cy": 100, "r": 25},
        ]

        resolved = resolve_positions(elements)

        connection = resolved[0]
        assert_that(connection["stroke"], equal_to("red"))
        assert_that(connection["stroke-width"], equal_to(3))

    def test_raises_error_for_unknown_from_reference(self):
        from mcp_svg_animator.generators.position_resolver import resolve_positions

        elements = [
            {"type": "connection", "from": "unknown", "to": "box1"},
            {"id": "box1", "type": "circle", "cx": 100, "cy": 100, "r": 25},
        ]

        with pytest.raises(ValueError, match="Unknown element reference: unknown"):
            resolve_positions(elements)

    def test_raises_error_for_unknown_to_reference(self):
        from mcp_svg_animator.generators.position_resolver import resolve_positions

        elements = [
            {"type": "connection", "from": "box1", "to": "unknown"},
            {"id": "box1", "type": "circle", "cx": 100, "cy": 100, "r": 25},
        ]

        with pytest.raises(ValueError, match="Unknown element reference: unknown"):
            resolve_positions(elements)

    def test_connection_to_closed_path_uses_centroid(self):
        from mcp_svg_animator.generators.position_resolver import resolve_positions

        elements = [
            {"type": "connection", "from": "circle1", "to": "triangle"},
            {"id": "circle1", "type": "circle", "cx": 50, "cy": 50, "r": 25},
            {
                "id": "triangle",
                "type": "path",
                "segments": [
                    {"type": "move_to", "x": 0, "y": 0},
                    {"type": "line_to", "x": 100, "y": 0},
                    {"type": "line_to", "x": 50, "y": 100},
                    {"type": "close"},
                ]
            },
        ]

        resolved = resolve_positions(elements)

        connection = resolved[0]
        assert_that(connection["x1"], equal_to(50))  # circle center
        assert_that(connection["y1"], equal_to(50))
        # Triangle centroid: (0+100+50)/3, (0+0+100)/3
        assert_that(connection["x2"], equal_to(50.0))
        assert_that(connection["y2"], equal_to(100 / 3))

    def test_connection_to_open_path_raises_error(self):
        from mcp_svg_animator.generators.position_resolver import resolve_positions

        elements = [
            {"type": "connection", "from": "circle1", "to": "open_path"},
            {"id": "circle1", "type": "circle", "cx": 50, "cy": 50, "r": 25},
            {
                "id": "open_path",
                "type": "path",
                "segments": [
                    {"type": "move_to", "x": 0, "y": 0},
                    {"type": "line_to", "x": 100, "y": 0},
                ]
            },
        ]

        with pytest.raises(ValueError, match="Cannot calculate center for open path"):
            resolve_positions(elements)


class TestConnectionRendering:
    """Tests for connection rendering in SVG output."""

    def test_connection_renders_as_line(self):
        from mcp_svg_animator.generators.animations import create_animated_diagram

        result = create_animated_diagram({
            "elements": [
                {"id": "box1", "type": "circle", "cx": 100, "cy": 100, "r": 25},
                {"id": "box2", "type": "circle", "cx": 200, "cy": 100, "r": 25},
                {"type": "connection", "from": "box1", "to": "box2"},
            ]
        })

        # Connection should render as a path (drawsvg uses path for lines)
        assert_that(result, contains_string('<path'))
        # Path should contain coordinates for the centers
        assert_that(result, contains_string('M100'))  # box1 center x
        assert_that(result, contains_string('L200'))  # box2 center x

    def test_connection_with_arrow(self):
        from mcp_svg_animator.generators.animations import create_animated_diagram

        result = create_animated_diagram({
            "elements": [
                {"id": "box1", "type": "circle", "cx": 100, "cy": 100, "r": 25},
                {"id": "box2", "type": "circle", "cx": 200, "cy": 100, "r": 25},
                {"type": "connection", "from": "box1", "to": "box2", "marker-end": "arrow"},
            ]
        })

        # Should include marker definition for arrow
        assert_that(result, contains_string('marker'))

    def test_connection_appears_before_shapes(self):
        from mcp_svg_animator.generators.animations import create_animated_diagram

        result = create_animated_diagram({
            "elements": [
                {"id": "box1", "type": "circle", "cx": 100, "cy": 100, "r": 25},
                {"type": "connection", "from": "box1", "to": "box2"},
                {"id": "box2", "type": "circle", "cx": 200, "cy": 100, "r": 25},
            ]
        })

        # Connection (path for line) should appear before circles
        path_pos = result.find('<path')
        circle_pos = result.find('<circle')
        assert path_pos < circle_pos


class TestTextBackground:
    """Tests for text background panels."""

    def test_text_spec_accepts_background(self):
        from mcp_svg_animator.generators.specs.text_spec import TextSpec

        spec = TextSpec.model_validate({
            "type": "text",
            "text": "Hello",
            "x": 100,
            "y": 50,
            "background": "white",
        })

        assert_that(spec.background, equal_to("white"))

    def test_text_spec_accepts_background_padding(self):
        from mcp_svg_animator.generators.specs.text_spec import TextSpec

        spec = TextSpec.model_validate({
            "type": "text",
            "text": "Hello",
            "x": 100,
            "y": 50,
            "background": "white",
            "background-padding": 8,
        })

        assert_that(spec.background_padding, equal_to(8))

    def test_text_spec_defaults_background_padding_to_4(self):
        from mcp_svg_animator.generators.specs.text_spec import TextSpec

        spec = TextSpec.model_validate({
            "type": "text",
            "text": "Hello",
            "x": 100,
            "y": 50,
            "background": "white",
        })

        assert_that(spec.background_padding, equal_to(4))

    def test_text_with_background_renders_group_with_rect(self):
        from mcp_svg_animator.generators.animations import create_animated_diagram

        result = create_animated_diagram({
            "elements": [{
                "type": "text",
                "text": "Label",
                "x": 100,
                "y": 50,
                "background": "white",
            }]
        })

        # Should create a group containing rect and text
        assert_that(result, contains_string('<g>'))
        assert_that(result, contains_string('<rect'))
        assert_that(result, contains_string('<text'))
        assert_that(result, contains_string('Label'))

    def test_text_without_background_renders_just_text(self):
        from mcp_svg_animator.generators.animations import create_animated_diagram

        result = create_animated_diagram({
            "elements": [{
                "type": "text",
                "text": "Label",
                "x": 100,
                "y": 50,
            }]
        })

        # Should not have a group wrapper
        assert_that(result, contains_string('<text'))
        assert_that(result, contains_string('Label'))
        # No extra rect for background
        assert result.count('<rect') == 0


class TestConnectionSpec:
    """Tests for ConnectionSpec class."""

    def test_creates_connection_with_from_and_to(self):
        spec = ConnectionSpec.model_validate({
            "type": "connection",
            "from": "box1",
            "to": "box2",
        })

        assert_that(spec.from_id, equal_to("box1"))
        assert_that(spec.to_id, equal_to("box2"))

    def test_defaults_stroke_to_black(self):
        spec = ConnectionSpec.model_validate({
            "type": "connection",
            "from": "box1",
            "to": "box2",
        })

        assert_that(spec.stroke, equal_to("black"))

    def test_defaults_stroke_width_to_2(self):
        spec = ConnectionSpec.model_validate({
            "type": "connection",
            "from": "box1",
            "to": "box2",
        })

        assert_that(spec.stroke_width, equal_to(2))

    def test_accepts_marker_end(self):
        spec = ConnectionSpec.model_validate({
            "type": "connection",
            "from": "box1",
            "to": "box2",
            "marker-end": "arrow",
        })

        assert_that(spec.marker_end, equal_to("arrow"))
