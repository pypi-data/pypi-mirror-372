from __future__ import annotations
from typing_extensions import Self

__all__ = ("SimpleMovementComponent",)

from typing import TYPE_CHECKING, NoReturn, Any

from charz_core import Scene, TransformComponent, Vec2, group

from .._time import Time
from .._grouping import Group

if TYPE_CHECKING:
    import keyboard
else:
    keyboard = None

loaded_simple_movement = False


# Use lazy loading to allow for not using `keyboard` module, as long as it is never used
def __getattr__(name: str) -> type[SimpleMovementComponent] | NoReturn:
    global keyboard  # noqa: PLW0603
    if keyboard is None:
        try:
            import keyboard as _keyboard  # noqa: PLC0415

            keyboard = _keyboard
        except ModuleNotFoundError as error:
            raise ModuleNotFoundError(
                "Module 'keyboard' was not found,"
                " use 'charz' with 'keyboard' or 'all' feature flag,"
                " like depending on 'charz[keyboard]' in 'pyproject.toml'"
            ) from error

    # Add frame task - Once the component is loaded
    global loaded_simple_movement  # noqa: PLW0603
    if not loaded_simple_movement:
        loaded_simple_movement = True
        Scene.frame_tasks[65] = update_moving_nodes

    # FIXME: Argument `name` has sometimes a value of `__path__`
    if name not in __all__:
        raise AttributeError(f"Module '{__name__}' has no attribute '{name}'")

    return SimpleMovementComponent


@group(Group.MOVEMENT)
class SimpleMovementComponent:  # Component (mixin class)
    """`SimpleMovementComponent` mixin class for node.

    It provides basic movement functionality for a node,
    and allows the node to move in 2D space using the `WASD` keys.

    Example:

    Player class with the ability to move using `WASD`:

    ```python
    from charz import Sprite
    from charz import SimpleMovementComponent

    class Player(Sprite, SimpleMovementComponent):
        texture = ["@"]
    ```

    Attributes:
        `speed`: `float` - The speed of the node's movement per second (`units/s`).
            Defaults to `16` `units/s`, which is a reasonable speed for most games.
            You can change this value to make the node move faster or slower,
            by overriding this attribute in your node class as a class attribute.
            When `use_delta_time` is `False`, the unit will be `units/frame`.
            Movement direction is normalized when `normalize_movement` is `True`.
        `use_delta_time`: `bool` - Whether to use delta time for movement.
            Defaults to `True`; movement will be frame-rate independent.
        `normalize_movement`: `bool` - Whether to normalize the movement direction vector.
            Defaults to `True`; movement direction will always have a length of `1`.

    Methods:
        `is_moving_left`
        `is_moving_right`
        `is_moving_up`
        `is_moving_down`
        `get_movement_direction`
    """

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        # Workaround when using `@group`
        return super().__new__(cls, *args, **kwargs)

    speed: float = 16
    use_delta_time: bool = True
    normalize_movement: bool = True

    def is_moving_left(self) -> bool:
        """Check if the node is moving left.

        Override implementation to change the key used for moving left.

        Returns:
            `bool`: `True` if the node is moving left, `False` otherwise.
        """
        return keyboard.is_pressed("a")

    def is_moving_right(self) -> bool:
        """Check if the node is moving right.

        Override implementation to change the key used for moving right.

        Returns:
            `bool`: `True` if the node is moving right, `False` otherwise.
        """
        return keyboard.is_pressed("d")

    def is_moving_up(self) -> bool:
        """Check if the node is moving up.

        Override implementation to change the key used for moving up.

        Returns:
            `bool`: `True` if the node is moving up, `False` otherwise.
        """
        return keyboard.is_pressed("w")

    def is_moving_down(self) -> bool:
        """Check if the node is moving down.

        Override implementation to change the key used for moving down.

        Returns:
            `bool`: `True` if the node is moving down, `False` otherwise.
        """
        return keyboard.is_pressed("s")

    def get_movement_direction(self) -> Vec2:
        """Get the movement direction of the node.

        This method returns a `Vec2` object representing the direction
        of movement based on the current input.

        `NOTE` The returned vector is **not** normalized,
        meaning it can have a length greater than `1`.

        Returns:
            `Vec2`: Raw direction vector.
        """
        return Vec2(
            self.is_moving_right() - self.is_moving_left(),
            self.is_moving_down() - self.is_moving_up(),
        )

    def update_movement(self) -> None:
        """Custom update method for the node.

        Automatically handles checking for movement input,
        and moving the node accordingly.
        """
        assert isinstance(self, TransformComponent), (
            f"Node {self} missing `TransformComponent`"
        )
        direction = self.get_movement_direction()
        if self.normalize_movement:
            direction = direction.normalized()

        distance_delta = direction * self.speed
        if self.use_delta_time:
            distance_delta *= Time.delta

        self.position += distance_delta


# Define lazy added scene frame task


def update_moving_nodes(current_scene: Scene) -> None:
    """Update moving nodes in the current scene."""
    for moving_node in current_scene.get_group_members(
        Group.MOVEMENT,
        type_hint=SimpleMovementComponent,
    ):
        moving_node.update_movement()
