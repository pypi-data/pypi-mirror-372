from __future__ import annotations

from math import cos, sin
from dataclasses import dataclass
from copy import deepcopy
from typing import Any

from charz_core import Scene, TransformComponent, Vec2, Self, group

from .._grouping import Group
from .._annotations import ColliderNode


@dataclass(kw_only=True)
class Hitbox:
    """Hitbox dataclass for collision shape data.

    Example:

    Creating and centering `Hitbox` to a new collision node:

    ```python
    # collision_box.py
    from charz import Sprite, CollisionComponent, Hitbox, Vec2

    class CollisionBox(Sprite, CollisionComponent):
        hitbox = Hitbox(
            size=Vec2(5, 3),
            centered=True,  # Centering of collision hitbox
        )
        centered = True  # Centering of texture
        texture = [
            "#####",
            "#####",
            "#####",
        ]
    ```

    Attributes:
        `size`: `Vec2` - Width and height of the hitbox.
        `centered`: `bool` - Whether hitbox is centered around the node's global position.
            Defaults to `False`, meaning the hitbox starts at the node's position,
            and expanding to the right and downwards.
        `disabled`: `bool` - Whether collision with node is disabled.
            Defaults to `False`, meaning collision is active on with node.
        `margin`: `float` - Inverse margin around the hitbox for collision detection.
            Defaults to `1`, and should not be smaller than `1e-2`.
    """

    size: Vec2
    centered: bool = False
    disabled: bool = False
    margin: float = 1.0


