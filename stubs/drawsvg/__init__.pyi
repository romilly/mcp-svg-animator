"""Type stubs for drawsvg library."""

from typing import Any

class Drawing:
    def __init__(self, width: float, height: float, **kwargs: Any) -> None: ...
    def append(self, element: Any) -> None: ...
    def as_svg(self) -> str: ...

class Circle:
    def __init__(
        self,
        cx: float,
        cy: float,
        r: float,
        *,
        fill: str = ...,
        stroke: str = ...,
        stroke_width: float = ...,
        **kwargs: Any,
    ) -> None: ...
    def append_anim(self, anim: Any) -> None: ...

class Rectangle:
    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        *,
        fill: str = ...,
        stroke: str = ...,
        stroke_width: float = ...,
        **kwargs: Any,
    ) -> None: ...
    def append_anim(self, anim: Any) -> None: ...

class Line:
    def __init__(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        *,
        stroke: str = ...,
        stroke_width: float = ...,
        marker_end: Marker | None = ...,
        **kwargs: Any,
    ) -> None: ...
    def append_anim(self, anim: Any) -> None: ...

class Text:
    def __init__(
        self,
        text: str,
        font_size: float,
        x: float | None = ...,
        y: float | None = ...,
        *,
        fill: str = ...,
        text_anchor: str = ...,
        **kwargs: Any,
    ) -> None: ...
    def append_anim(self, anim: Any) -> None: ...

class Path:
    def __init__(
        self,
        d: str = ...,
        *,
        fill: str = ...,
        stroke: str = ...,
        stroke_width: float = ...,
        **kwargs: Any,
    ) -> None: ...
    def append_anim(self, anim: Any) -> None: ...

class Animate:
    def __init__(
        self,
        attribute: str,
        dur: str,
        *,
        from_or_values: str | None = ...,
        to: str | None = ...,
        repeatCount: str | None = ...,
        **kwargs: Any,
    ) -> None: ...

class Group:
    def __init__(self, *, transform: str = ..., **kwargs: Any) -> None: ...
    def append(self, element: Any) -> None: ...

class Raw:
    def __init__(self, content: str) -> None: ...

class Marker:
    def __init__(
        self,
        minx: float,
        miny: float,
        maxx: float,
        maxy: float,
        *,
        scale: float = ...,
        orient: str = ...,
        id: str = ...,
        **kwargs: Any,
    ) -> None: ...
    def append(self, element: Any) -> None: ...

class Lines:
    def __init__(
        self,
        *points: float,
        fill: str = ...,
        stroke: str = ...,
        close: bool = ...,
        **kwargs: Any,
    ) -> None: ...
