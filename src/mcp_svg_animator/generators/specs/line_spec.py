"""Line element specification class."""

from typing import Literal

from pydantic import BaseModel, Field

from .animation_spec import AnimationSpec


class LineSpec(BaseModel):
    """Specification for a line element."""

    id: str | None = None
    type: Literal["line"] = "line"
    x1: float = 0
    y1: float = 0
    x2: float = 100
    y2: float = 100
    stroke: str = "black"
    stroke_width: float = Field(default=2, alias="stroke_width")
    marker_end: str | None = None
    animations: list[AnimationSpec] = Field(default_factory=list)

    model_config = {"populate_by_name": True}