@group(Group.COLLIDER)
class ColliderComponent:  # Component (mixin class)
    """`ColliderComponent` mixin class for node.

    Assign this component to a node to enable collision detection.
    All other collider components will then do collision detection against this node,
    when `is_colliding` and `get_colliders` is called.

    You can also use `is_colliding_with` for more fine-grained control.
    *Custom collision checks* can therefore be implemented by **overriding
    this method in a subclass**.

    Examples:

    Creating a boxes with collision, then printing the ones that collide:

    ```python
    # collision_box.py
    import colex
    from charz import Sprite, CollisionComponent, Hitbox, Vec2

    class CollisionBox(Sprite, CollisionComponent):
        hitbox = Hitbox(size=Vec2(5, 3))  # Usually matches the size of `texture`
        texture = [
            "#####",
            "#####",
            "#####",
        ]

    # main.py
    from charz import Engine
    from .collision_box import CollisionBox

    class MyGame(Engine):
        def __init__(self) -> None:
            self.box1 = CollisionBox(position=Vec2(2, 5), color=colex.RED)
            self.box2 = CollisionBox(position=Vec2(4, 7), color=colex.BLUE)
            self.box3 = CollisionBox(position=Vec2(5, 9), color=colex.GREEN)
            print(self.box2.get_colliders())

    # Prints out
    >>> ['CollisionBox(#0:Vec2(2, 5):0R:5x3:None)',
         'CollisionBox(#2:Vec2(5, 9):0R:5x3:None)']
    ```

    Filtering collision results, and deleting if collision occurs:

    ```python
    # Extending the last example...

    class Lethal: ...  # This works as a "tag" that can be detected using `isinstance`

    class LethalBox(Lethal, CollisionBox): ...

    box = CollisionBox(position=Vec2(4, 7))
    LethalBox(position=Vec2(3, 6))  # Remember: Reference not needed to create node

    for collider in box.get_colliders():
        if isinstance(collider, Lethal):
            print("Killed by", collider)
            box.queue_free()

    # Prints out
    >>> 'Killed by LethalBox(#1:Vec2(3, 6):0R:5x3:None)'
    ```

    Attributes:
        `hitbox`: `Hitbox` - The hitbox data for collision detection.
        `disabled`: `bool` - Whether the collider is disabled.

    Methods:
        `get_colliders`
        `is_colliding`
        `is_colliding_with`
    """

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        instance = super().__new__(cls, *args, **kwargs)
        if (class_hitbox := getattr(instance, "hitbox", None)) is not None:
            instance.hitbox = deepcopy(class_hitbox)
        else:
            instance.hitbox = Hitbox(size=Vec2.ZERO)
        return instance

    hitbox: Hitbox

    def with_hitbox(self, hitbox: Hitbox, /) -> Self:
        """Chained method to set the hitbox.

        Args:
            hitbox (Hitbox): The hitbox to set.

        Returns:
            Self: Same node instance.
        """
        self.hitbox = hitbox
        return self

    def get_colliders(self) -> list[ColliderNode]:
        """Get a list of colliders that this node is colliding with.

        This method iterates through all nodes in the `Group.Collider` group and checks
        if this node is colliding with any of them.

        Returns:
            list[ColliderNode]: List of colliders that this node is colliding with.
        """
        assert isinstance(self, ColliderComponent)
        nodes_collided_with: list[ColliderNode] = []
        # NOTE: Iterate `dict_values` instead of creating a `list` for speed
        for node in Scene.current.groups[Group.COLLIDER].values():
            if self is node:
                continue
            # Ignoring incorrect type because group `Group.Collider`
            # should only contain `ColliderNode` instances
            if self.is_colliding_with(node):  # type: ignore
                nodes_collided_with.append(node)  # type: ignore
        return nodes_collided_with

    def is_colliding(self) -> bool:
        """Check if this node is colliding with any other collider node.

        This method iterates through all nodes in the `Group.Collider` group and checks
        if this node is colliding with any of them.

        Returns:
            bool: Whether this node is colliding with any other collider node.
        """
        assert isinstance(self, ColliderComponent)
        for node in Scene.current.groups[Group.COLLIDER].values():
            if self is node:
                continue
            # Ignoring incorrect type because group `Group.Collider`
            # should only contain `ColliderNode` instances
            if self.is_colliding_with(node):  # type: ignore
                return True
        return False

    def is_colliding_with(self, collider_node: ColliderNode, /) -> bool:
        """Check if this node is colliding with another collider node.

        Uses SAT (Separating Axis Theorem).

        `NOTE` Does not yet fully support rotated hitboxes.

        Args:
            collider_node (ColliderNode): The other collider node to check collision with.

        Returns:
            bool: Whether this node is colliding with the other collider node.
        """
        if self.hitbox.disabled or collider_node.hitbox.disabled:
            return False

        corners_a = self.get_corner_points()
        corners_b = collider_node.get_corner_points()

        # Axes to test: x and y
        axes = [Vec2(1, 0), Vec2(0, 1)]

        for axis in axes:
            min_a, max_a = self._get_projection_range(corners_a, axis)
            min_b, max_b = self._get_projection_range(corners_b, axis)
            # Hitbox margin is negative space inside the hitbox,
            # extending from the edges
            if (
                max_a - self.hitbox.margin < min_b
                or max_b - collider_node.hitbox.margin < min_a
            ):
                return False  # Separating axis found

        return True  # No separating axis found, collision detected

    def get_corner_points(self) -> tuple[Vec2, Vec2, Vec2, Vec2]:
        assert isinstance(self, TransformComponent), (
            f"Node {self} missing `TransformComponent`"
        )
        global_position = self.global_position
        global_rotation = self.global_rotation
        hitbox_size = self.hitbox.size

        # Center the hitbox if needed
        if self.hitbox.centered:
            global_position = global_position - hitbox_size / 2

        # Define corners relative to position
        corners = (
            Vec2.ZERO,
            Vec2(hitbox_size.x, 0),
            hitbox_size,
            Vec2(0, hitbox_size.y),
        )

        # Rotate corners around the hitbox center
        if global_rotation != 0.0:
            center = global_position + hitbox_size / 2
            rotated = []
            for corner in corners:
                relative = global_position + corner - center
                rotated_corner = (
                    Vec2(
                        relative.x * cos(global_rotation)
                        - relative.y * sin(global_rotation),
                        relative.x * sin(global_rotation)
                        + relative.y * cos(global_rotation),
                    )
                    + center
                )
                rotated.append(rotated_corner)
            return tuple(rotated)
        else:
            return (  # Expanded to pass type checking
                global_position + corners[0],
                global_position + corners[1],
                global_position + corners[2],
                global_position + corners[3],
            )

    @staticmethod
    def _get_projection_range(
        corners: tuple[Vec2, Vec2, Vec2, Vec2],
        axis: Vec2,
    ) -> tuple[float, float]:
        projections = [corner.dot(axis) for corner in corners]
        return (min(projections), max(projections))
