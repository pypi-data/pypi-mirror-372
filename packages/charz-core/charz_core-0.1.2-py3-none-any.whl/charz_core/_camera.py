from __future__ import annotations

from enum import Flag, unique, auto
from typing import Literal

from linflex import Vec2
from typing_extensions import Self

from ._node import Node, NodeMixinSorter
from ._prefabs.node2d import Node2D


@unique
class CameraMode(Flag):
    FIXED = auto()
    CENTERED = auto()
    INCLUDE_SIZE = auto()


class CameraClassAttributes(NodeMixinSorter):
    """Workaround to add class attributes to `Camera`."""

    MODE_FIXED: CameraMode = CameraMode.FIXED
    MODE_CENTERED: CameraMode = CameraMode.CENTERED
    MODE_INCLUDE_SIZE: CameraMode = CameraMode.INCLUDE_SIZE
    _current: Camera

    @property
    def current(self) -> Camera:
        if not hasattr(self, "_current"):
            self._current = Camera()  # Create default camera if none exists
        return self._current

    @current.setter
    def current(self, new: Camera) -> None:
        self._current = new


class Camera(Node2D, metaclass=CameraClassAttributes):
    """`Camera` for controlling location of viewport in the world, per `Scene`.

    To access the current camera, access `Camera.current`.
    To set the current camera, use `Camera.current = <Camera>`,
    or call `camera.set_current()` on the camera instance.
    To set the current camera and return the instance, use `camera.as_current()`.

    `NOTE` A default `Camera` will be used if not explicitly set.

    Example:

    ```python
    from charz_core import Engine, Camera

    class MyGame(Engine):
        def __init__(self) -> None:
            # Configure how the current camera centers the viewport
            Camera.current.mode = Camera.MODE_CENTERED | Camera.MODE_INCLUDE_SIZE
    ```

    Attributes:
        `current`: `ClassVar[property[Camera]]` - Current camera instance in use.
        `mode`: `CameraMode` - Mode to decide origin for centering.

    Variants for `Camera.mode`:
    - `Camera.MODE_FIXED`: Camera is fixed at upper left corner.
    - `Camera.MODE_CENTERED`: Camera is centered.
    - `Camera.MODE_INCLUDE_SIZE`: Camera includes texture size of parent to camera.

    Methods:
        `set_current`
        `as_current` `chained`
        `is_current`
        `with_mode` `chained`
    """

    mode: CameraMode = CameraMode.FIXED

    def __init__(
        self,
        parent: Node | None = None,
        *,
        position: Vec2 | None = None,
        rotation: float | None = None,
        top_level: bool | None = None,
        mode: CameraMode | None = None,
        current: Literal[True] | None = None,
    ) -> None:
        Node2D.__init__(
            self,
            parent=parent,
            position=position,
            rotation=rotation,
            top_level=top_level,
        )
        if mode is not None:
            self.mode = mode
        if current is True:
            self.set_current()

    def set_current(self) -> None:
        """Set this camera as the current camera."""
        Camera.current = self

    def as_current(self) -> Self:
        """Chained method to set this camera as the current camera.

        Returns:
            Self: Same camera instance.
        """
        self.set_current()
        return self

    def is_current(self) -> bool:
        """Check if this camera is the current camera of the current `Scene`.

        Returns:
            bool: `True` if this camera is the current camera, `False` otherwise.
        """
        return Camera.current is self

    def with_mode(self, mode: CameraMode, /) -> Self:
        """Chained method to set the camera's mode.

        Args:
            mode (CameraMode): Enum variant to set the camera's mode.
        """
        self.mode = mode
        return self
