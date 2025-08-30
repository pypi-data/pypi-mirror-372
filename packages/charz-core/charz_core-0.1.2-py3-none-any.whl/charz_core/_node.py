from __future__ import annotations

from itertools import count
from typing import Any, ClassVar

from typing_extensions import Self

from ._grouping import Group, group
from ._scene import Scene
from ._annotations import NodeID


class NodeMixinSorter(type):
    """Metaclass for sorting `Node` to be the last base in MRO."""

    def __new__(
        cls,
        name: str,
        bases: tuple[type, ...],
        attrs: dict[str, object],
    ) -> type:
        def sorter(base: type) -> bool:
            # Ensures `Node` will be last in MRO (except for `object`),
            # to help `__new__` chain for nodes (instances of `Node`/`Node` subclass)
            # work despite wrong order in subclass declaration
            return issubclass(base, Node)

        sorted_bases = tuple(sorted(bases, key=sorter))
        new_type = super().__new__(cls, name, sorted_bases, attrs)
        return new_type


@group(Group.NODE)
class Node(metaclass=NodeMixinSorter):
    """`Node` base class.

    All nodes existing in a scene (either "physically" or "theoretically"),
    will be instances of either this class, or a subclass.
    Subclasses can be combined with component mixins, using Python's multiple inheritance.
    This class can be instantiated directly, but in itself it does not do anything useful.

    The reference of nodes is stored in `Scene.groups[Group.NODE]`,
    which is a dictionary mapping `NodeID` to `Node` instances.
    It keeps the node alive, and prevents it from being garbage collected.

    Example:

    Every node will be assigned a unique identifier (`uid`),
    which can be used to reference it within the scene:

    ```python
    from charz_core import Scene, Node, Group

    my_node = Node()
    reference = Scene.groups[Group.NODE][my_node.uid]
    assert reference is my_node
    ```

    The assignment of `uid` is done automatically when the node is created,
    and is guaranteed to be unique within the scene.
    It happens at the end of the `__new__` chain.
    The `__new__` chain is when components call `super().__new__(...)`,
    which calls `Node.__new__` to assign the `uid`, since the bases are
    sorted to ensure `Node` is the last base in the MRO (Method Resolution Order).
    """

    _uid_counter: ClassVar[count[NodeID]] = count(0, 1)

    def __new__(cls, *_args: Any, **_kwargs: Any) -> Self:
        """Last in the `__new__` chain, which assigns `uid`."""
        # NOTE: Additional args and kwargs are ignored!
        instance = super().__new__(cls)
        instance.uid = next(Node._uid_counter)
        return instance

    uid: NodeID  # Is set in `Node.__new__`
    parent: Node | None = None

    def __init__(self, parent: Node | None = None) -> None:
        """Initialize node."""
        if parent is not None:
            self.parent = parent

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(#{self.uid})"

    def with_parent(self, parent: Node | None, /) -> Self:
        """Chained method to set parent node."""
        self.parent = parent
        return self

    def update(self) -> None:
        """Called each frame.

        Override this method in subclasses to implement custom update logic.
        """

    def queue_free(self) -> None:
        """Queues this node for freeing.

        This method should be called when you want to remove the node from the scene.
        It will be freed at the end of the current frame, handled by `Engine.frame_tasks`.
        """
        Scene.current._queued_nodes.add(self.uid)
