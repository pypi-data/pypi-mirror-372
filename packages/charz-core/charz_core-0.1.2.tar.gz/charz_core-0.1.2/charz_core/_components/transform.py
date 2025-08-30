from __future__ import annotations

from typing import Any

from linflex import Vec2
from typing_extensions import Self
from typing import overload


class TransformComponent:  # Component (mixin class)
    """`TransformComponent` mixin class for node.

    Examples:

    Composing a 2D node with custom physics component:

    ```python
    from charz_core import Node, TransformComponent
    from .my_files.physics_component import PhysicsComponent

    class PhysicsBody(TransformComponent, PhysicsComponent, Node):
        ...
    ```

    *Psudocode* for how `charz_core.Node2D` is composed:

    ```python
    from charz_core import Node, TransformComponent

    class Node2D(TransformComponent, Node):
        ...
    ```

    Attributes:
        `position`: `Vec2` - Position in local space.
        `rotation`: `float` - Angle in radians.
        `top_level`: `bool` - Indicating if the node is a top-level node.
        `global_position`: `property[Vec2]` - Copy of position in world space.
        `global_rotation`: `property[float]` - Rotation in world space.

    Methods:
        `set_global_x`
        `set_global_y`
    """

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        instance = super().__new__(cls, *args, **kwargs)
        if (class_position := getattr(instance, "position", None)) is not None:
            instance.position = Vec2.copy(class_position)
        else:
            instance.position = Vec2.ZERO
        return instance

    position: Vec2
    rotation: float = 0
    top_level: bool = False

    @overload
    def with_position(
        self,
        position: Vec2,
        /,
    ) -> Self: ...

    @overload
    def with_position(
        self,
        *,
        x: float,
        y: float,
    ) -> Self: ...

    def with_position(  # type: ignore[override]
        self,
        position: Vec2 | None = None,
        /,
        *,
        x: float | None = None,
        y: float | None = None,
    ) -> Self:
        """Chained method to set the node's position.

        This method allows you to set the position of the node,
        using either a `Vec2` instance or individual `x` and `y` coordinates.

        Args:
            position (Vec2 | None, optional): Position of the node. Defaults to None.
            x (float | None, optional): X-coordinate of the node. Defaults to None.
            y (float | None, optional): Y-coordinate of the node. Defaults to None.

        Raises:
            TypeError: If all arguments are `None` at the same time.
            TypeError: If both `position` and any of `x`/`y` are provided.

        Returns:
            Self: Same node instance.
        """
        if position is None and x is None and y is None:
            raise TypeError(f"Not all arguments can be {None} at the same time")
        if position is not None and (x is not None or y is not None):
            raise TypeError(
                "Chose either positional argument 'position' "
                "or keyword arguments 'x' and/or 'y', not all three"
            )
        if position is not None:
            self.position = position
        if x is not None:
            self.position.x = x
        if y is not None:
            self.position.y = y
        return self

    @overload
    def with_global_position(
        self,
        global_position: Vec2,
        /,
    ) -> Self: ...

    @overload
    def with_global_position(
        self,
        *,
        x: float,
        y: float,
    ) -> Self: ...

    def with_global_position(  # type: ignore[override]
        self,
        global_position: Vec2 | None = None,
        /,
        *,
        x: float | None = None,
        y: float | None = None,
    ) -> Self:
        """Chained method to set the node's global position.

        This method allows you to set the global position of the node,
        using either a `Vec2` instance or individual `x` and `y` coordinates.

        Args:
            global_position (Vec2 | None, optional): Global position. Defaults to None.
            x (float | None, optional): Global x-coordinate of node. Defaults to None.
            y (float | None, optional): Global y-coordinate of node. Defaults to None.

        Raises:
            TypeError: If all arguments are `None` at the same time.
            TypeError: If both `global_position` and any of `x`/`y` are provided.

        Returns:
            Self: Same node instance.
        """
        if global_position is None and x is None and y is None:
            raise TypeError(f"Not all arguments can be {None} at the same time")
        if global_position is not None and (x is not None or y is not None):
            raise TypeError(
                "Chose either positional argument 'global_position' "
                "or keyword arguments 'x' and/or 'y', not all three"
            )
        if global_position is not None:
            self.global_position = global_position
        if x is not None:
            self.set_global_x(x)
        if y is not None:
            self.set_global_y(y)
        return self

    def with_rotation(self, rotation: float, /) -> Self:
        """Chained method to set the node's `rotation`.

        Args:
            rotation (float): Rotation in radians.

        Returns:
            Self: Same node instance.
        """
        self.rotation = rotation
        return self

    def with_global_rotation(self, global_rotation: float, /) -> Self:
        """Chained method to set the node's `global_rotation`.

        Args:
            global_rotation (float): Global rotation in radians.

        Returns:
            Self: Same node instance.
        """
        self.global_rotation = global_rotation
        return self

    def with_top_level(self, state: bool = True, /) -> Self:
        """Chained method to set the node's `top_level` state.

        Args:
            state (bool, optional): Whether node is a top-level node. Defaults to True.

        Returns:
            Self: Same node instance.
        """
        self.top_level = state
        return self

    def set_global_x(self, x: float, /) -> None:
        """Set node's global x-coordinate.

        Args:
            x (float): Global x-coordinate.
        """
        diff_x = x - self.global_position.x
        self.position.x += diff_x

    def set_global_y(self, y: float, /) -> None:
        """Set node's global y-coordinate.

        Args:
            y (float): Global y-coordinate.
        """
        diff_y = y - self.global_position.y
        self.position.y += diff_y

    @property
    def global_position(self) -> Vec2:
        """Computes a copy of the node's global position (world space).

        `NOTE` Cannot do the following:

        ```python
        self.global_position.x += 5
        self.global_position.x = 42
        ```

        Instead, you should use:

        ```python
        self.position.x += 5
        self.set_global_x(42)
        ```

        Returns:
            Vec2: Copy of global position.
        """
        if self.top_level:
            return self.position.copy()
        global_position = self.position.copy()
        parent = self.parent  # type: ignore
        while isinstance(parent, TransformComponent):
            # Check for rotation, since cos(0) and sin(0) produces *approximate* values
            if parent.rotation:
                global_position = parent.position + global_position.rotated(
                    parent.rotation
                )
            else:
                global_position += parent.position
            if parent.top_level:
                return global_position
            parent = parent.parent  # type: ignore
        return global_position

    @global_position.setter
    def global_position(self, position: Vec2) -> None:
        """Set node's global position (world space).

        Args:
            position (Vec2): Global position.
        """
        diff = position - self.global_position
        self.position += diff

    @property
    def global_rotation(self) -> float:
        """Computes node's global rotation (world space).

        Returns:
            float: Global rotation in radians.
        """
        if self.top_level:
            return self.rotation
        global_rotation = self.rotation
        parent = self.parent  # type: ignore
        while isinstance(parent, TransformComponent):
            global_rotation += parent.rotation
            if parent.top_level:
                return global_rotation
            parent = parent.parent  # type: ignore
        return global_rotation

    @global_rotation.setter
    def global_rotation(self, rotation: float) -> None:
        """Set node's global rotation (world space).

        Args:
            rotation (float): Global rotation in radians.
        """
        diff = rotation - self.global_rotation
        self.rotation += diff
