import arcade
import arcade.gui
from arcade.types import Color
from collections.abc import Callable
import random
from card import Card
from human_player import HumanPlayer
from artificial_player import ArtificialPlayer
from player import Player
from country import Country, CountryEnum
import math
import json

WINDOW_TITLE = "Risk"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

BACKGROUND_COLOR = arcade.color.ALMOND
TERRITORY_COUNT = 42

class CircleButton:
    """A custom circular button with text."""
    def __init__(self, center_x : int, center_y : int, radius : int, text : str, action : Callable[[],None] | None = None,
            normal_color : Color = arcade.color.ORANGE, hover_color: Color = arcade.color.ANTIQUE_RUBY, 
            inactive_color: Color = arcade.color.GRAY):
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

    def set_active(self, active : bool):
        self.active = active

    def draw(self):
        # Choose color based on hover state
        color = self.hover_color if self.is_hovered else self.normal_color
        color = color if self.active else self.inactive_color

        # Draw the circular button base
        arcade.draw_circle_filled(self.center_x, self.center_y, self.radius, color)
        
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

    def check_hover(self, mouse_x: int, mouse_y: int):
        """Check if the mouse cursor is inside the circle."""
        # Calculate distance between mouse and center of the circle
        distance = math.sqrt((mouse_x - self.center_x) ** 2 + (mouse_y - self.center_y) ** 2)
        self.is_hovered = distance <= self.radius

    def on_mouse_press(self):
        """Execute action if the button is clicked."""
        if self.is_hovered and self.action:
            self.action()
        if self.is_hovered:
            return True
        return False
        

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
            game_view.setup(3)
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


class RiskGame(arcade.View):
    def __init__(self):
        super().__init__()
        # Set background color
        self.background_color = BACKGROUND_COLOR
        self.map = None
        self.buttons: list[CircleButton] = []
        self.territories: list[Country] = []
        self.selected: int | None = None
        self.mouse_pos = (0, 0)
    
    def setup(self, player_count : int):
        with open("relpos.txt", "r", encoding="utf-8") as file:
            for (i, line) in enumerate(file.readlines()):
                rx, ry = line.split(", ")
                x = math.floor(float(rx) * self.window.width)
                y = math.floor(float(ry) * self.window.height)
                self.territories.append(Country(type=CountryEnum(i)))
                self.buttons.append(CircleButton(
                                        center_x = x,
                                        center_y = y,
                                        radius = math.floor(self.window.width/100),
                                        text = f"{CountryEnum.country_id_to_continent_id(i) + 1}",
                                    ))
                                    
        
        with open("edges.txt", "r", encoding="utf-8") as file:
            edges = json.load(file)
            for (i,adj) in enumerate(edges):
                self.territories[i].adj = adj
            
        self.map = arcade.load_texture("./Risk_game_map.png")

        # create players
        self.players: list[Player] = []

        # choose order randomly
        random.shuffle(self.players)

        if player_count == 2:
            self.two_player_setup()
            return
        
        # create & shuffle set of cards
        self.cards = Card.new_deck()
        random.shuffle(self.cards)


    def two_player_setup(self):
        self.cards = Card.new_deck(keep_wilds=False)
        random.shuffle(self.cards)

        self.players.append(HumanPlayer())
        self.players.append(ArtificialPlayer())

        hands = [self.players[i].hand for i in range(len(self.players))]
        Card.draw(hands=hands, deck=self.cards, n=14) # Alternatively draws n cards to each player's hands from the top of the deck


    def on_key_press(self, key, modifiers):
        if key == arcade.key.A:
            data: list[list[int]] = []
            for territory in self.territories:
                data.append(list(set(territory.adj)))
            with open("edges.txt", "w", encoding="utf-8") as file:
                json.dump(data, file)
            with open("edges.txt", "r", encoding="utf-8") as file:
                        edges = json.load(file)
                        for (i,adj) in enumerate(edges):
                            self.territories[i].adj = adj
        
        if key == arcade.key.ESCAPE:
            arcade.close_window()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers):
        """ Called whenever the mouse button is clicked. """
        
        if button == arcade.MOUSE_BUTTON_LEFT:
            for (i, btn) in enumerate(self.buttons):
                if btn.on_mouse_press():
                    if self.selected == i:
                        self.selected = None
                        for btn in self.buttons:
                            btn.set_active(True)
                    else:
                        self.selected = i
                        adj = self.territories[i].adj
                        for (j, btn) in enumerate(self.buttons):
                            if j == i or (j in adj):
                                btn.set_active(True)
                            else:
                                btn.set_active(False)
                    return #exit before processing all buttons
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            for (i, btn) in enumerate(self.buttons):
                if btn.on_mouse_press():
                    print("doing things")
                    if self.selected != i:
                        self.territories[self.selected].adj.append(i)
                        self.territories[i].adj.append(self.selected)
                    else:
                        self.selected = i
                        adj = self.territories[i].adj
                        for (j, btn) in enumerate(self.buttons):
                            if j == i or (j in adj):
                                btn.set_active(True)
                            else:
                                btn.set_active(False)
                    return #exit before processing all buttons
        # if button == arcade.MOUSE_BUTTON_LEFT:
        #     for (i, btn) in enumerate(self.buttons):
        #         if btn.on_mouse_press():
        #             self.last_lclicked = i
        # elif button == arcade.MOUSE_BUTTON_RIGHT:
        #     for (i, btn) in enumerate(self.buttons):
        #         if btn.on_mouse_press():
        #             if i == self.last_lclicked:
        #                 return
        #             self.territories[self.last_lclicked].adj.append(i)
        #             self.territories[i].adj.append(self.last_lclicked)

        # with open("relpos.txt", "a", encoding="utf-8") as file:
        #     rx = x / self.window.width
        #     ry = y / self.window.height
        #     print(rx, ", ", ry)
        #     file.write(f"{rx:.16f}, {ry:.16f}\n")

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons, modifiers):
        """ Called whenever the mouse is clicked and dragged 
            `x` and `y` are current position, `dx` and `dy` are distance from last mouse event """
        pass
    
    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        self.mouse_pos = (x, y)
        for button in self.buttons:
            button.check_hover(x, y)

    def on_mouse_release(self, x: int, y: int, button, modifiers):
        """ Called whenever a button is released """
        pass

    def on_update(self, delta_time: float):
        # Move the rectangle
        pass

    def on_draw_before_ui(self):
        pass

    def on_draw_after_ui(self):
        # Add draw commands that should be on top of the UI (uncommon)
        pass

    def on_draw(self):
        """ Render the screen. """
        self.clear()
        arcade.draw_texture_rect(self.map, 
                    arcade.LBWH(0,0,self.window.width, self.window.height))
        for button in self.buttons:
            button.draw()

        self.draw_tooltip()

        # Clear screen
        
        # Draw all items & update text here:


    def draw_tooltip(self):
        for (i, button) in enumerate(self.buttons):
            if button.is_hovered:
                label = arcade.Text(
                    self.territories[i].type.name.replace("_", " ").title(),
                    0, 0, arcade.color.WHITE, font_size=12
                )

                label.x = min(self.mouse_pos[0] - label.content_width / 2, self.window.width - label.content_width - 12)
                label.y = min(self.mouse_pos[1] + 20, self.window.height - label.content_height - 12)

                arcade.draw_rect_filled(
                    arcade.LBWH(label.x - 6, label.y - 10,
                                label.content_width + 12, label.content_height + 12),
                                Color(0, 0, 0, 200)
                )

                label.draw()
                return
        

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