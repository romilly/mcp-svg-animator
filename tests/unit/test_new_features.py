"""Tests for new SVG features: ellipse element and extended attributes."""

from hamcrest import assert_that, contains_string, equal_to

from mcp_svg_animator.generators.animations import create_animated_diagram


class TestEllipseElement:
    """Tests for ellipse element support."""

    def test_creates_ellipse_element(self):
        result = create_animated_diagram({
            "elements": [{
                "type": "ellipse",
                "cx": 100,
                "cy": 100,
                "rx": 50,
                "ry": 25,
                "fill": "white",
                "stroke": "black",
            }]
        })

        assert_that(result, contains_string('<ellipse'))
        assert_that(result, contains_string('cx="100'))
        assert_that(result, contains_string('cy="100'))
        assert_that(result, contains_string('rx="50'))
        assert_that(result, contains_string('ry="25'))
        assert_that(result, contains_string('fill="white"'))
        assert_that(result, contains_string('stroke="black"'))

    def test_ellipse_with_default_values(self):
        result = create_animated_diagram({
            "elements": [{"type": "ellipse"}]
        })

        assert_that(result, contains_string('<ellipse'))

    def test_ellipse_with_animation(self):
        result = create_animated_diagram({
            "elements": [{
                "type": "ellipse",
                "cx": 100,
                "cy": 100,
                "rx": 50,
                "ry": 25,
                "animations": [{
                    "attribute": "rx",
                    "from_value": "50",
                    "to_value": "100",
                    "dur": "2s",
                    "repeatCount": "indefinite",
                }]
            }]
        })

        assert_that(result, contains_string('<ellipse'))
        assert_that(result, contains_string('<animate'))
        assert_that(result, contains_string('attributeName="rx"'))


class TestStrokeDasharray:
    """Tests for stroke-dasharray attribute on lines."""

    def test_line_with_stroke_dasharray(self):
        result = create_animated_diagram({
            "elements": [{
                "type": "line",
                "x1": 0,
                "y1": 0,
                "x2": 100,
                "y2": 0,
                "stroke": "black",
                "stroke_width": 2,
                "stroke-dasharray": "5,3",
            }]
        })

        assert_that(result, contains_string('stroke-dasharray="5,3"'))


class TestOpacity:
    """Tests for opacity attribute on elements."""

    def test_circle_with_opacity(self):
        result = create_animated_diagram({
            "elements": [{
                "type": "circle",
                "cx": 50,
                "cy": 50,
                "r": 25,
                "fill": "blue",
                "opacity": 0.5,
            }]
        })

        assert_that(result, contains_string('opacity="0.5"'))

    def test_rectangle_with_fill_opacity(self):
        result = create_animated_diagram({
            "elements": [{
                "type": "rectangle",
                "x": 10,
                "y": 10,
                "width": 100,
                "height": 50,
                "fill": "red",
                "fill-opacity": 0.7,
            }]
        })

        assert_that(result, contains_string('fill-opacity="0.7"'))

    def test_line_with_stroke_opacity(self):
        result = create_animated_diagram({
            "elements": [{
                "type": "line",
                "x1": 0,
                "y1": 0,
                "x2": 100,
                "y2": 100,
                "stroke": "black",
                "stroke-opacity": 0.5,
            }]
        })

        assert_that(result, contains_string('stroke-opacity="0.5"'))


class TestTransformOnElements:
    """Tests for transform attribute on non-group elements."""

    def test_circle_with_transform(self):
        result = create_animated_diagram({
            "elements": [{
                "type": "circle",
                "cx": 50,
                "cy": 50,
                "r": 25,
                "transform": "rotate(45 50 50)",
            }]
        })

        assert_that(result, contains_string('transform="rotate(45 50 50)"'))


