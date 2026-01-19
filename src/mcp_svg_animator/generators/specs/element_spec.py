"""Base element specification class."""

from pydantic import BaseModel, Field

from .animation_spec import AnimationSpec


class ElementSpec(BaseModel):
    """Base specification for SVG elements."""

    id: str | None = None
    fill: str = "blue"
    stroke: str = "none"
    stroke_width: float = Field(default=0, alias="stroke_width")
    animations: list[AnimationSpec] = Field(default_factory=list)

    model_config = {"populate_by_name": True}
