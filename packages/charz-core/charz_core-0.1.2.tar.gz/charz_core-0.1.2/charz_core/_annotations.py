"""
Custom Annotations for `charz-core`
===================================

This file contains private annotations used across this package.

Whenever there is a "?" comment,
it means a type may or may not implement that field or mixin class.
"""

from __future__ import annotations as _annotations

import sys as _sys
from itertools import count as _count
from typing import (
    TypeVar as _TypeVar,
    TypeAlias as _TypeAlias,
    ClassVar as _ClassVar,
    Hashable as _Hashable,
    Protocol as _Protocol,
    overload as _overload,
)

from linflex import Vec2 as _Vec2

if _sys.version_info >= (3, 11):
    from typing import (
        LiteralString as _LiteralString,
        Self,
    )
else:
    from typing_extensions import (
        LiteralString as _LiteralString,
        Self,
    )

from ._frame_task import FrameTaskManager as _FrameTaskManager

T = _TypeVar("T")
NodeID: _TypeAlias = int
GroupID: _TypeAlias = _LiteralString | NodeID | _Hashable


class Engine(_Protocol):
    frame_tasks: _FrameTaskManager[Self]  # Global across instances
    _is_running: bool

    @property
    def is_running(self) -> bool: ...
    @is_running.setter
    def is_running(self, run_state: bool) -> None: ...
    def process(self) -> None: ...
    def update(self) -> None: ...
    def run(self) -> None: ...


class Node(_Protocol):
    _uid_counter: _ClassVar[_count[NodeID]]
    uid: NodeID
    parent: Node | None

    def __init__(self) -> None: ...
    def with_parent(self, parent: Node | None, /) -> Self: ...
    def update(self) -> None: ...
    def queue_free(self) -> None: ...


class TransformComponent(_Protocol):
    position: _Vec2
    rotation: float
    top_level: bool

    @_overload
    def with_position(
        self,
        position: _Vec2,
        /,
    ) -> Self: ...
    @_overload
    def with_position(
        self,
        *,
        x: float,
        y: float,
    ) -> Self: ...
    @_overload
    def with_global_position(
        self,
        global_position: _Vec2,
        /,
    ) -> Self: ...
    @_overload
    def with_global_position(
        self,
        *,
        x: float,
        y: float,
    ) -> Self: ...
    def with_rotation(self, rotation: float, /) -> Self: ...
    def with_global_rotation(self, global_rotation: float, /) -> Self: ...
    def with_top_level(self, state: bool = True, /) -> Self: ...
    @property
    def global_position(self) -> _Vec2: ...
    @global_position.setter
    def global_position(self, position: _Vec2) -> None: ...
    @property
    def global_rotation(self) -> float: ...
    @global_rotation.setter
    def global_rotation(self, rotation: float) -> None: ...
    def set_global_x(self, x: float, /) -> None: ...
    def set_global_y(self, y: float, /) -> None: ...


class TransformNode(
    TransformComponent,
    Node,
    _Protocol,
): ...
