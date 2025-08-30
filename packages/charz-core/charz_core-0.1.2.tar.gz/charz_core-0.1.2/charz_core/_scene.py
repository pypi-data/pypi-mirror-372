from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, ClassVar, Any

from typing_extensions import Self

from ._frame_task import FrameTaskManager
from ._grouping import Group
from ._annotations import T, GroupID, NodeID

if TYPE_CHECKING:
    from ._node import Node


def static_load_node_type() -> type[Node]:
    """Workaround for the static type checker, to prevent circular dependencies."""
    if TYPE_CHECKING:
        from ._node import Node

        return Node
    return None  # Value used at runtime


# This type variable is never called, as its true value is `None` at runtime
# Used by the static type checker
NodeType = static_load_node_type()


class SceneClassProperties(type):
    _current: Scene

    @property
    def current(cls) -> Scene:
        if not hasattr(cls, "_current"):
            cls._current = cls()  # Create default scene if none exists
        return cls._current

    @current.setter
    def current(cls, new: Scene) -> None:
        cls.current.on_exit()
        cls._current = new
        new.on_enter()


class Scene(metaclass=SceneClassProperties):
    """`Scene` to encapsulate dimensions/worlds.

    Instantiating a scene (either of type `Scene` or subclass of `Scene`),
    will set that new scene instance to the current scene.

    Example:

    Structure of a scene and how to declare:

    ```python
    from charz_core import Scene
    from .my_files.player import Player

    class InsideHouse(Scene):
        def __init__(self) -> None:
            self.player = Player(position=Vec2(5, 7))  # Player when inside house
            self.table = ...
            self.chair = ...
    ```

    `NOTE` Use the *classmethod* `preload` to prevent setting current scene,
    while still loading nodes (and more) of the returned instance.

    When a node is created, it will be handled by the currently active `Scene`.

    `NOTE` If no `Scene` is created,
    a default `Scene` will be created and set as the active one.

    By subclassing `Scene`, and implementing `__init__`, all nodes
    created in that `__init__` will be added to that subclass's group of nodes.

    `NOTE (Technical)` A `Scene` hitting reference count of `0`
    will reduce the reference count to its nodes by `1`.
    """

    # Tasks are shared across all scenes
    frame_tasks: ClassVar[FrameTaskManager[Self]] = FrameTaskManager()
    # Values are set in `Scene.__new__`
    groups: defaultdict[GroupID, dict[NodeID, Node]]
    _queued_nodes: set[NodeID]

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        instance = super().__new__(cls, *args, **kwargs)
        # NOTE: When instantiating the scene,
        #       it will be set as the current one
        #     - Use preloading to surpass
        Scene._current = instance
        instance.groups = defaultdict(dict)
        instance._queued_nodes = set()
        return instance

    @classmethod
    def preload(cls) -> Self:
        """Preload the scene class, creating an instance without setting it as current.

        Returns:
            Self: An instance of the scene class, without setting it as current.
        """
        previous_scene = Scene.current
        instance = cls()
        Scene.current = previous_scene
        return instance

    def __init__(self) -> None:  # Override in subclass
        """Override to instantiate nodes and state related to this scene."""

    def __repr__(self) -> str:
        group_counts = ", ".join(f"{group}: {len(self.groups[group])}" for group in Group)
        return f"{self.__class__.__name__}({group_counts})"

    def set_current(self) -> None:
        """Set this scene as the current one."""
        Scene.current = self

    def as_current(self) -> Self:
        """Chained method to set this scene as the current one."""
        self.set_current()
        return self

    def get_group_members(
        self,
        group_id: GroupID,
        /,
        # Used to hint type checkers of dynamic return type
        type_hint: type[T] = NodeType,
    ) -> list[T]:
        """Get all members of a specific group.

        Args:
            group_id (GroupID): The ID of the group to retrieve members from.
            type_hint (type[T], optional): Node type in list returned.
                Defaults to type[Node].

        Returns:
            list[T]: A list of nodes in the specified group.
        """
        # NOTE: Return type `list` is faster than `tuple`,
        #       when copying iterate a copy (hence the use of `list(...)`)
        #       This allows node creation during iteration
        return list(self.groups[group_id].values())  # type: ignore

    def get_first_group_member(
        self,
        group_id: GroupID,
        /,
        # Used to hint type checkers of dynamic return type
        type_hint: type[T] = NodeType,
    ) -> T:
        """Get the first member of a specific group.

        Args:
            group_id (GroupID): The ID of the group to retrieve the first member from.
            type_hint (type[T], optional): Node type returned.
                Defaults to type[Node].

        Returns:
            T: The first node in the specified group.

        Raises:
            ValueError: If the group is empty.
        """
        for node in self.groups[group_id].values():
            return node  # type: ignore
        raise ValueError(f"No node in group {group_id}")

    def process(self) -> None:
        """Process the scene, executing all frame tasks.

        This method is called each frame to update the scene and its nodes,
        but can also be called manually to simulate time step.
        It will execute all registered frame tasks in the order of their priority.
        """
        for frame_task in self.frame_tasks.values():
            frame_task(self)

    def update(self) -> None:
        """Called each frame.

        Override this method in new subclass to implement custom update logic.
        """

    def on_enter(self) -> None:
        """Triggered when this scene is set as the current one."""

    def on_exit(self) -> None:
        """Triggered when this scene is no longer the current one."""


# Define core frame tasks


def update_self_scene(current_scene: Scene) -> None:
    """Update the scene itself, calling `update` on current scene."""
    current_scene.update()


def update_nodes(current_scene: Scene) -> None:
    """Update all nodes in the current scene, calling `update` on each node."""
    for node in current_scene.get_group_members(Group.NODE):
        node.update()


def free_queued_nodes(current_scene: Scene) -> None:
    """Free all queued nodes in the current scene, called at the end of each frame."""
    for node_id in current_scene._queued_nodes:
        for group in current_scene.groups.values():
            if node_id in group:
                del group[node_id]
    current_scene._queued_nodes.clear()


# Register core frame tasks
# Priorities are chosen with enough room to insert many more tasks in between
Scene.frame_tasks[100] = update_self_scene
Scene.frame_tasks[90] = update_nodes
Scene.frame_tasks[80] = free_queued_nodes
