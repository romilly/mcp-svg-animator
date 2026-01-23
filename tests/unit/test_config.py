"""Tests for file output configuration."""

from pathlib import Path

import pytest
from hamcrest import assert_that, is_

from mcp_svg_animator.config import clear_config_cache, is_path_allowed, load_config


@pytest.fixture(autouse=True)
def reset_config_cache():
    """Clear config cache before and after each test."""
    clear_config_cache()
    yield
    clear_config_cache()


class TestLoadConfig:
    """Tests for loading configuration."""

    def test_returns_empty_config_when_no_file_exists(self, tmp_path: Path, monkeypatch):
        """When config file doesn't exist, return empty allowed list."""
        monkeypatch.setenv("HOME", str(tmp_path))
        config = load_config()
        assert config["file_output"]["allowed"] == []

    def test_loads_config_from_file(self, tmp_path: Path, monkeypatch):
        """Config file is loaded and parsed correctly."""
        monkeypatch.setenv("HOME", str(tmp_path))
        config_dir = tmp_path / ".config" / "mcp-svg-animator"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.yaml"
        config_file.write_text("""
file_output:
  allowed:
    - path: "~/diagrams"
      types: [svg, png]
""")
        config = load_config()
        assert len(config["file_output"]["allowed"]) == 1
        assert config["file_output"]["allowed"][0]["path"] == "~/diagrams"
        assert config["file_output"]["allowed"][0]["types"] == ["svg", "png"]


class TestIsPathAllowed:
    """Tests for path permission checking."""

    def test_denies_when_no_config(self, tmp_path: Path, monkeypatch):
        """When no config exists, all paths are denied."""
        monkeypatch.setenv("HOME", str(tmp_path))
        assert_that(is_path_allowed("/some/path/file.svg", "svg"), is_(False))

    def test_allows_exact_directory_match(self, tmp_path: Path, monkeypatch):
        """Path in exactly specified directory is allowed."""
        monkeypatch.setenv("HOME", str(tmp_path))
        config_dir = tmp_path / ".config" / "mcp-svg-animator"
        config_dir.mkdir(parents=True)
        (config_dir / "config.yaml").write_text(f"""
file_output:
  allowed:
    - path: "{tmp_path}/diagrams"
      types: [svg]
""")
        assert_that(is_path_allowed(f"{tmp_path}/diagrams/test.svg", "svg"), is_(True))

    def test_allows_subdirectory(self, tmp_path: Path, monkeypatch):
        """Path in subdirectory of allowed directory is permitted."""
        monkeypatch.setenv("HOME", str(tmp_path))
        config_dir = tmp_path / ".config" / "mcp-svg-animator"
        config_dir.mkdir(parents=True)
        (config_dir / "config.yaml").write_text(f"""
file_output:
  allowed:
    - path: "{tmp_path}/diagrams"
      types: [svg]
""")
        assert_that(
            is_path_allowed(f"{tmp_path}/diagrams/subdir/test.svg", "svg"), is_(True)
        )

    def test_denies_wrong_file_type(self, tmp_path: Path, monkeypatch):
        """Path with disallowed file type is denied."""
        monkeypatch.setenv("HOME", str(tmp_path))
        config_dir = tmp_path / ".config" / "mcp-svg-animator"
        config_dir.mkdir(parents=True)
        (config_dir / "config.yaml").write_text(f"""
file_output:
  allowed:
    - path: "{tmp_path}/diagrams"
      types: [svg]
""")
        assert_that(is_path_allowed(f"{tmp_path}/diagrams/test.png", "png"), is_(False))

    def test_denies_path_outside_allowed(self, tmp_path: Path, monkeypatch):
        """Path outside allowed directories is denied."""
        monkeypatch.setenv("HOME", str(tmp_path))
        config_dir = tmp_path / ".config" / "mcp-svg-animator"
        config_dir.mkdir(parents=True)
        (config_dir / "config.yaml").write_text(f"""
file_output:
  allowed:
    - path: "{tmp_path}/diagrams"
      types: [svg]
""")
        assert_that(is_path_allowed(f"{tmp_path}/other/test.svg", "svg"), is_(False))

    def test_expands_tilde_in_config(self, tmp_path: Path, monkeypatch):
        """Tilde in config path is expanded to home directory."""
        monkeypatch.setenv("HOME", str(tmp_path))
        config_dir = tmp_path / ".config" / "mcp-svg-animator"
        config_dir.mkdir(parents=True)
        (config_dir / "config.yaml").write_text("""
file_output:
  allowed:
    - path: "~/diagrams"
      types: [svg]
""")
        assert_that(is_path_allowed(f"{tmp_path}/diagrams/test.svg", "svg"), is_(True))

    def test_glob_pattern_with_double_star(self, tmp_path: Path, monkeypatch):
        """Double star glob matches any subdirectory depth."""
        monkeypatch.setenv("HOME", str(tmp_path))
        config_dir = tmp_path / ".config" / "mcp-svg-animator"
        config_dir.mkdir(parents=True)
        (config_dir / "config.yaml").write_text(f"""
file_output:
  allowed:
    - path: "{tmp_path}/projects/**/output"
      types: [svg, png]
""")
        assert_that(
            is_path_allowed(f"{tmp_path}/projects/foo/bar/output/test.svg", "svg"),
            is_(True),
        )
        assert_that(
            is_path_allowed(f"{tmp_path}/projects/output/test.png", "png"), is_(True)
        )

    def test_glob_pattern_with_single_star(self, tmp_path: Path, monkeypatch):
        """Single star glob matches single directory level."""
        monkeypatch.setenv("HOME", str(tmp_path))
        config_dir = tmp_path / ".config" / "mcp-svg-animator"
        config_dir.mkdir(parents=True)
        (config_dir / "config.yaml").write_text(f"""
file_output:
  allowed:
    - path: "{tmp_path}/projects/*/output"
      types: [svg]
""")
        assert_that(
            is_path_allowed(f"{tmp_path}/projects/foo/output/test.svg", "svg"),
            is_(True),
        )
        # Single star shouldn't match multiple levels
        assert_that(
            is_path_allowed(f"{tmp_path}/projects/foo/bar/output/test.svg", "svg"),
            is_(False),
        )

    def test_multiple_allowed_paths(self, tmp_path: Path, monkeypatch):
        """Multiple allowed paths are all checked."""
        monkeypatch.setenv("HOME", str(tmp_path))
        config_dir = tmp_path / ".config" / "mcp-svg-animator"
        config_dir.mkdir(parents=True)
        (config_dir / "config.yaml").write_text(f"""
file_output:
  allowed:
    - path: "{tmp_path}/diagrams"
      types: [svg]
    - path: "{tmp_path}/images"
      types: [png]
""")
        assert_that(is_path_allowed(f"{tmp_path}/diagrams/test.svg", "svg"), is_(True))
        assert_that(is_path_allowed(f"{tmp_path}/images/test.png", "png"), is_(True))

    def test_webm_type_for_video(self, tmp_path: Path, monkeypatch):
        """webm file type is supported for video output."""
        monkeypatch.setenv("HOME", str(tmp_path))
        config_dir = tmp_path / ".config" / "mcp-svg-animator"
        config_dir.mkdir(parents=True)
        (config_dir / "config.yaml").write_text(f"""
file_output:
  allowed:
    - path: "{tmp_path}/videos"
      types: [webm]
""")
        assert_that(is_path_allowed(f"{tmp_path}/videos/anim.webm", "webm"), is_(True))
