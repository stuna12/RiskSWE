"""Circular clickable button used to represent countries on the map."""

import math
from collections.abc import Callable
from dataclasses import dataclass

import arcade
from arcade.types import Color


@dataclass
class Circle:
    """Position and size of a circular button."""
    x: int
    y: int
    radius: int

    def contains(self, px: int, py: int) -> bool:
        """Return True if the point (px, py) is inside the circle."""
        return math.hypot(px - self.x, py - self.y) <= self.radius


@dataclass
class ButtonColors:
    """Fill colors for each button state."""
    normal: Color = arcade.color.ORANGE
    hover: Color = arcade.color.ANTIQUE_RUBY
    inactive: Color = arcade.color.GRAY


@dataclass
class Outline:
    """Highlight ring drawn around a button."""
    color: Color
    width: int = 3


class CircleButton:
    """A custom circular button with text."""
    def __init__(self, circle: Circle, text: str, action: Callable[[], None] | None = None,
                 colors: ButtonColors | None = None):
        self.circle = circle
        self.text: str = text
        self.action = action  # The function to run when clicked
        self.colors = colors if colors is not None else ButtonColors()
        self.is_hovered = False
        self.active: bool = True
        self.outline: Outline | None = None

    def set_active(self, active: bool):
        """Enable or disable the button."""
        self.active = active

    def draw(self):
        """Draw the button, its outline, and its label."""
        # Choose color based on hover state
        color = self.colors.hover if self.is_hovered else self.colors.normal
        color = color if self.active else self.colors.inactive

        # Draw the circular button base
        arcade.draw_circle_filled(self.circle.x, self.circle.y, self.circle.radius, color)

        if self.outline is not None:
            arcade.draw_circle_outline(self.circle.x, self.circle.y, self.circle.radius + 3,
                                       self.outline.color, self.outline.width)

        # Draw the text centered inside the circle
        label = arcade.Text(self.text, self.circle.x, self.circle.y, arcade.color.WHITE,
                    font_size=14,
                    anchor_x="center",
                    anchor_y="center")
        label.draw()

    def check_hover(self, mouse_x: int, mouse_y: int):
        """Check if the mouse cursor is inside the circle."""
        self.is_hovered = self.circle.contains(mouse_x, mouse_y)

    def on_mouse_press(self):
        """Execute action if the button is clicked."""
        if self.is_hovered and self.active and self.action:
            self.action()
        if self.is_hovered:
            return True
        return False
