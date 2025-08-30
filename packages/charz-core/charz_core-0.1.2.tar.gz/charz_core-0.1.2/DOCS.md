# Documentation for `charz-core`

## Table of Contents

* [charz\_core](#charz_core)
* [charz\_core.\_annotations](#charz_core._annotations)
  * [Engine](#charz_core._annotations.Engine)
    * [frame\_tasks](#charz_core._annotations.Engine.frame_tasks)
* [charz\_core.\_camera](#charz_core._camera)
  * [CameraClassAttributes](#charz_core._camera.CameraClassAttributes)
  * [Camera](#charz_core._camera.Camera)
    * [set\_current](#charz_core._camera.Camera.set_current)
    * [as\_current](#charz_core._camera.Camera.as_current)
    * [is\_current](#charz_core._camera.Camera.is_current)
    * [with\_mode](#charz_core._camera.Camera.with_mode)
* [charz\_core.\_components.\_transform](#charz_core._components._transform)
  * [TransformComponent](#charz_core._components._transform.TransformComponent)
    * [with\_position](#charz_core._components._transform.TransformComponent.with_position)
    * [with\_global\_position](#charz_core._components._transform.TransformComponent.with_global_position)
    * [with\_rotation](#charz_core._components._transform.TransformComponent.with_rotation)
    * [with\_global\_rotation](#charz_core._components._transform.TransformComponent.with_global_rotation)
    * [with\_top\_level](#charz_core._components._transform.TransformComponent.with_top_level)
    * [set\_global\_x](#charz_core._components._transform.TransformComponent.set_global_x)
    * [set\_global\_y](#charz_core._components._transform.TransformComponent.set_global_y)
    * [global\_position](#charz_core._components._transform.TransformComponent.global_position)
    * [global\_position](#charz_core._components._transform.TransformComponent.global_position)
    * [global\_rotation](#charz_core._components._transform.TransformComponent.global_rotation)
    * [global\_rotation](#charz_core._components._transform.TransformComponent.global_rotation)
* [charz\_core.\_engine](#charz_core._engine)
  * [EngineMixinSorter](#charz_core._engine.EngineMixinSorter)
  * [Engine](#charz_core._engine.Engine)
    * [is\_running](#charz_core._engine.Engine.is_running)
    * [is\_running](#charz_core._engine.Engine.is_running)
    * [update](#charz_core._engine.Engine.update)
    * [run](#charz_core._engine.Engine.run)
  * [update\_self\_engine](#charz_core._engine.update_self_engine)
  * [process\_current\_scene](#charz_core._engine.process_current_scene)
* [charz\_core.\_frame\_task](#charz_core._frame_task)
  * [FrameTaskManager](#charz_core._frame_task.FrameTaskManager)
* [charz\_core.\_grouping](#charz_core._grouping)
  * [group](#charz_core._grouping.group)
* [charz\_core.\_node](#charz_core._node)
  * [NodeMixinSorter](#charz_core._node.NodeMixinSorter)
  * [Node](#charz_core._node.Node)
    * [\_\_new\_\_](#charz_core._node.Node.__new__)
    * [uid](#charz_core._node.Node.uid)
    * [\_\_init\_\_](#charz_core._node.Node.__init__)
    * [with\_parent](#charz_core._node.Node.with_parent)
    * [update](#charz_core._node.Node.update)
    * [queue\_free](#charz_core._node.Node.queue_free)
* [charz\_core.\_prefabs.\_node2d](#charz_core._prefabs._node2d)
  * [Node2D](#charz_core._prefabs._node2d.Node2D)
* [charz\_core.\_scene](#charz_core._scene)
  * [static\_load\_node\_type](#charz_core._scene.static_load_node_type)
  * [Scene](#charz_core._scene.Scene)
    * [preload](#charz_core._scene.Scene.preload)
    * [\_\_init\_\_](#charz_core._scene.Scene.__init__)
    * [set\_current](#charz_core._scene.Scene.set_current)
    * [as\_current](#charz_core._scene.Scene.as_current)
    * [get\_group\_members](#charz_core._scene.Scene.get_group_members)
    * [get\_first\_group\_member](#charz_core._scene.Scene.get_first_group_member)
    * [process](#charz_core._scene.Scene.process)
    * [update](#charz_core._scene.Scene.update)
    * [on\_enter](#charz_core._scene.Scene.on_enter)
    * [on\_exit](#charz_core._scene.Scene.on_exit)
  * [update\_self\_scene](#charz_core._scene.update_self_scene)
  * [update\_nodes](#charz_core._scene.update_nodes)
  * [free\_queued\_nodes](#charz_core._scene.free_queued_nodes)

<a id="charz_core"></a>

# Module `charz_core`

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

<a id="charz_core._annotations"></a>

# Module `charz_core._annotations`

Custom Annotations for `charz-core`
===================================

This file contains private annotations used across this package.

Whenever there is a "?" comment,
it means a type may or may not implement that field or mixin class.

<a id="charz_core._annotations.Engine"></a>

## Class `Engine`

```python
class Engine(_Protocol)
```

<a id="charz_core._annotations.Engine.frame_tasks"></a>

### `frame_tasks`

Global across instances

<a id="charz_core._camera"></a>

# Module `charz_core._camera`

<a id="charz_core._camera.CameraClassAttributes"></a>

## Class `CameraClassAttributes`

```python
class CameraClassAttributes(NodeMixinSorter)
```

Workaround to add class attributes to `Camera`.

<a id="charz_core._camera.Camera"></a>

## Class `Camera`

```python
class Camera(Node2D, metaclass=CameraClassAttributes)
```

`Camera` for controlling location of viewport in the world, per `Scene`.

To access the current camera, access `Camera.current`.
To set the current camera, use `Camera.current = <Camera>`,
or call `camera.set_current()` on the camera instance.
To set the current camera and return the instance, use `camera.as_current()`.

`NOTE` A default `Camera` will be used if not explicitly set.

**Example**:

  
```python
from charz_core import Engine, Camera

class MyGame(Engine):
    def __init__(self) -> None:
        # Configure how the current camera centers the viewport
        Camera.current.mode = Camera.MODE_CENTERED | Camera.MODE_INCLUDE_SIZE
```
  

**Attributes**:

- ``current`` - `ClassVar[property[Camera]]` - Current camera instance in use.
- ``mode`` - `CameraMode` - Mode to decide origin for centering.
  
  Variants for `Camera.mode`:
  - `Camera.MODE_FIXED`: Camera is fixed at upper left corner.
  - `Camera.MODE_CENTERED`: Camera is centered.
  - `Camera.MODE_INCLUDE_SIZE`: Camera includes texture size of parent to camera.
  

**Methods**:

  `set_current`
  `as_current` `chained`
  `is_current`
  `with_mode` `chained`

<a id="charz_core._camera.Camera.set_current"></a>

### `Camera.set_current`

```python
def set_current() -> None
```

Set this camera as the current camera.

<a id="charz_core._camera.Camera.as_current"></a>

### `Camera.as_current`

```python
def as_current() -> Self
```

Chained method to set this camera as the current camera.

**Returns**:

- `Self` - Same camera instance.

<a id="charz_core._camera.Camera.is_current"></a>

### `Camera.is_current`

```python
def is_current() -> bool
```

Check if this camera is the current camera of the current `Scene`.

**Returns**:

- `bool` - `True` if this camera is the current camera, `False` otherwise.

<a id="charz_core._camera.Camera.with_mode"></a>

### `Camera.with_mode`

```python
def with_mode(mode: CameraMode) -> Self
```

Chained method to set the camera's mode.

**Arguments**:

- `mode` _CameraMode_ - Enum variant to set the camera's mode.

<a id="charz_core._components._transform"></a>

# Module `charz_core._components._transform`

<a id="charz_core._components._transform.TransformComponent"></a>

## Class `TransformComponent`

```python
class TransformComponent()
```

`TransformComponent` mixin class for node.

**Examples**:

  
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
  

**Attributes**:

- ``position`` - `Vec2` - Position in local space.
- ``rotation`` - `float` - Angle in radians.
- ``top_level`` - `bool` - Indicating if the node is a top-level node.
- ``global_position`` - `property[Vec2]` - Copy of position in world space.
- ``global_rotation`` - `property[float]` - Rotation in world space.
  

**Methods**:

  `set_global_x`
  `set_global_y`

<a id="charz_core._components._transform.TransformComponent.with_position"></a>

### `TransformComponent.with_position`

```python
def with_position(
    position: Vec2 | None = None,
    *,
    x: float | None = None,
    y: float | None = None,
) -> Self
```

Chained method to set the node's position.

This method allows you to set the position of the node,
using either a `Vec2` instance or individual `x` and `y` coordinates.

**Arguments**:

- `position` _Vec2 | None, optional_ - Position of the node. Defaults to None.
- `x` _float | None, optional_ - X-coordinate of the node. Defaults to None.
- `y` _float | None, optional_ - Y-coordinate of the node. Defaults to None.
  

**Raises**:

- `TypeError` - If all arguments are `None` at the same time.
- `TypeError` - If both `position` and any of `x`/`y` are provided.
  

**Returns**:

- `Self` - Same node instance.

<a id="charz_core._components._transform.TransformComponent.with_global_position"></a>

### `TransformComponent.with_global_position`

```python
def with_global_position(
    global_position: Vec2 | None = None,
    *,
    x: float | None = None,
    y: float | None = None,
) -> Self
```

Chained method to set the node's global position.

This method allows you to set the global position of the node,
using either a `Vec2` instance or individual `x` and `y` coordinates.

**Arguments**:

- `global_position` _Vec2 | None, optional_ - Global position. Defaults to None.
- `x` _float | None, optional_ - Global x-coordinate of node. Defaults to None.
- `y` _float | None, optional_ - Global y-coordinate of node. Defaults to None.
  

**Raises**:

- `TypeError` - If all arguments are `None` at the same time.
- `TypeError` - If both `global_position` and any of `x`/`y` are provided.
  

**Returns**:

- `Self` - Same node instance.

<a id="charz_core._components._transform.TransformComponent.with_rotation"></a>

### `TransformComponent.with_rotation`

```python
def with_rotation(rotation: float) -> Self
```

Chained method to set the node's `rotation`.

**Arguments**:

- `rotation` _float_ - Rotation in radians.
  

**Returns**:

- `Self` - Same node instance.

<a id="charz_core._components._transform.TransformComponent.with_global_rotation"></a>

### `TransformComponent.with_global_rotation`

```python
def with_global_rotation(global_rotation: float) -> Self
```

Chained method to set the node's `global_rotation`.

**Arguments**:

- `global_rotation` _float_ - Global rotation in radians.
  

**Returns**:

- `Self` - Same node instance.

<a id="charz_core._components._transform.TransformComponent.with_top_level"></a>

### `TransformComponent.with_top_level`

```python
def with_top_level(state: bool = True) -> Self
```

Chained method to set the node's `top_level` state.

**Arguments**:

- `state` _bool, optional_ - Whether node is a top-level node. Defaults to True.
  

**Returns**:

- `Self` - Same node instance.

<a id="charz_core._components._transform.TransformComponent.set_global_x"></a>

### `TransformComponent.set_global_x`

```python
def set_global_x(x: float) -> None
```

Set node's global x-coordinate.

**Arguments**:

- `x` _float_ - Global x-coordinate.

<a id="charz_core._components._transform.TransformComponent.set_global_y"></a>

### `TransformComponent.set_global_y`

```python
def set_global_y(y: float) -> None
```

Set node's global y-coordinate.

**Arguments**:

- `y` _float_ - Global y-coordinate.

<a id="charz_core._components._transform.TransformComponent.global_position"></a>

### `TransformComponent.global_position`

```python
@property
def global_position() -> Vec2
```

Computes a copy of the node's global position (world space).

`NOTE` Cannot do the following:


Instead, you should use:


```python
self.global_position.x += 5
self.global_position.x = 42
```
```python
self.position.x += 5
self.set_global_x(42)
```

**Returns**:

- `Vec2` - Copy of global position.

<a id="charz_core._components._transform.TransformComponent.global_position"></a>

### `TransformComponent.global_position`

```python
@global_position.setter
def global_position(position: Vec2) -> None
```

Set node's global position (world space).

**Arguments**:

- `position` _Vec2_ - Global position.

<a id="charz_core._components._transform.TransformComponent.global_rotation"></a>

### `TransformComponent.global_rotation`

```python
@property
def global_rotation() -> float
```

Computes node's global rotation (world space).

**Returns**:

- `float` - Global rotation in radians.

<a id="charz_core._components._transform.TransformComponent.global_rotation"></a>

### `TransformComponent.global_rotation`

```python
@global_rotation.setter
def global_rotation(rotation: float) -> None
```

Set node's global rotation (world space).

**Arguments**:

- `rotation` _float_ - Global rotation in radians.

<a id="charz_core._engine"></a>

# Module `charz_core._engine`

<a id="charz_core._engine.EngineMixinSorter"></a>

## Class `EngineMixinSorter`

```python
class EngineMixinSorter(type)
```

Metaclass for sorting `Engine` to be the last base in MRO.

<a id="charz_core._engine.Engine"></a>

## Class `Engine`

```python
class Engine(metaclass=EngineMixinSorter)
```

`Engine` for managing the game loop and frame tasks.

Subclass this to create your main entry class.

**Example**:

  
```python
class MyGame(Engine):
    def __init__(self) -> None:
        ... # Initialize your nodes, preload scenes, etc.

    def update(self) -> None:
        ... # Your game logic here
```

<a id="charz_core._engine.Engine.is_running"></a>

### `Engine.is_running`

```python
@property
def is_running() -> bool
```

Check if main loop is running.

This attribute is wrapped in a property to protect it from being
overridden by subclass definitions.

**Example**:

  
  This will signal the type checker the following is not allowed:
  
```python
from charz_core import Engine

class MyGame(Engine):
    is_running: bool = True  # Invalid type, reported by type checker
```
  

**Returns**:

- `bool` - `True` if the main loop is running, `False` otherwise.

<a id="charz_core._engine.Engine.is_running"></a>

### `Engine.is_running`

```python
@is_running.setter
def is_running(run_state: bool) -> None
```

Set the running state of the main loop.

**Arguments**:

- `run_state` _bool_ - `True` to start/continue the main loop, `False` to stop it.

<a id="charz_core._engine.Engine.update"></a>

### `Engine.update`

```python
def update() -> None
```

Called each frame.

Override this method in new subclass to implement custom update logic.

<a id="charz_core._engine.Engine.run"></a>

### `Engine.run`

```python
def run() -> None
```

Run app/game, which will start the main loop.

This will run the main loop until `is_running` is set to `False`.

<a id="charz_core._engine.update_self_engine"></a>

## `update_self_engine`

```python
def update_self_engine(engine: Engine) -> None
```

Update the engine itself, calling its `update` method.

<a id="charz_core._engine.process_current_scene"></a>

## `process_current_scene`

```python
def process_current_scene(_engine: Engine) -> None
```

Process the current scene (`Scene.current`), calling its `process` method.

<a id="charz_core._frame_task"></a>

# Module `charz_core._frame_task`

<a id="charz_core._frame_task.FrameTaskManager"></a>

## Class `FrameTaskManager`

```python
class FrameTaskManager(Generic[T], dict[Priority, FrameTask[T]])
```

A dict-like manager that auto-sorts tasks by priority.

`NOTE` The higher the priority, the earlier the task will be executed.

<a id="charz_core._grouping"></a>

# Module `charz_core._grouping`

<a id="charz_core._grouping.group"></a>

## `group`

```python
def group(group_id: GroupID) -> Callable[[type[T]], type[T]]
```

Decorator that adds `node`/`component` to the given `group`.

**Example**:

  
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
  

**Arguments**:

- `group_id` _GroupID_ - *Hashable* object used for group ID
  

**Returns**:

  Callable[[type[T]], type[T]]: Wrapped class

<a id="charz_core._node"></a>

# Module `charz_core._node`

<a id="charz_core._node.NodeMixinSorter"></a>

## Class `NodeMixinSorter`

```python
class NodeMixinSorter(type)
```

Metaclass for sorting `Node` to be the last base in MRO.

<a id="charz_core._node.Node"></a>

## Class `Node`

```python
@group(Group.NODE)
class Node(metaclass=NodeMixinSorter)
```

`Node` base class.

All nodes existing in a scene (either "physically" or "theoretically"),
will be instances of either this class, or a subclass.
Subclasses can be combined with component mixins, using Python's multiple inheritance.
This class can be instantiated directly, but in itself it does not do anything useful.

The reference of nodes is stored in `Scene.groups[Group.NODE]`,
which is a dictionary mapping `NodeID` to `Node` instances.
It keeps the node alive, and prevents it from being garbage collected.

**Example**:

  
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

<a id="charz_core._node.Node.__new__"></a>

### `Node.__new__`

```python
def __new__(
    cls,
    *_args: Any,
    **_kwargs: Any,
) -> Self
```

Last in the `__new__` chain, which assigns `uid`.

<a id="charz_core._node.Node.uid"></a>

### `uid`

Is set in `Node.__new__`

<a id="charz_core._node.Node.__init__"></a>

### `Node.__init__`

```python
def __init__(parent: Node | None = None) -> None
```

Initialize node.

<a id="charz_core._node.Node.with_parent"></a>

### `Node.with_parent`

```python
def with_parent(parent: Node | None) -> Self
```

Chained method to set parent node.

<a id="charz_core._node.Node.update"></a>

### `Node.update`

```python
def update() -> None
```

Called each frame.

Override this method in subclasses to implement custom update logic.

<a id="charz_core._node.Node.queue_free"></a>

### `Node.queue_free`

```python
def queue_free() -> None
```

Queues this node for freeing.

This method should be called when you want to remove the node from the scene.
It will be freed at the end of the current frame, handled by `Engine.frame_tasks`.

<a id="charz_core._prefabs._node2d"></a>

# Module `charz_core._prefabs._node2d`

<a id="charz_core._prefabs._node2d.Node2D"></a>

## Class `Node2D`

```python
class Node2D(TransformComponent, Node)
```

`Node2D` node that exists in 2D space.

Has a transform (position, rotation).
All 2D nodes, including sprites, inherit from Node2D.
Use Node2D as a parent node to move, hide and rotate children in a 2D project.

**Example**:

  
  Extending `Node2D` with components:
  
```python
from charz_core import Node2D

class ColorComponent:
    color: str = "green"

class GreenPoint(Node2D, ColorComponent):
    ...

assert ColoredPoint().color == "green"
```

<a id="charz_core._scene"></a>

# Module `charz_core._scene`

<a id="charz_core._scene.static_load_node_type"></a>

## `static_load_node_type`

```python
def static_load_node_type() -> type[Node]
```

Workaround for the static type checker, to prevent circular dependencies.

<a id="charz_core._scene.Scene"></a>

## Class `Scene`

```python
class Scene(metaclass=SceneClassProperties)
```

`Scene` to encapsulate dimensions/worlds.

Instantiating a scene (either of type `Scene` or subclass of `Scene`),
will set that new scene instance to the current scene.

**Example**:

  
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

<a id="charz_core._scene.Scene.preload"></a>

### `Scene.preload`

```python
@classmethod
def preload() -> Self
```

Preload the scene class, creating an instance without setting it as current.

**Returns**:

- `Self` - An instance of the scene class, without setting it as current.

<a id="charz_core._scene.Scene.__init__"></a>

### `Scene.__init__`

```python
def __init__() -> None
```

Override to instantiate nodes and state related to this scene.

<a id="charz_core._scene.Scene.set_current"></a>

### `Scene.set_current`

```python
def set_current() -> None
```

Set this scene as the current one.

<a id="charz_core._scene.Scene.as_current"></a>

### `Scene.as_current`

```python
def as_current() -> Self
```

Chained method to set this scene as the current one.

<a id="charz_core._scene.Scene.get_group_members"></a>

### `Scene.get_group_members`

```python
def get_group_members(
    group_id: GroupID,
    type_hint: type[T] = NodeType,
) -> list[T]
```

Get all members of a specific group.

**Arguments**:

- `group_id` _GroupID_ - The ID of the group to retrieve members from.
- `type_hint` _type[T], optional_ - Node type in list returned.
  Defaults to type[Node].
  

**Returns**:

- `list[T]` - A list of nodes in the specified group.

<a id="charz_core._scene.Scene.get_first_group_member"></a>

### `Scene.get_first_group_member`

```python
def get_first_group_member(
    group_id: GroupID,
    type_hint: type[T] = NodeType,
) -> T
```

Get the first member of a specific group.

**Arguments**:

- `group_id` _GroupID_ - The ID of the group to retrieve the first member from.
- `type_hint` _type[T], optional_ - Node type returned.
  Defaults to type[Node].
  

**Returns**:

- `T` - The first node in the specified group.
  

**Raises**:

- `ValueError` - If the group is empty.

<a id="charz_core._scene.Scene.process"></a>

### `Scene.process`

```python
def process() -> None
```

Process the scene, executing all frame tasks.

This method is called each frame to update the scene and its nodes,
but can also be called manually to simulate time step.
It will execute all registered frame tasks in the order of their priority.

<a id="charz_core._scene.Scene.update"></a>

### `Scene.update`

```python
def update() -> None
```

Called each frame.

Override this method in new subclass to implement custom update logic.

<a id="charz_core._scene.Scene.on_enter"></a>

### `Scene.on_enter`

```python
def on_enter() -> None
```

Triggered when this scene is set as the current one.

<a id="charz_core._scene.Scene.on_exit"></a>

### `Scene.on_exit`

```python
def on_exit() -> None
```

Triggered when this scene is no longer the current one.

<a id="charz_core._scene.update_self_scene"></a>

## `update_self_scene`

```python
def update_self_scene(current_scene: Scene) -> None
```

Update the scene itself, calling `update` on current scene.

<a id="charz_core._scene.update_nodes"></a>

## `update_nodes`

```python
def update_nodes(current_scene: Scene) -> None
```

Update all nodes in the current scene, calling `update` on each node.

<a id="charz_core._scene.free_queued_nodes"></a>

## `free_queued_nodes`

```python
def free_queued_nodes(current_scene: Scene) -> None
```

Free all queued nodes in the current scene, called at the end of each frame.

