"""Text element specification class."""

from typing import Literal

from pydantic import BaseModel, Field

from .animation_spec import AnimationSpec


class TextSpec(BaseModel):
    """Specification for a text element."""

    id: str | None = None
    type: Literal["text"] = "text"
    text: str = ""
    font_size: float = 16
    x: float = 0
    y: float = 0
    fill: str = "black"
    text_anchor: str | None = None
    animations: list[AnimationSpec] = Field(default_factory=list)

    model_config = {"populate_by_name": True}
