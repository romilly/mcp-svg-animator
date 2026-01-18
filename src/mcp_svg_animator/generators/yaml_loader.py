"""Load SVG diagrams from YAML specifications."""

import yaml

from .animations import create_animated_diagram


def create_diagram_from_yaml(yaml_content: str) -> str:
    """Create an SVG diagram from a YAML specification.

    Args:
        yaml_content: YAML string containing the diagram specification.
            Should have the same structure as the dict passed to
            create_animated_diagram:
            - width: Canvas width (default 400)
            - height: Canvas height (default 300)
            - elements: List of shape specifications

    Returns:
        SVG content as a string.

    Raises:
        ValueError: If the YAML contains invalid element specifications.
        yaml.YAMLError: If the YAML is malformed.
    """
    spec = yaml.safe_load(yaml_content)
    return create_animated_diagram(spec)
