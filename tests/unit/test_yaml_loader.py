"""Tests for YAML diagram loading."""

from pathlib import Path

import pytest
from hamcrest import assert_that, contains_string

from mcp_svg_animator.generators.yaml_loader import create_diagram_from_yaml


class TestCreateDiagramFromYaml:
    """Tests for create_diagram_from_yaml function."""

    def test_creates_svg_from_yaml(self):
        yaml_content = """
width: 400
height: 300
elements:
  - type: circle
    cx: 100
    cy: 150
    r: 25
    fill: red
"""
        result = create_diagram_from_yaml(yaml_content)

        assert_that(result, contains_string('<svg'))
        assert_that(result, contains_string('<circle'))
        assert_that(result, contains_string('fill="red"'))

    def test_creates_animated_svg_from_yaml(self):
        yaml_content = """
width: 400
height: 300
elements:
  - type: circle
    cx: 50
    cy: 50
    r: 20
    fill: blue
    animations:
      - attribute: cx
        dur: 2s
        from_value: "50"
        to_value: "150"
        repeatCount: indefinite
"""
        result = create_diagram_from_yaml(yaml_content)

        assert_that(result, contains_string('<circle'))
        assert_that(result, contains_string('<animate'))
        assert_that(result, contains_string('attributeName="cx"'))

    def test_raises_error_for_invalid_yaml(self):
        yaml_content = """
width: 400
elements:
  - type: unknown_type
    x: 10
"""
        with pytest.raises(ValueError, match="Unknown element type"):
            create_diagram_from_yaml(yaml_content)

    def test_raises_error_for_missing_required_field(self):
        yaml_content = """
width: 400
elements:
  - cx: 100
    cy: 150
"""
        with pytest.raises(ValueError, match="Element spec missing 'type' key"):
            create_diagram_from_yaml(yaml_content)


class TestDefinitions:
    """Tests for definition and use functionality."""

    def test_expands_local_definition(self):
        yaml_content = """
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
"""
        result = create_diagram_from_yaml(yaml_content)

        assert_that(result, contains_string('<circle'))
        assert_that(result, contains_string('r="25'))
        assert_that(result, contains_string('fill="red"'))
        assert_that(result, contains_string('cx="50'))

    def test_definition_with_override(self):
        yaml_content = """
definitions:
  my_circle:
    type: circle
    r: 25
    fill: red

elements:
  - use: my_circle
    cx: 100
    cy: 100
    fill: blue
"""
        result = create_diagram_from_yaml(yaml_content)

        assert_that(result, contains_string('fill="blue"'))

    def test_raises_error_for_unknown_definition(self):
        yaml_content = """
elements:
  - use: nonexistent
    cx: 50
"""
        with pytest.raises(ValueError, match="Unknown definition: nonexistent"):
            create_diagram_from_yaml(yaml_content)


class TestLibraryImports:
    """Tests for library file imports."""

    def test_loads_definition_from_library(self, tmp_path: Path):
        # Create a library file
        library_file = tmp_path / "shapes.yaml"
        library_file.write_text("""
blue_square:
  type: rectangle
  width: 50
  height: 50
  fill: blue
""")

        yaml_content = f"""
libraries:
  - {library_file}

elements:
  - use: blue_square
    x: 10
    y: 20
"""
        result = create_diagram_from_yaml(yaml_content)

        assert_that(result, contains_string('<rect'))
        assert_that(result, contains_string('width="50'))
        assert_that(result, contains_string('fill="blue"'))
        assert_that(result, contains_string('x="10'))

    def test_local_definitions_override_library(self, tmp_path: Path):
        # Create a library file
        library_file = tmp_path / "shapes.yaml"
        library_file.write_text("""
my_shape:
  type: circle
  r: 10
  fill: red
""")

        yaml_content = f"""
libraries:
  - {library_file}

definitions:
  my_shape:
    type: rectangle
    width: 100
    height: 50
    fill: green

elements:
  - use: my_shape
    x: 0
    y: 0
"""
        result = create_diagram_from_yaml(yaml_content)

        # Local definition should win
        assert_that(result, contains_string('<rect'))
        assert_that(result, contains_string('fill="green"'))

    def test_raises_error_for_missing_library(self):
        yaml_content = """
libraries:
  - /nonexistent/library.yaml

elements:
  - type: circle
    cx: 50
    cy: 50
    r: 25
"""
        with pytest.raises(FileNotFoundError):
            create_diagram_from_yaml(yaml_content)


class TestRectangleElements:
    """Tests for rectangle element handling."""

    def test_rectangle_with_rounded_corners(self):
        """Rectangle with rx should have rounded corners."""
        yaml_content = """
width: 400
height: 300
elements:
  - type: rectangle
    x: 50
    y: 50
    width: 100
    height: 60
    rx: 10
    fill: blue
"""
        result = create_diagram_from_yaml(yaml_content)

        assert_that(result, contains_string('rx="10'))


class TestLineElements:
    """Tests for line element handling."""

    def test_line_with_arrow_marker(self):
        """Line with marker_end: arrow should have an arrowhead."""
        yaml_content = """
width: 400
height: 300
elements:
  - type: line
    x1: 50
    y1: 150
    x2: 350
    y2: 150
    stroke: black
    marker_end: arrow
"""
        result = create_diagram_from_yaml(yaml_content)

        assert_that(result, contains_string('<marker'))
        assert_that(result, contains_string('marker-end="url(#arrow)"'))


class TestTextElements:
    """Tests for text element handling."""

    def test_text_attribute_appears_in_svg(self):
        """Text specified with 'text' attribute should appear in output."""
        yaml_content = """
width: 400
height: 300
elements:
  - type: text
    x: 100
    y: 150
    text: "Hello World"
    fill: black
"""
        result = create_diagram_from_yaml(yaml_content)

        assert_that(result, contains_string("Hello World"))

    def test_text_anchor_centers_text(self):
        """Text with text_anchor middle should have text-anchor attribute."""
        yaml_content = """
width: 400
height: 300
elements:
  - type: text
    x: 200
    y: 150
    text: "Centered"
    text_anchor: middle
"""
        result = create_diagram_from_yaml(yaml_content)

        assert_that(result, contains_string('text-anchor="middle"'))
