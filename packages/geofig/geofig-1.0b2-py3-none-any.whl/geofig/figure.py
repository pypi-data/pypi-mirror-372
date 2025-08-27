"""Figure module."""

import xml.etree.ElementTree as ET

from .geometry import Arc, Scalar, Transformer
from collections.abc import Callable
from math import ceil
from pathlib import Path
from sympy import Max, Min, pi
from sympy.geometry.ellipse import Circle, Ellipse
from sympy.geometry.entity import GeometryEntity
from sympy.geometry.line import Segment
from sympy.geometry.point import Point
from sympy.geometry.polygon import Polygon
from typing import Any, Iterable, NamedTuple
from xml.dom import minidom


def _n(x: Any) -> int | float:
    f = round(float(x), 4)
    i = int(f)
    return i if i == f else f


class _Bounds(NamedTuple):
    """Bounding box."""

    xmin: Scalar
    ymin: Scalar
    xmax: Scalar
    ymax: Scalar

    def union(self, other: "_Bounds") -> "_Bounds":
        """Return the union of this and another bounding box."""
        return _Bounds(
            Min(self.xmin, other.xmin),
            Min(self.ymin, other.ymin),
            Max(self.xmax, other.xmax),
            Max(self.ymax, other.ymax),
        )


class _Padding(NamedTuple):
    """Figure padding."""

    top: float
    right: float
    bottom: float
    left: float


class _CSS:
    """Dynamic cascading style sheet."""

    def __init__(self):
        self._rules: dict[tuple[str, ...], str] = {}
        self._selected: set[str] = set(("*", "svg"))

    def __str__(self) -> str:
        result = []
        result.append("")
        for key in self._rules:
            if selectors := ", ".join(s for s in key if s in self._selected):
                result.append(f"{selectors} {{")
                for line in self._rules[key].split("\n"):
                    line = line.strip()
                    if line:
                        result.append(f"\t{line}")
                result.append("}")
        result.append("")
        return f"{'\n'.join(result)}"

    def __setitem__(self, key: str | tuple[str, ...], value: str) -> None:
        if isinstance(key, str):
            key = (key,)
        if key in self._rules:
            raise ValueError(f"{key} rule already defined")
        self._rules[key] = value

    def select(self, element: ET.Element) -> None:
        """Select an element and its attributes for styling."""

        def _select(_element: ET.Element) -> None:
            self._selected.add(_element.tag)
            keys = _element.keys()
            if id := _element.get("id"):
                self._selected.add(f"#{id}")
            if classes := _element.get("class"):
                for cls in classes.split(" "):
                    self._selected.add(f".{cls}")

        _select(element)
        for subelement in element:
            _select(subelement)

    def update(self, rules: dict[str | tuple[str, ...], str]) -> None:
        for key, value in rules.items():
            self[key] = value


class ts:
    """A text span, for inclusion in figure text."""

    def __init__(self, text: str, **kwargs: Any):
        self.text = text
        self.kwargs = kwargs


def _kw(kwargs: dict[str, Any]) -> dict[str, Any]:
    return {k.rstrip("_").replace("_", "-"): v for k, v in kwargs.items()}


