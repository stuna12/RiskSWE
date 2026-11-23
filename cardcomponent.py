"""A GUI Object Representing A Card"""

from typing import ClassVar

import arcade
from arcade.types import Color
from arcade import Texture
from card import Card

class CardComponent:
    """Custom Class For Rendering A Card"""

    _army_textures: ClassVar[list[Texture] | None] = None
    _window_width = 0
    _window_height = 0

    def __init__(self, card: Card):
        self.card = card
        self.bounds = arcade.XYWH(0, 0, 0, 0)
        self.is_hovered = False
        self.active: bool = False
        self.selected: bool = False

    @classmethod
    def load_textures(cls) -> list[Texture]:
        """Loads army textures from memory if they are not already"""
        if cls._army_textures is None:
            cls._army_textures = \
                [arcade.load_texture("resources/a" + str(i) + ".png") for i in range(3)]
        return cls._army_textures

    def set_active(self, active: bool):
        """Enable or disable selection"""
        self.active = active

    def set_selected(self, selected: bool):
        """Set card selected"""
        self.selected = selected

    def update_bounds(self, left, bottom, width, height):
        """Update the bounds of the rectangle corresponding to the card"""
        self.bounds = arcade.LBWH(left, bottom, width, height)

    def draw(self) -> None:
        """Draw the button, its outline, and its label."""
        # Choose color based on hover state
        color = Color(255,255,255) if self.selected or self.active else Color(150, 150, 150)

        if self.selected or (self.is_hovered and self.active):
            self.bounds = arcade.LBWH(self.bounds.left, self.bounds.height/4,
                                      self.bounds.width, self.bounds.height)
        else:
            self.bounds = arcade.LBWH(self.bounds.left, 0,
                                      self.bounds.width, self.bounds.height)

        # draw the actual card
        arcade.draw_rect_filled(self.bounds, color)
        arcade.draw_rect_outline(self.bounds, Color(0, 0, 0))

        # NOTE pylint can't typecheck this, so will complain unless disabled per-line, as below
        textures = self.load_textures()

        # if wildcard
        if self.card.wildcard:
            for i in range(3):
                rect = arcade.XYWH(self.bounds.x, (i + 1) * self.bounds.y / 4,
                                   self.bounds.width, self.bounds.width)
                arcade.draw_texture_rect(textures[i], rect) # pylint: disable=unsubscriptable-object
        else:
            rect = arcade.XYWH(self.bounds.x, self.bounds.y, self.bounds.width, self.bounds.width)
            arcade.draw_texture_rect(textures[self.card.army], rect) # pylint: disable=unsubscriptable-object


    def check_hover(self, mouse_x: int, mouse_y: int):
        """Check if the mouse cursor is inside the card."""
        self.is_hovered = self.bounds.point_in_rect((mouse_x, mouse_y))
