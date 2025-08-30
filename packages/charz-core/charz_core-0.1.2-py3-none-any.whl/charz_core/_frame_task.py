from __future__ import annotations

from typing import TypeVar, TypeAlias, Generic, Callable

# NOTE: These annotaion-related variables exist here to prevent circular import error
T = TypeVar("T")
Priority: TypeAlias = int
FrameTask: TypeAlias = Callable[[T], None]


class FrameTaskManager(Generic[T], dict[Priority, FrameTask[T]]):
    """A dict-like manager that auto-sorts tasks by priority.

    `NOTE` The higher the priority, the earlier the task will be executed.
    """

    def __setitem__(self, key: Priority, value: FrameTask[T]) -> None:
        super().__setitem__(key, value)
        sorted_items = sorted(self.items(), reverse=True)
        self.clear()
        self.update(sorted_items)

    def __repr__(self) -> str:
        # Produces: [Priority]: [Function Name] :: [Function Docstring?]
        return (
            self.__class__.__name__
            + f"[{T}]("
            + "".join(
                f"\n| {priority}: {function.__qualname__} -- "
                f'"{"<No Docstring>" if function.__doc__ is None else function.__doc__}"'
                for (priority, function) in self.items()
            )
            + "\n)"
        )
