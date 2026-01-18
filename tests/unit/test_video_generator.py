"""Tests for video generation from SVG animations."""

from pathlib import Path

import pytest
from hamcrest import assert_that, greater_than, is_

from mcp_svg_animator.generators.video_generator import create_video_from_svg


class TestCreateVideoFromSvg:
    """Tests for create_video_from_svg function."""

    def test_creates_video_file(self, tmp_path: Path):
        svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">
  <circle cx="100" cy="100" r="50" fill="red">
    <animate attributeName="r" from="50" to="80" dur="1s" repeatCount="indefinite"/>
  </circle>
</svg>"""
        output_path = tmp_path / "animation.webm"

        create_video_from_svg(svg_content, str(output_path), duration_ms=1000)

        assert_that(output_path.exists(), is_(True))
        assert_that(output_path.stat().st_size, greater_than(0))

    def test_creates_video_with_custom_dimensions(self, tmp_path: Path):
        svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300">
  <rect x="50" y="50" width="100" height="100" fill="blue"/>
</svg>"""
        output_path = tmp_path / "custom.webm"

        create_video_from_svg(
            svg_content,
            str(output_path),
            duration_ms=500,
            width=400,
            height=300,
        )

        assert_that(output_path.exists(), is_(True))
