import arcade
from arcade.types import Color
import random
from human_player import HumanPlayer
from artificial_player import ArtificialPlayer
from player import Player
from country import CountryEnum
from country import Country, CountryEnum
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

# Turn phases: reinforce first, then attack
REINFORCE = "reinforce"
ATTACK = "attack"

def lighten(color, amount=60):
    """Return a brighter version of `color`, used for hover feedback."""
    return Color(min(color[0] + amount, 255),
                 min(color[1] + amount, 255),
                 min(color[2] + amount, 255), 255)

def roll_dice(count):
    """Roll `count` six-sided dice, sorted highest first (the order Risk compares them in)."""
    return sorted((random.randint(1, 6) for _ in range(count)), reverse=True)

class RiskGame(arcade.View):
    def __init__(self):
        super().__init__()
        # Set background color
        self.background_color = BACKGROUND_COLOR
        self.map = None
        self.buttons = []
        self.territories = []
        self.selected = None
        self.mouse_pos = (0, 0)
        self.players = []
        self.current_player_index = 0
        self.current_player = None
        self.end_turn_button = None
        self.roll_button = None
        self.dice = []
        self.phase = REINFORCE
        self.reinforcements_left = 0
    
    def setup(self, player_count):
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
        self.state.add_player(Player(PLAYER_SETUPS[0][1], PLAYER_SETUPS[0][0]))
        self.state.add_player(Player(PLAYER_SETUPS[1][1], PLAYER_SETUPS[1][0]))
        self.owner = self.state.players[0]
        self.state.start_play()
        
        self.refresh_buttons()

    def deal_territories(self):
        """Randomly split the territories between the players (round-robin over a shuffled list,
        so 2 players get 21 each and it extends to more players later)."""
        indices = list(range(len(self.territories)))
        random.shuffle(indices)
        for (n, i) in enumerate(indices):
            self.territories[i].owner = self.players[n % len(self.players)]
            self.territories[i].armies = random.randint(1, 5)  # TODO: replace with real placement phase

    def refresh_buttons(self):
        """Recolor every territory by owner. Only the current player's territories react to hover."""
        assert self.state.current_player is not None
        self.owner = self.state.current_player
        interactible = self.state.reachable_tiles(self.owner)
        # assert len(interactible) > 1
        # print(interactible)
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
        self.state.rolls(self.owner)

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
    
    def on_mouse_motion(self, x, y, dx, dy):
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
        self.refresh_buttons()
        self.update_highlights()
        for button in self.buttons:
            button.draw()

        if self.end_turn_button:
            self.end_turn_button.draw()
        if self.roll_button:
            self.roll_button.draw()
        self.draw_dice()
        self.draw_turn_banner()
        self.draw_phase_banner()
        self.draw_tooltip()

    def draw_turn_banner(self):
        """Top-left banner showing whose turn it is."""
        player = self.state.current_player
        if player is None:
            return
        label = arcade.Text(f"{player.name}'s Turn; {self.state.current_stage.name}", 0, 0, arcade.color.WHITE, font_size=18, bold=True)
        label.x = 16
        label.y = self.window.height - label.content_height - 16
        arcade.draw_rect_filled(
            arcade.LBWH(label.x - 8, label.y - 6, label.content_width + 16, label.content_height + 12),
            Color(player.color[0], player.color[1], player.color[2], 255)
        )
        label.draw()

    def draw_phase_banner(self):
        """Banner under the turn banner showing the phase and remaining reinforcements."""
        if self.phase == REINFORCE:
            text = f"REINFORCE: {self.reinforcements_left} troops left"
            bg = Color(200, 120, 0, 255)
        else:
            text = "ATTACK PHASE"
            bg = Color(60, 60, 60, 255)

        label = arcade.Text(text, 0, 0, arcade.color.WHITE, font_size=16, bold=True)
        label.x = 16
        label.y = self.window.height - 90
        arcade.draw_rect_filled(
            arcade.LBWH(label.x - 8, label.y - 6, label.content_width + 16, label.content_height + 12),
            bg
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
                arcade.draw_rect_filled(arcade.LBWH(x, y, size, size), (dice_color[0] // 2, dice_color[1] // 2, dice_color[2] // 2)) #inactive, color greyish
            
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
        