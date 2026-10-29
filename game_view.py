import arcade
from arcade.types import Color
import random
from human_player import HumanPlayer
from artificial_player import ArtificialPlayer
from player import Player
from country import CountryEnum
import math

from CountryButton import CircleButton
from gamestate import GameState


BACKGROUND_COLOR = arcade.color.ALMOND
DEFAULT_COLOR = arcade.color.COOL_GREY

# (name, color) for each player, in the order they are created
PLAYER_SETUPS = [
    ("Blue", arcade.color.BLUE),
    ("Red", arcade.color.RED),
]

def lighten(color: Color, amount: int = 60) -> Color:
    """Return a brighter version of `color`, used for hover feedback."""
    return Color(min(color[0] + amount, 255),
                 min(color[1] + amount, 255),
                 min(color[2] + amount, 255), 255)

def roll_dice(count: int) -> list[int]:
    """Roll `count` six-sided dice, sorted highest first (the order Risk compares them in)."""
    return sorted((random.randint(1, 6) for _ in range(count)), reverse=True)

class RiskGame(arcade.View):
    def __init__(self):
        super().__init__()
        # Set background color
        self.background_color = BACKGROUND_COLOR
        self.map = None
        self.buttons: list[CircleButton] = []
        self.mouse_pos = (0, 0)
        self.end_turn_button: CircleButton | None = None
        self.roll_button: CircleButton | None = None
        self.state: GameState = GameState.from_file("edges.txt")
        self.owner: Player # The owner of the current view
    
    def setup(self, player_count : int):
        with open("relpos.txt", "r", encoding="utf-8") as file:
            for (i, line) in enumerate(file.readlines()):
                rx, ry = line.split(", ")
                x = math.floor(float(rx) * self.window.width)
                y = math.floor(float(ry) * self.window.height)
                self.buttons.append(CircleButton(
                                        center_x = x,
                                        center_y = y,
                                        radius = math.floor(self.window.width/100),
                                        text = f"{CountryEnum.country_id_to_continent_id(i) + 1}",
                                    ))
                                                
        self.map = arcade.load_texture("./Risk_game_map.png")

        self.end_turn_button = CircleButton(
            center_x = self.window.width - 80,
            center_y = 80,
            radius = 50,
            text = "End Turn",
            action = self.state.end_turn,
        )

        self.roll_button = CircleButton(
            center_x = 80,
            center_y = 80,
            radius = 50,
            text = "Roll",
            action = self.roll,
        )

        # create & shuffle set of cards

        if player_count == 2:
            self.two_player_setup()
        else:
            raise NotImplementedError("Only the 2-player setup is implemented so far")


    def two_player_setup(self):
        # Both players are human for now, swap one for ArtificialPlayer later
         # Random turn order
        self.owner = self.state.players[0]

        self.refresh_buttons()

    def refresh_buttons(self):
        """Recolor every territory by owner. Only the current player's territories react to hover."""

        interactible = self.state.reachable_tiles(self.owner)

        # zip pairs each territory with its button (both lists are in the same order)
        for (territory, btn) in zip(self.state.territories, self.buttons):
            btn.text = str(territory.armies)
            if territory.owner is None:
                btn.normal_color = DEFAULT_COLOR
            else:
                btn.normal_color = territory.owner.color
            if territory in interactible:
                btn.hover_color = lighten(btn.normal_color)
            else:
                btn.hover_color = btn.normal_color

    def update_highlights(self):
        """White ring on the selected territory, yellow rings on its neighbors."""
        for btn in self.buttons:
            btn.outline = None
        interactible = self.state.reachable_tiles(self.owner)
        for ter in interactible:
            self.buttons[ter.type.value].outline = arcade.color.YELLOW
            self.buttons[ter.type.value].outline_width = 2
        
        if self.state.selected is not None:
            self.buttons[self.state.selected.type.value].outline = arcade.color.WHITE
            self.buttons[self.state.selected.type.value].outline_width = 4



    def roll(self):
        """Not hooked into attacking yet, just rolls 3 dice for display."""
        self.dice = roll_dice(3)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            arcade.close_window()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """ Called whenever the mouse button is clicked. """
        
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.end_turn_button and self.end_turn_button.on_mouse_press():
                return
            if self.roll_button and self.roll_button.on_mouse_press():
                return

            for (i, btn) in enumerate(self.buttons):
                if btn.on_mouse_press():
                    self.state.select_territory(self.owner, i)
                    return #exit before processing all buttons

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        """ Called whenever the mouse is clicked and dragged 
            `x` and `y` are current position, `dx` and `dy` are distance from last mouse event """
        pass
    
    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        self.mouse_pos = (x, y)
        for button in self.buttons:
            button.check_hover(x, y)
        if self.end_turn_button:
            self.end_turn_button.check_hover(x, y)
        if self.roll_button:
            self.roll_button.check_hover(x, y)

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        """ Called whenever a button is released """
        pass

    def on_update(self, delta_time: float):
        pass

    def on_draw(self):
        """ Render the screen. """
        self.clear()
        assert self.map is not None 
        arcade.draw_texture_rect(self.map, 
                    arcade.LBWH(0,0,self.window.width, self.window.height))
        for button in self.buttons:
            button.draw()

        if self.end_turn_button:
            self.end_turn_button.draw()
        if self.roll_button:
            self.roll_button.draw()
        self.draw_dice()
        self.draw_turn_banner()
        self.draw_tooltip()

    def draw_turn_banner(self):
        """Top-left banner showing whose turn it is."""
        player = self.state.current_player
        label = arcade.Text(f"{player.name}'s Turn", 0, 0, arcade.color.WHITE, font_size=18, bold=True)
        label.x = 16
        label.y = self.window.height - label.content_height - 16
        arcade.draw_rect_filled(
            arcade.LBWH(label.x - 8, label.y - 6, label.content_width + 16, label.content_height + 12),
            Color(player.color[0], player.color[1], player.color[2], 255)
        )
        label.draw()

    def draw_dice(self):
        """Bottom-left row of dice showing the last roll, next to the Roll button."""
        dice_color: Color = arcade.color.RED
        dice_number: int = 2
        active = self.state.active_dice(self.owner)

        if self.owner == self.state.current_player:
            dice_color = arcade.color.WHITE
            dice_number = 3

        dice_rolls = self.state.rolls(self.owner)
        
        size = 50
        
        for i in range(dice_number):
            x = 150 + i * (size + 10)
            y = 80 - size / 2
            if i < active:
                arcade.draw_rect_filled(arcade.LBWH(x, y, size, size), dice_color)
            else:
                arcade.draw_rect_filled(arcade.LBWH(x, y, size, size), (dice_color[1] // 2, dice_color[2] // 2, dice_color[3] // 2)) #inactive, color greyish
            
            arcade.draw_rect_outline(arcade.LBWH(x, y, size, size), arcade.color.BLACK, 2)


            text = "X" if i >= len(dice_rolls) else str(dice_rolls[i])
            arcade.draw_text(
                            text,
                            x + size / 2,
                            y + size / 2,
                            arcade.color.BLACK,
                            font_size=24,
                            anchor_x="center",
                            anchor_y="center"
                        )

    def draw_tooltip(self):
        for (i, button) in enumerate(self.buttons):
            if button.is_hovered:
                label = arcade.Text(
                    self.state.territories[i].type.name.replace("_", " ").title(),
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
        