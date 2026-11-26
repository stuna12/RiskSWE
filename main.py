"""Entry point for the Risk game: opens the window and main menu."""

import arcade
import arcade.gui
from game_view import RiskGame, PlayerKind, PLAYER_SETUPS, MIN_PLAYERS

WINDOW_TITLE = "Risk"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

BACKGROUND_COLOR = arcade.color.ALMOND
TERRITORY_COUNT = 42



class MainMenuView(arcade.View):
    """The initial Main Menu screen containing the GUI buttons."""

    def __init__(self):
        super().__init__()
        # The UIManager is the backbone of the GUI system
        self.manager = arcade.gui.UIManager()
        # One per color in PLAYER_SETUPS
        self.kinds = (
            [PlayerKind.HUMAN, PlayerKind.AI] + 
            [PlayerKind.OFF] * (len(PLAYER_SETUPS) - 2)
        )

        # Shows validation messages
        self.error_label = arcade.gui.UILabel(text="", font_size=14, width=380,
                                              text_color=arcade.color.LIGHT_SALMON)

    def on_show_view(self):
        """Called when this view becomes active."""
        # Enable the UIManager to capture mouse events/clicks
        self.manager.enable()
        self.manager.clear()
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        # Create a layout structure to hold our elements
        # UIAnchorLayout helps center our box layout on the screen
        anchor_layout = arcade.gui.UIAnchorLayout()

        # UIBoxLayout stacks widgets vertically by default
        v_box = arcade.gui.UIBoxLayout(space_between=20)

        # Add a title label
        title_label = arcade.gui.UILabel(
            text="Main Menu",
            font_size=32,
            font_name="Arial",
            text_color=arcade.color.WHITE
        )
        v_box.add(title_label)

        # One row per color: color, name, and button for cycling Human to AI to Off
        for index, (name, color) in enumerate(PLAYER_SETUPS):
            row = arcade.gui.UIBoxLayout(vertical=False, space_between=15)
            row.add(arcade.gui.UISpace(width=40, height=40, color=color))
            row.add(arcade.gui.UILabel(text=name, font_size=20, width=110,
                                       text_color=arcade.color.WHITE))
            kind_button = arcade.gui.UIFlatButton(text=self.kinds[index].value, width=140)
            kind_button.event("on_click")(self._make_cycle_handler(index, kind_button))
            row.add(kind_button)
            v_box.add(row)

        self.error_label.text = ""
        v_box.add(self.error_label)

        start_button = arcade.gui.UIFlatButton(text="Start Game", width=200)
        start_button.event("on_click")(self._on_start)
        v_box.add(start_button)

        # Center the v_box within the anchor layout
        anchor_layout.add(v_box, anchor_x="center", anchor_y="center")

        # Add our layout to the UIManager
        self.manager.add(anchor_layout)

    def _make_cycle_handler(self, index, button):
        """Makes click handler to cycle a color's setting."""
        order = [PlayerKind.HUMAN, PlayerKind.AI, PlayerKind.OFF]

        def on_click(_event):
            self.kinds[index] = order[(order.index(self.kinds[index]) + 1) % len(order)]
            button.text = self.kinds[index].value
        return on_click

    def _on_start(self, _event):
        """Validate selections and start game."""
        playing = [k for k in self.kinds if k != PlayerKind.OFF]
        if len(playing) < MIN_PLAYERS:
            self.error_label.text = f"Select at least {MIN_PLAYERS} players"
            return
        if PlayerKind.HUMAN not in playing:
            self.error_label.text = "Make at least one player Human"
            return
        game_view = RiskGame()
        game_view.setup(list(self.kinds))
        self.window.show_view(game_view)

    def on_hide_view(self):
        """Called when switching away from this view."""
        # Clean up and disable the manager so it stops processing inputs
        self.manager.disable()

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            arcade.close_window()

    def on_draw(self):
        """Render the menu screen."""
        self.clear()
        # Draw all GUI widgets managed by the UIManager
        self.manager.draw()

def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, True)

    menu_view = MainMenuView()
    window.show_view(menu_view)

    # Start the arcade game loop
    arcade.run()

if __name__ == "__main__":
    main()