class Figure:
    """A geometric figure, expressed on a Cartesian plane, rendered as an SVG drawing."""

    scale: int | float

    def __init__(self):
        self._background: dict[str, Any] | None = None
        self._bounds: _Bounds | None = None
        self._css = _CSS()
        self._description = None
        self._ops: list[Callable[[Transformer], ET.Element]] = []
        self._title = None
        self.scale(1)
        self.padding(4)

    def _include(self, entity: GeometryEntity) -> None:
        """Update the internal bounding box to include the given entity."""
        bounds = _Bounds(*entity.bounds)
        self._bounds = self._bounds.union(bounds) if self._bounds else bounds

    def arc(self, arc: Arc, **kwargs: Any):
        """Add an arc to the figure."""

        def op(transformer: Transformer) -> ET.Element:
            _arc = transformer.apply(arc)
            return ET.Element(
                "path",
                d=(
                    f"M {_n(_arc.points[0].x)} {_n(_arc.points[0].y)} "
                    f"A "
                    f"{_n(_arc.ellipse.hradius)} "  # rx
                    f"{_n(_arc.ellipse.vradius)} "  # ry
                    f"0 "  # rotation
                    f"{int(bool(_arc.length > pi or _arc.length < -pi))} "  # large_arc
                    f"{int(bool(_arc.length > 0))} "  # sweep
                    f"{_n(_arc.points[1].x)} "  # x
                    f"{_n(_arc.points[1].y)}"  # y
                ),
                **_kw(kwargs),
            )

        self._ops.append(op)
        self._include(arc)

    def circle(self, circle: Circle, **kwargs: Any) -> None:
        """Add a circle to the figure."""

        def op(transformer: Transformer) -> ET.Element:
            _circle = transformer.apply(circle)
            if isinstance(_circle, Circle):
                return ET.Element(
                    "circle",
                    cx=f"{_n(_circle.center.x)}",
                    cy=f"{_n(_circle.center.y)}",
                    r=f"{_n(_circle.radius)}",
                    **_kw(kwargs),
                )
            elif isinstance(_circle, Ellipse):  # transformed to ellipse
                return ET.Element(
                    "ellipse",
                    cx=f"{_n(_circle.center.x)}",
                    cy=f"{_n(_circle.center.y)}",
                    rx=f"{_n(_circle.hradius)}",
                    ry=f"{_n(_circle.vradius)}",
                    **_kw(kwargs),
                )
            raise TypeError(f"unsupported type: {type(_circle)}")

        self._ops.append(op)
        self._include(circle)

    def curve(self, *vertices: Point, **kwargs: Any):
        """Add a smooth Bézier curve to figure."""

        def op(transformer: Transformer) -> ET.Element:
            _vertices = [transformer.apply(vertex) for vertex in vertices]
            commands = [f"M {_n(_vertices[0].x)} {_n(_vertices[0].y)}"]
            if len(_vertices) == 2:
                commands.append(f"L {_n(_vertices[1].x)} {_n(_vertices[1].y)}")
            for i in range(1, len(_vertices) - 1):
                p0 = _vertices[i - 1]
                p1 = _vertices[i]
                p2 = _vertices[i + 1]
                p3 = _vertices[i + 2] if i + 2 < len(_vertices) else _vertices[i + 1]
                cp1 = Point(p1.x + (p2.x - p0.x) / 6, p1.y + (p2.y - p0.y) / 6)
                cp2 = Point(p2.x - (p3.x - p1.x) / 6, p2.y - (p3.y - p1.y) / 6)
                commands.append(
                    f"C "
                    f"{_n(cp1.x)} "  # x1
                    f"{_n(cp1.y)} "  # y1
                    f"{_n(cp2.x)} "  # x2
                    f"{_n(cp2.y)} "  # y2
                    f"{_n(p2.x)} "  # x
                    f"{_n(p2.y)}"  # y
                )
            return ET.Element("path", d=" ".join(commands), **_kw(kwargs))

        self._ops.append(op)
        for vertex in vertices:
            self._include(vertex)

    def ellipse(self, ellipse: Ellipse, **kwargs: Any) -> None:
        """Add an ellipse to the figure."""

        def op(transformer: Transformer) -> ET.Element:
            _ellipse = transformer.apply(ellipse)
            if isinstance(_ellipse, Ellipse):
                return ET.Element(
                    "ellipse",
                    cx=f"{_n(_ellipse.center.x)}",
                    cy=f"{_n(_ellipse.center.y)}",
                    rx=f"{_n(_ellipse.hradius)}",
                    ry=f"{_n(_ellipse.vradius)}",
                    **_kw(kwargs),
                )
            elif isinstance(_ellipse, Circle):  # transformed to circle
                return ET.Element(
                    "circle",
                    cx=f"{_n(_ellipse.center.x)}",
                    cy=f"{_n(_ellipse.center.y)}",
                    r=f"{_n(_ellipse.radius)}",
                    **_kw(kwargs),
                )
            raise TypeError(f"unsupported type: {type(_ellipse)}")

        self._ops.append(op)
        self._include(ellipse)

    def line(self, segment: Segment, **kwargs: Any) -> None:
        """Add a line to figure."""

        def op(transformer: Transformer) -> ET.Element:
            _segment = transformer.apply(segment)
            return ET.Element(
                "line",
                x1=f"{_n(_segment.p1.x)}",
                y1=f"{_n(_segment.p1.y)}",
                x2=f"{_n(_segment.p2.x)}",
                y2=f"{_n(_segment.p2.y)}",
                **_kw(kwargs),
            )

        self._ops.append(op)
        self._include(segment)

    def path(
        self, *entities: Iterable[Arc | Segment], close: bool = False, **kwargs: Any
    ) -> None:
        """
        Add a connected path to the figure.

        Parameters:
        • entities: sequence of arc or segment objects that define the path
        • close: close the path to the starting point
        """

        def op(transformer: Transformer) -> ET.Element:
            _entities = [transformer.apply(entity) for entity in entities]
            commands = []
            last = None
            count = len(_entities)
            for n in range(count):
                entity = _entities[n]
                p1, p2 = entity.points
                if last == p2:
                    p1, p2 = p2, p1
                if last != p1:
                    if n < count - 1:
                        next = _entities[n + 1]
                        if p1 in next.points:
                            p1, p2 = p2, p1
                if last != p1:
                    commands.append(f"M {_n(p1.x)} {_n(p1.y)}")
                if isinstance(entity, Segment):
                    commands.append(f"L {_n(p2.x)} {_n(p2.y)}")
                elif isinstance(entity, Arc):
                    commands.append(
                        f"A "
                        f"{_n(entity.ellipse.hradius)} "  # rx
                        f"{_n(entity.ellipse.vradius)} "  # ry
                        f"0 "  # rotation
                        f"{int(bool(entity.length > pi or entity.length < -pi))} "  # large_arc
                        f"{int((bool(entity.length > 0) ^ (p1 != entity.points[0])))} "  # sweep
                        f"{_n(p2.x)} "  # x
                        f"{_n(p2.y)}"  # y
                    )
                else:
                    raise ValueError(f"unsupported entity: {type(entity)}")
                last = p2
            if close:
                commands.append("Z")
            return ET.Element("path", d=" ".join(commands), **_kw(kwargs))

        self._ops.append(op)
        for entity in entities:
            self._include(entity)

    def polygon(self, polygon: Polygon, **kwargs: Any) -> None:
        """Add a polygon to the figure."""

        def op(transformer: Transformer) -> ET.Element:
            _polygon = transformer.apply(polygon)
            return ET.Element(
                "polygon",
                points=" ".join(f"{_n(v.x)} {_n(v.y)}" for v in _polygon.vertices),
                **_kw(kwargs),
            )

        self._ops.append(op)
        self._include(polygon)

    def polyline(self, *vertices: Point, **kwargs: Any) -> None:
        """Add a polyline to the figure."""

        def op(transformer: Transformer) -> ET.Element:
            _vertices = [transformer.apply(vertex) for vertex in vertices]
            return ET.Element(
                "polyline",
                points=" ".join(f"{_n(v.x)} {_n(v.y)}" for v in _vertices),
                **_kw(kwargs),
            )

        self._ops.append(op)
        for vertex in vertices:
            self._include(vertex)

    def text(
        self,
        text: str | Iterable[str | ts],
        point: Point,
        *,
        sx: Scalar = 0,
        sy: Scalar = 0,
        **kwargs: Any,
    ) -> None:
        """
        Add text to the figure.

        Parameters:
        • text: text and/or text spans to be added
        • point: point of text, in Cartesian space
        • sx: shift x-axis offset in SVG pixels
        • sy: shift y-axis offset in SVG pixels

        Example:

        ```
        origin = Point(0, 0)
        fig.text("This is normal text.", origin)
        fig.text(("This is ", ts("italic", class_="italic"), " text."), origin, sy=18)
        ```
        """

        def op(transformer: Transformer) -> ET.Element:
            _point = transformer.apply(point)
            _text = (text,) if isinstance(text, str) else text
            element = ET.Element(
                "text",
                x=f"{_n(_point.x + sx)}",
                y=f"{_n(_point.y + sy)}",
                **_kw(kwargs),
            )
            for part in _text:
                if isinstance(part, str):
                    if not len(element):
                        element.text = f"{element.text or ''}{part}"
                    else:
                        element[-1].tail = f"{element[-1].tail or ''}{part}"
                else:
                    tspan = ET.Element("tspan", **_kw(part.kwargs))
                    tspan.text = part.text
                    element.append(tspan)
            return element

        self._ops.append(op)
        self._include(point)

    def background(self, **kwargs: Any) -> None:
        """
        Add a background rectangle with the dimensions of the figure.

        The background `rect` SVG element can be identified with an `id` or `class_`
        keyword argument, and styled accordingly.
        """
        self._background = kwargs

    def description(self, value: str) -> None:
        """Set the figure description."""
        self._description = value

    def padding(self, *args: int | float) -> None:
        """
        Set padding around the figure, in SVG pixels.

        Parameters:
        • 1 value: all sides
        • 2 values: vertical, horizontal
        • 4 values: top, right, bottom, left
        """
        args = [float(arg) for arg in args]
        match len(args):
            case 1:
                self._padding = _Padding(args[0], args[0], args[0], args[0])
            case 2:
                self._padding = _Padding(args[0], args[1], args[0], args[1])
            case 4:
                self._padding = _Padding(args[0], args[1], args[2], args[3])
            case _:
                raise ValueError("padding requires 1, 2 or 4 arguments")

    def scale(self, value: int | float) -> None:
        """Set scaling factor to be applied to output drawing."""
        self._scale = value

    def styles(self, rules: dict[str, str]) -> None:
        """Set CSS style rules."""
        self._css.update(rules)

    def title(self, value: str) -> None:
        """Set the figure title."""
        self._title = value

    def save(self, path: str | Path) -> None:
        """Save the figure as an SVG file."""
        if not self._ops:
            raise RuntimeError("nothing to save")
        transformer = Transformer()
        transformer.scale(self._scale, -self._scale)
        transformer.translate(
            -self._bounds.xmin * self._scale + self._padding.left,
            self._bounds.ymax * self._scale + self._padding.top,
        )
        width = ceil(
            _n(
                (self._bounds.xmax - self._bounds.xmin) * self._scale
                + self._padding.right
                + self._padding.left
            )
        )
        height = ceil(
            _n(
                (self._bounds.ymax - self._bounds.ymin) * self._scale
                + self._padding.top
                + self._padding.bottom
            )
        )
        svg = ET.Element(
            "svg",
            xmlns="http://www.w3.org/2000/svg",
            version="1.1",
            viewBox=f"0 0 {width} {height}",
        )
        if self._title:
            title = ET.Element("title")
            title.text = self._title
            svg.append(title)
        if self._description:
            desc = ET.Element("desc")
            desc.text = self._description
            svg.append(desc)
        elements = []
        if self._background is not None:
            elements.append(
                ET.Element(
                    "rect",
                    x="0",
                    y="0",
                    width=f"{width}",
                    height=f"{height}",
                    **_kw(self._background),
                )
            )
        for op in self._ops:
            elements.append(op(transformer))
        for element in elements:
            self._css.select(element)
        defs = ET.Element("defs")
        style = ET.Element("style", type="text/css")
        style.text = str(self._css)
        defs.append(style)
        svg.append(defs)
        for element in elements:
            svg.append(element)
        ET.indent(svg, space="\t")
        with open(path, "w", encoding="utf-8") as file:
            file.write('<?xml version="1.0" encoding="utf-8"?>\n')
            file.write(ET.tostring(svg, encoding="unicode", xml_declaration=False))
            file.write("\n")
