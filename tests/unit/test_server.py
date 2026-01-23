"""Tests for MCP server functionality."""

import asyncio
from pathlib import Path

from hamcrest import assert_that, contains_string, is_not

from mcp_svg_animator.server import call_tool


class TestCreateSvgFromYamlWithOutputPath:
    """Tests for create_svg_from_yaml with output_path parameter."""

    def test_writes_svg_to_file_when_output_path_provided(self, tmp_path: Path):
        """When output_path is provided, SVG should be written to that file."""
        output_file = tmp_path / "output.svg"
        yaml_spec = """
width: 200
height: 100
elements:
  - type: circle
    cx: 50
    cy: 50
    r: 25
    fill: red
"""
        result = asyncio.run(
            call_tool(
                "create_svg_from_yaml",
                {"yaml_spec": yaml_spec, "output_path": str(output_file)},
            )
        )

        assert output_file.exists()
        svg_content = output_file.read_text()
        assert_that(svg_content, contains_string("<svg"))
        assert_that(svg_content, contains_string("<circle"))

    def test_returns_confirmation_when_output_path_provided(self, tmp_path: Path):
        """When output_path is provided, return confirmation instead of SVG content."""
        output_file = tmp_path / "output.svg"
        yaml_spec = """
width: 200
height: 100
elements:
  - type: circle
    cx: 50
    cy: 50
    r: 25
    fill: red
"""
        result = asyncio.run(
            call_tool(
                "create_svg_from_yaml",
                {"yaml_spec": yaml_spec, "output_path": str(output_file)},
            )
        )

        response_text = result[0].text
        assert_that(response_text, contains_string(str(output_file)))
        assert_that(response_text, is_not(contains_string("<svg")))

    def test_returns_svg_content_when_no_output_path(self):
        """When output_path is not provided, return SVG content (existing behavior)."""
        yaml_spec = """
width: 200
height: 100
elements:
  - type: circle
    cx: 50
    cy: 50
    r: 25
    fill: red
"""
        result = asyncio.run(
            call_tool("create_svg_from_yaml", {"yaml_spec": yaml_spec})
        )

        response_text = result[0].text
        assert_that(response_text, contains_string("<svg"))
        assert_that(response_text, contains_string("<circle"))


class TestCreateSvgFromYamlWithPngPath:
    """Tests for create_svg_from_yaml with png_path parameter."""

    def test_creates_png_file_when_png_path_provided(self, tmp_path: Path):
        """When png_path is provided, PNG should be created at that path."""
        png_file = tmp_path / "output.png"
        yaml_spec = """
width: 200
height: 100
elements:
  - type: circle
    cx: 50
    cy: 50
    r: 25
    fill: red
"""
        asyncio.run(
            call_tool(
                "create_svg_from_yaml",
                {"yaml_spec": yaml_spec, "png_path": str(png_file)},
            )
        )

        assert png_file.exists()
        # Verify it's a valid PNG (starts with PNG signature)
        png_content = png_file.read_bytes()
        assert png_content[:8] == b"\x89PNG\r\n\x1a\n"

    def test_returns_confirmation_when_png_path_provided(self, tmp_path: Path):
        """When png_path is provided, return confirmation mentioning PNG file."""
        png_file = tmp_path / "output.png"
        yaml_spec = """
width: 200
height: 100
elements:
  - type: circle
    cx: 50
    cy: 50
    r: 25
    fill: red
"""
        result = asyncio.run(
            call_tool(
                "create_svg_from_yaml",
                {"yaml_spec": yaml_spec, "png_path": str(png_file)},
            )
        )

        response_text = result[0].text
        assert_that(response_text, contains_string(str(png_file)))

    def test_creates_both_svg_and_png_when_both_paths_provided(self, tmp_path: Path):
        """When both output_path and png_path provided, both files are created."""
        svg_file = tmp_path / "output.svg"
        png_file = tmp_path / "output.png"
        yaml_spec = """
width: 200
height: 100
elements:
  - type: circle
    cx: 50
    cy: 50
    r: 25
    fill: red
"""
        result = asyncio.run(
            call_tool(
                "create_svg_from_yaml",
                {
                    "yaml_spec": yaml_spec,
                    "output_path": str(svg_file),
                    "png_path": str(png_file),
                },
            )
        )

        assert svg_file.exists()
        assert png_file.exists()
        response_text = result[0].text
        assert_that(response_text, contains_string(str(svg_file)))
        assert_that(response_text, contains_string(str(png_file)))
