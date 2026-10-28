import arcade
import arcade.gui
from game_view import RiskGame

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
        
    def on_show_view(self):
        """Called when this view becomes active."""
        # Enable the UIManager to capture mouse events/clicks
        self.manager.enable()
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
        
        # Create a styled "Start Game" button
        start_button = arcade.gui.UIFlatButton(text="Start Game", width=200)
        v_box.add(start_button)
        
        # Assign an action handler to the button's click event
        @start_button.event("on_click")
        def on_click_start(event):
            # Instantiate the game view, set it up, and switch to it
            game_view = RiskGame()
            game_view.setup(2)
            self.window.show_view(game_view)

        # Center the v_box within the anchor layout
        anchor_layout.add(v_box, anchor_x="center", anchor_y="center")
        
        # Add our layout to the UIManager
        self.manager.add(anchor_layout)

    def on_hide_view(self):
        """Called when switching away from this view."""
        # Clean up and disable the manager so it stops processing inputs
        self.manager.disable()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
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