from __future__ import annotations

import sys
from enum import unique
from functools import wraps
from typing import TYPE_CHECKING, Callable, Any

from ._annotations import T, GroupID

if TYPE_CHECKING:
    from ._node import Node


# NOTE: Variants of the enum produces the same hash as if it was using normal `str`
if sys.version_info >= (3, 11):
    from enum import StrEnum, auto

    @unique
    class Group(StrEnum):
        """Enum for core node groups used in `charz-core`."""

        NODE = auto()

else:
    from enum import Enum

    @unique
    class Group(str, Enum):
        """Enum for core node groups used in `charz-core`."""

        NODE = "node"


def group(group_id: GroupID, /) -> Callable[[type[T]], type[T]]:
    """Decorator that adds `node`/`component` to the given `group`.

    Example:

    Adding instances of a custom node class to a new group `"tile"`,
    and `iterating over members` in the current scene:

    ```python
    from charz_core import Node2D, Scene, group

    @group("tile")
    class WorldTile(Node2D):
        def __init__(self, material_name: str) -> None:
            self.material_name = material_name

    dirt = WorldTile("Dirt")
    stone = WorldTile("Stone")

    for tile in Scene.current.get_group_members("tile", type_hint=WorldTile):
        print(tile.material_name)

    # Prints out
    >>> 'Dirt'
    >>> 'Stone'
    ```

    This works by wrapping `__new__` and `_free`.
    Recommended types for parameter `group_id`: `LiteralString`, `StrEnum` or `int`.

    `NOTE` Each node is added to the current scene's group when `__new__` is called.

    Args:
        group_id (GroupID): *Hashable* object used for group ID

    Returns:
        Callable[[type[T]], type[T]]: Wrapped class
    """
    # NOTE: Lazyloading `Scene`
    # Do import here to prevent cycling dependencies,
    # as there won't be a lot of scene creation
    from ._scene import Scene

    def wrapper(node_type_or_component: type[T]) -> type[T]:
        original_new = node_type_or_component.__new__

        # This will not always be correct, but I will leave it for now...
        @wraps(original_new)
        def new_wrapper(cls: type[T], *args: Any, **kwargs: Any) -> T:
            # This conditional fixes (hopefully) the MRO chain problem I had for a long time...
            if original_new is object.__new__:
                # Perform `super()` call to the next object's `__new__` in the MRO chain
                # without the help of compiler magic.
                # This path (in the if-statement) is likely triggered by
                # the component/node class (that is decorated with this decorator)
                # not implementing its own `__new__` method.
                # NOTE: This path fixes components' `__new__` so it will call
                # the right `__new__` associated with the next object in the MRO chain,
                # and don't just end with `object.__new__`
                # - that previously resulted in "lost logic".
                mro_next_index = cls.__mro__.index(node_type_or_component) + 1
                mro_next = cls.__mro__[mro_next_index]
                instance = mro_next.__new__(cls, *args, **kwargs)
            else:
                # Wrap the original `__new__` method
                instance = original_new(cls, *args, **kwargs)
            Scene.current.groups[group_id][instance.uid] = instance  # type: ignore
            return instance

        node_type_or_component.__new__ = new_wrapper
        return node_type_or_component

    return wrapper
