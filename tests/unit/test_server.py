"""Tests for MCP server functionality."""

import asyncio
from pathlib import Path

import pytest
from hamcrest import assert_that, contains_string, is_not

from mcp_svg_animator.config import clear_config_cache
from mcp_svg_animator.server import call_tool


@pytest.fixture(autouse=True)
def reset_config(tmp_path: Path, monkeypatch):
    """Set up config to allow writing to tmp_path for all tests."""
    import os

    clear_config_cache()
    # Preserve original home for Playwright browser cache
    original_home = os.environ.get("HOME", "")
    monkeypatch.setenv("PLAYWRIGHT_BROWSERS_PATH", f"{original_home}/.cache/ms-playwright")
    monkeypatch.setenv("HOME", str(tmp_path))
    config_dir = tmp_path / ".config" / "mcp-svg-animator"
    config_dir.mkdir(parents=True)
    (config_dir / "config.yaml").write_text(f"""
file_output:
  allowed:
    - path: "{tmp_path}"
      types: [svg, png, webm]
""")
    yield
    clear_config_cache()


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


class TestFileOutputPermissions:
    """Tests for file output permission checking."""

    def test_denies_svg_write_when_not_configured(self, tmp_path: Path, monkeypatch):
        """Writing SVG to unconfigured path raises PermissionError."""
        # Override config to allow only a different path
        clear_config_cache()
        config_dir = tmp_path / ".config" / "mcp-svg-animator"
        (config_dir / "config.yaml").write_text(f"""
file_output:
  allowed:
    - path: "{tmp_path}/allowed"
      types: [svg]
""")
        disallowed_file = tmp_path / "disallowed" / "output.svg"
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
        with pytest.raises(PermissionError, match="not allowed"):
            asyncio.run(
                call_tool(
                    "create_svg_from_yaml",
                    {"yaml_spec": yaml_spec, "output_path": str(disallowed_file)},
                )
            )

    def test_denies_png_write_when_type_not_allowed(self, tmp_path: Path, monkeypatch):
        """Writing PNG when only SVG is allowed raises PermissionError."""
        clear_config_cache()
        config_dir = tmp_path / ".config" / "mcp-svg-animator"
        (config_dir / "config.yaml").write_text(f"""
file_output:
  allowed:
    - path: "{tmp_path}"
      types: [svg]
""")
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
        with pytest.raises(PermissionError, match="not allowed"):
            asyncio.run(
                call_tool(
                    "create_svg_from_yaml",
                    {"yaml_spec": yaml_spec, "png_path": str(png_file)},
                )
            )

    def test_denies_all_writes_when_no_config(self, tmp_path: Path, monkeypatch):
        """With no config file, all file writes are denied."""
        clear_config_cache()
        # Remove the config file
        config_file = tmp_path / ".config" / "mcp-svg-animator" / "config.yaml"
        config_file.unlink()

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
        with pytest.raises(PermissionError, match="not allowed"):
            asyncio.run(
                call_tool(
                    "create_svg_from_yaml",
                    {"yaml_spec": yaml_spec, "output_path": str(output_file)},
                )
            )
