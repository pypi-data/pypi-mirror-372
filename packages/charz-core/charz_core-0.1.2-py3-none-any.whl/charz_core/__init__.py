"""
Charz Core
==========

Core logic for `charz`

Includes
--------

- Annotations
  - `Self`  (from standard `typing` or from package `typing-extensions`)
- Math (from package `linflex`)
  - `lerp`
  - `sign`
  - `clamp`
  - `move_toward`
  - `Vec2`
  - `Vec2i`
  - `Vec3`
- Framework
  - `Engine`
  - `Scene`
- Decorators
  - `group`
- Enums
  - `Group`
- Components
  - `TransformComponent`
- Nodes
  - `Camera`
  - `Node`
  - `Node2D`
"""

__all__ = [
    "Engine",
    "Camera",
    "Scene",
    "group",
    "Group",
    "Node",
    "Self",
    "Node2D",
    "TransformComponent",
    "lerp",
    "sign",
    "clamp",
    "move_toward",
    "Vec2",
    "Vec2i",
    "Vec3",
]

# Re-exports
from linflex import lerp, sign, clamp, move_toward, Vec2, Vec2i, Vec3

# Exports
from ._annotations import Self  # Version proof
from ._engine import Engine
from ._camera import Camera
from ._scene import Scene
from ._grouping import Group, group
from ._node import Node
from ._components.transform import TransformComponent
from ._prefabs.node2d import Node2D
