"""Tests for YAML diagram loading."""

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