class TestTextFontAttributes:
    """Tests for font attributes on text elements."""

    def test_text_with_font_family(self):
        result = create_animated_diagram({
            "elements": [{
                "type": "text",
                "text": "Hello",
                "x": 50,
                "y": 50,
                "font-family": "Arial, sans-serif",
            }]
        })

        assert_that(result, contains_string('font-family="Arial, sans-serif"'))

    def test_text_with_font_weight(self):
        result = create_animated_diagram({
            "elements": [{
                "type": "text",
                "text": "Bold",
                "x": 50,
                "y": 50,
                "font-weight": "bold",
            }]
        })

        assert_that(result, contains_string('font-weight="bold"'))

    def test_text_with_font_style(self):
        result = create_animated_diagram({
            "elements": [{
                "type": "text",
                "text": "Italic",
                "x": 50,
                "y": 50,
                "font-style": "italic",
            }]
        })

        assert_that(result, contains_string('font-style="italic"'))

    def test_text_with_dominant_baseline(self):
        result = create_animated_diagram({
            "elements": [{
                "type": "text",
                "text": "Centered",
                "x": 50,
                "y": 50,
                "dominant-baseline": "middle",
            }]
        })

        assert_that(result, contains_string('dominant-baseline="middle"'))

    def test_text_with_all_font_attributes(self):
        result = create_animated_diagram({
            "elements": [{
                "type": "text",
                "text": "Styled",
                "x": 50,
                "y": 50,
                "font-family": "Arial, sans-serif",
                "font_size": 24,
                "font-weight": "bold",
                "text_anchor": "middle",
            }]
        })

        assert_that(result, contains_string('font-family="Arial, sans-serif"'))
        assert_that(result, contains_string('font-weight="bold"'))
        assert_that(result, contains_string('text-anchor="middle"'))


class TestStrokeLinecapLinejoin:
    """Tests for stroke-linecap and stroke-linejoin attributes."""

    def test_line_with_stroke_linecap(self):
        result = create_animated_diagram({
            "elements": [{
                "type": "line",
                "x1": 0,
                "y1": 0,
                "x2": 100,
                "y2": 0,
                "stroke": "black",
                "stroke_width": 10,
                "stroke-linecap": "round",
            }]
        })

        assert_that(result, contains_string('stroke-linecap="round"'))

    def test_path_with_stroke_linejoin(self):
        result = create_animated_diagram({
            "elements": [{
                "type": "path",
                "d": "M10,10 L50,50 L90,10",
                "stroke": "black",
                "fill": "none",
                "stroke-linejoin": "round",
            }]
        })

        assert_that(result, contains_string('stroke-linejoin="round"'))


class TestHyphenatedAttributeAliases:
    """Tests for hyphenated YAML attribute names."""

    def test_ellipse_with_hyphenated_stroke_width(self):
        """stroke-width in YAML should work for ellipse."""
        result = create_animated_diagram({
            "elements": [{
                "type": "ellipse",
                "cx": 100,
                "cy": 100,
                "rx": 50,
                "ry": 25,
                "stroke": "#333",
                "stroke-width": 2,
            }]
        })

        # SVG may render as "2" or "2.0"
        assert 'stroke-width="2"' in result or 'stroke-width="2.0"' in result

    def test_text_with_hyphenated_font_size(self):
        """font-size in YAML should work."""
        result = create_animated_diagram({
            "elements": [{
                "type": "text",
                "x": 50,
                "y": 50,
                "text": "Large",
                "font-size": 24,
            }]
        })

        # SVG may render as "24" or "24.0"
        assert 'font-size="24"' in result or 'font-size="24.0"' in result

    def test_text_with_hyphenated_text_anchor(self):
        """text-anchor in YAML should work."""
        result = create_animated_diagram({
            "elements": [{
                "type": "text",
                "x": 100,
                "y": 50,
                "text": "Centered",
                "text-anchor": "middle",
            }]
        })

        assert_that(result, contains_string('text-anchor="middle"'))

    def test_text_with_transform(self):
        """transform should be passed through for text elements."""
        result = create_animated_diagram({
            "elements": [{
                "type": "text",
                "x": 100,
                "y": 100,
                "text": "Rotated",
                "transform": "rotate(45, 100, 100)",
            }]
        })

        assert_that(result, contains_string('transform="rotate(45, 100, 100)"'))

    def test_rectangle_with_hyphenated_stroke_width(self):
        """stroke-width in YAML should work for rectangle."""
        result = create_animated_diagram({
            "elements": [{
                "type": "rectangle",
                "x": 10,
                "y": 10,
                "width": 100,
                "height": 50,
                "stroke": "black",
                "stroke-width": 3,
            }]
        })

        # SVG may render as "3" or "3.0"
        assert 'stroke-width="3"' in result or 'stroke-width="3.0"' in result
