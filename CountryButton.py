import arcade
import math

class CircleButton:
    """A custom circular button with text."""
    def __init__(self, center_x, center_y, radius, text, action=None,
            normal_color=arcade.color.ORANGE, hover_color=arcade.color.ANTIQUE_RUBY,
            inactive_color=arcade.color.GRAY):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.text = text
        self.normal_color = normal_color
        self.hover_color = hover_color
        self.action = action  # The function to run when clicked
        self.is_hovered = False
        self.active = True
        self.inactive_color = inactive_color
        self.outline = None   # Highlight ring
        self.outline_width = 3

    def set_active(self, active):
        self.active = active

    def draw(self):
        # Choose color based on hover state
        color = self.hover_color if self.is_hovered else self.normal_color
        color = color if self.active else self.inactive_color

        # Draw the circular button base
        arcade.draw_circle_filled(self.center_x, self.center_y, self.radius, color)

        if self.outline is not None:
            arcade.draw_circle_outline(self.center_x, self.center_y, self.radius + 3,
                                       self.outline, self.outline_width)
        
        # Draw the text centered inside the circle
        arcade.draw_text(
            self.text,
            self.center_x,
            self.center_y,
            arcade.color.WHITE,
            font_size=14,
            anchor_x="center",
            anchor_y="center"
        )

    def check_hover(self, mouse_x, mouse_y):
        """Check if the mouse cursor is inside the circle."""
        # Calculate distance between mouse and center of the circle
        distance = math.sqrt((mouse_x - self.center_x) ** 2 + (mouse_y - self.center_y) ** 2)
        self.is_hovered = distance <= self.radius

    def on_mouse_press(self):
        """Execute action if the button is clicked."""
        if self.is_hovered and self.active and self.action:
            self.action()
        if self.is_hovered:
            return True
        return False
