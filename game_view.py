import arcade
from arcade.types import Color
import random
from card import Card
from human_player import HumanPlayer
from artificial_player import ArtificialPlayer
from country import Country, CountryEnum
import math
import json
from CountryButton import CircleButton


BACKGROUND_COLOR = arcade.color.ALMOND


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

        self.end_turn_button = CircleButton(
            center_x = self.window.width - 80,
            center_y = 80,
            radius = 50,
            text = "End Turn",
            action = self.end_turn,
        )

        self.roll_button = CircleButton(
            center_x = 80,
            center_y = 80,
            radius = 50,
            text = "Roll",
            action = self.roll,
        )

        # create & shuffle set of cards
        self.cards = Card.new_deck(keep_wilds=(player_count != 2))
        random.shuffle(self.cards)

        if player_count == 2:
            self.two_player_setup()
        else:
            raise NotImplementedError("Only the 2-player setup is implemented so far")


    def two_player_setup(self):
        # Both players are human for now, swap one for ArtificialPlayer later
        self.players = [HumanPlayer(color, name) for (name, color) in PLAYER_SETUPS]
        random.shuffle(self.players)  # Random turn order
        self.current_player_index = 0
        self.current_player = self.players[self.current_player_index]

        self.deal_territories()
        self.refresh_buttons()
        self.start_turn()

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

        # zip pairs each territory with its button (both lists are in the same order)
        for (territory, btn) in zip(self.territories, self.buttons):
            btn.text = str(territory.armies)
            btn.normal_color = territory.owner.color
            if territory.owner is self.current_player:
                btn.hover_color = lighten(territory.owner.color)
            else:
                btn.hover_color = territory.owner.color

    def update_highlights(self):
        """White ring on the selected territory, yellow rings on its neighbors."""
        for btn in self.buttons:
            btn.outline = None
        if self.selected is None:
            return
        for j in self.territories[self.selected].adj:
            self.buttons[j].outline = arcade.color.YELLOW
            self.buttons[j].outline_width = 2
        self.buttons[self.selected].outline = arcade.color.WHITE
        self.buttons[self.selected].outline_width = 4

    def attack(self, src_i, dst_i):
        """Simple attack for now: higher troop count wins and takes the territory."""
        src = self.territories[src_i]
        dst = self.territories[dst_i]

        # Need at least 2 troops to attack (1 must stay behind), and strictly more than the defender
        if src.armies < 2 or src.armies <= dst.armies:
            return

        dst.owner = src.owner
        dst.armies = src.armies - 1   # Everything but one troop moves in
        src.armies = 1                # One troop stays behind

        self.selected = None
        self.update_highlights()
        self.refresh_buttons()
        self.check_winner()

    def check_winner(self):
        if all(t.owner is self.current_player for t in self.territories):
            print(f"{self.current_player.name} wins!")  # TODO: real win screen

    def start_turn(self):
        """Begin a turn: hand the current player their reinforcements and lock attacking."""
        self.selected = None
        self.update_highlights()
        self.reinforcements_left = self.current_player.available_troops(self.territories)
        self.set_phase(REINFORCE if self.reinforcements_left > 0 else ATTACK)

    def set_phase(self, phase):
        self.phase = phase
        # Attack phase buttons are greyed out and ignore clicks during reinforcement
        in_attack = (phase == ATTACK)
        self.end_turn_button.set_active(in_attack)
        self.roll_button.set_active(in_attack)

    def reinforce(self, i):
        """Place one troop on territory i (must be owned by the current player)."""
        if self.phase != REINFORCE or self.reinforcements_left <= 0:
            return
        self.territories[i].armies += 1
        self.reinforcements_left -= 1
        self.refresh_buttons()
        if self.reinforcements_left == 0:
            self.set_phase(ATTACK)

    def end_turn(self):
        if self.phase != ATTACK:
            return
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.current_player = self.players[self.current_player_index]
        self.refresh_buttons()
        self.start_turn()


    def roll(self):
        """Not hooked into attacking yet, just rolls 3 dice for display."""
        self.dice = roll_dice(3)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            arcade.close_window()

    def on_mouse_press(self, x, y, button, modifiers):
        """ Called whenever the mouse button is clicked. """
        
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.end_turn_button and self.end_turn_button.on_mouse_press():
                return
            if self.roll_button and self.roll_button.on_mouse_press():
                return

            for (i, btn) in enumerate(self.buttons):
                if btn.on_mouse_press():
                    owned = self.territories[i].owner is self.current_player
                    if self.phase == REINFORCE:
                        # Only reinforcing is allowed: click your own territory to add a troop
                        if owned:
                            self.reinforce(i)
                    elif owned:
                        # Own territory: select / deselect
                        self.selected = None if self.selected == i else i
                        self.update_highlights()
                    elif self.selected is not None and i in self.territories[self.selected].adj:
                        # Enemy neighbor of the selected territory: attack it
                        self.attack(self.selected, i)
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

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
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

    def on_mouse_release(self, x, y, button, modifiers):
        """ Called whenever a button is released """
        pass

    def on_update(self, delta_time):
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

        if self.end_turn_button:
            self.end_turn_button.draw()
        if self.roll_button:
            self.roll_button.draw()
        self.draw_dice()
        self.draw_turn_banner()
        self.draw_phase_banner()
        self.draw_tooltip()

        # Clear screen
        
        # Draw all items & update text here:


    def draw_turn_banner(self):
        """Top-left banner showing whose turn it is."""
        player = self.current_player
        label = arcade.Text(f"{player.name}'s Turn", 0, 0, arcade.color.WHITE, font_size=18, bold=True)
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
        size = 50
        for (n, value) in enumerate(self.dice):
            x = 150 + n * (size + 10)
            y = 80 - size / 2
            arcade.draw_rect_filled(arcade.LBWH(x, y, size, size), arcade.color.WHITE)
            arcade.draw_rect_outline(arcade.LBWH(x, y, size, size), arcade.color.BLACK, 2)
            arcade.draw_text(
                str(value),
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
        