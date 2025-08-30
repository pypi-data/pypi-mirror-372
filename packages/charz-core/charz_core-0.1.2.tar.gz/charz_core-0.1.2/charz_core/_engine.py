from __future__ import annotations

from typing import ClassVar

from typing_extensions import Self

from ._frame_task import FrameTaskManager
from ._scene import Scene


class EngineMixinSorter(type):
    """Metaclass for sorting `Engine` to be the last base in MRO."""

    def __new__(
        cls,
        name: str,
        bases: tuple[type, ...],
        attrs: dict[str, object],
    ) -> type:
        def sorter(base: type) -> bool:
            # Ensures `Engine` will be last in MRO (except for `object`),
            # to help `__new__` chain for nodes (instances of `Engine`/`Engine` subclass)
            # work despite wrong order in subclass declaration
            return issubclass(base, Engine)

        sorted_bases = tuple(sorted(bases, key=sorter))
        new_type = super().__new__(cls, name, sorted_bases, attrs)
        return new_type


class Engine(metaclass=EngineMixinSorter):
    """`Engine` for managing the game loop and frame tasks.

    Subclass this to create your main entry class.

    Example:

    ```python
    class MyGame(Engine):
        def __init__(self) -> None:
            ... # Initialize your nodes, preload scenes, etc.

        def update(self) -> None:
            ... # Your game logic here
    ```
    """

    # Tasks are shared across all engines
    frame_tasks: ClassVar[FrameTaskManager[Self]] = FrameTaskManager()
    # Using setter and getter to prevent subclass def overriding
    _is_running: bool = False

    @property
    def is_running(self) -> bool:
        """Check if main loop is running.

        This attribute is wrapped in a property to protect it from being
        overridden by subclass definitions.

        Example:

        This will signal the type checker the following is not allowed:

        ```python
        from charz_core import Engine

        class MyGame(Engine):
            is_running: bool = True  # Invalid type, reported by type checker
        ```

        Returns:
            bool: `True` if the main loop is running, `False` otherwise.
        """
        return self._is_running

    @is_running.setter
    def is_running(self, run_state: bool) -> None:
        """Set the running state of the main loop.

        Args:
            run_state (bool): `True` to start/continue the main loop, `False` to stop it.
        """
        self._is_running = run_state

    def update(self) -> None:
        """Called each frame.

        Override this method in new subclass to implement custom update logic.
        """

    def run(self) -> None:
        """Run app/game, which will start the main loop.

        This will run the main loop until `is_running` is set to `False`.
        """
        self.is_running = True
        while self.is_running:
            for frame_task in self.frame_tasks.values():
                frame_task(self)


# Define core frame tasks


def update_self_engine(engine: Engine) -> None:
    """Update the engine itself, calling its `update` method."""
    engine.update()


def process_current_scene(_engine: Engine) -> None:
    """Process the current scene (`Scene.current`), calling its `process` method."""
    Scene.current.process()


# Register core frame tasks
# Priorities are chosen with enough room to insert many more tasks in between
Engine.frame_tasks[100] = update_self_engine
Engine.frame_tasks[90] = process_current_scene
