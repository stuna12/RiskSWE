# pylint: disable=C0114, C0116
import math
import random
from enum import Enum
import arcade
from arcade.types import Color
from artificial_player import ArtificialPlayer
from player import Player
from country import CountryEnum
from country_button import ButtonColors, Circle, CircleButton, Outline
from gamestate import GameState, Stage

BACKGROUND_COLOR = arcade.color.ALMOND
DEFAULT_COLOR = arcade.color.COOL_GREY

# (name, color) for each player, in the order they are created
PLAYER_SETUPS = [
    ("Blue", arcade.color.BLUE),
    ("Red", arcade.color.RED),
    ("Green", arcade.color.FOREST_GREEN),
    ("Purple", arcade.color.PURPLE),
    ("Orange", arcade.color.ORANGE),
    ("Black", arcade.color.BLACK),
]

MIN_PLAYERS = 2
MAX_PLAYERS = len(PLAYER_SETUPS)

CAMERA_ZOOM = 1.5
CAMERA_SPEED = 5.0


class PlayerKind(Enum):
    """What controls a color in game."""
    HUMAN = "Human"
    AI = "AI"
    OFF = "Off"

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
    """Main game screen: draws map and passes clicks to game state"""

    def __init__(self):
        super().__init__()
        # Set background color
        self.background_color = BACKGROUND_COLOR
        self.map = None
        self.buttons: list[CircleButton] = []
        self.mouse_pos = (0, 0)
        self.action_buttons = {}
        self.state = GameState.from_file("edges.txt", True)
        self.owner: Player # The owner of the current view

        self.camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()

    def setup(self, kinds):
        with open("relpos.txt", "r", encoding="utf-8") as file:
            for (i, line) in enumerate(file.readlines()):
                rx, ry = line.split(", ")
                x = math.floor(float(rx) * self.window.width)
                y = math.floor(float(ry) * self.window.height)
                self.buttons.append(CircleButton(
                                        Circle(x, y, math.floor(self.window.width/100)),
                                        text = f"{CountryEnum.country_id_to_continent_id(i) + 1}",
                                    ))

        self.map = arcade.load_texture("./Risk_game_map.png")

        self.action_buttons = {
            "flex_button": CircleButton(
                Circle(self.window.width - 80, 80, 50),
                text = "Skip",
                action = self.flex_action,
            ),
            "roll": CircleButton(
                Circle(80, 80, 50),
                text = "Roll",
                action = self.roll,
            ),
            "quit": CircleButton(
                Circle(self.window.width - 50, self.window.height - 50, 50),
                text = "Quit Game",
                action = arcade.close_window,
                colors = ButtonColors(normal=arcade.color.DARK_RED, hover=arcade.color.RED),
            ),
        }

        self.setup_players(kinds)

    def setup_players(self, kinds):
        """Create the players chosen on main menu. Colors set to OFF are left out."""
        chosen = [(name, color, kind)
                  for (name, color), kind in zip(PLAYER_SETUPS, kinds)
                  if kind != PlayerKind.OFF]

        # Check for 2 player setup to use no wildcard rules
        self.state = GameState.from_file("edges.txt", len(chosen) == 2)

        humans = []
        for name, color, kind in chosen:
            if kind == PlayerKind.HUMAN:
                player = Player(color, name)
                humans.append(player)
            else:
                player = ArtificialPlayer(color, name)
            self.state.add_player(player)

        # Make sure owner starts as human for refresh_buttons
        self.owner = humans[0]
        self.state.start_play()

        self.refresh_buttons()

    def flex_action(self):
        if self.state.can_finish_trading(self.owner):
            self.state.finish_trading()
        elif self.state.can_skip_fortify(self.owner):
            self.state.skip_fortify()
        elif self.state.can_skip(self.owner):
            self.state.end_turn()

    def refresh_buttons(self):
        """Recolor territories by owner. Only the current player's territories react to hover."""
        assert self.state.turn.player is not None

        if not isinstance(self.state.turn.player, ArtificialPlayer):
            self.owner = self.state.turn.player

        interactible = self.state.reachable_tiles(self.owner)
        # zip pairs each territory with its button (both lists are in the same order)
        for (territory, btn) in zip(self.state.territories, self.buttons):
            btn.text = str(territory.armies)
            if territory.owner is None:
                btn.colors.normal = DEFAULT_COLOR
            else:
                btn.colors.normal = territory.owner.color
            if territory in interactible:
                btn.colors.hover = lighten(btn.colors.normal)
            else:
                btn.colors.hover = btn.colors.normal

    def update_highlights(self):
        """White ring on the selected territory, red ring on the target,
        yellow rings on clickable ones."""
        for btn in self.buttons:
            btn.outline = None
        interactible = self.state.reachable_tiles(self.owner)
        for ter in interactible:
            self.buttons[ter.type.value].outline = Outline(arcade.color.YELLOW, 2)

        if self.state.turn.selected is not None:
            self.buttons[self.state.turn.selected.type.value].outline = \
                Outline(arcade.color.WHITE, 4)

        if self.state.battle.attacked is not None:
            self.buttons[self.state.battle.attacked.type.value].outline = \
                Outline(arcade.color.RED, 4)

    def roll(self):
        """Roll max dice for both sides for attack."""

        # select dice verifies predicates
        if not self.state.select_dice(self.owner, self.state.active_dice(self.owner)):
            return
        assert self.state.battle.attacked is not None
        assert self.state.battle.attacked.owner is not None # obviously implied by above
        defender = self.state.battle.attacked.owner
        self.state.select_dice(defender, self.state.active_dice(defender))

        self.state.do_damage()

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            arcade.close_window()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """ Called whenever the mouse button is clicked. """

        if button == arcade.MOUSE_BUTTON_LEFT:
            for action_button in self.action_buttons.values():
                if action_button.on_mouse_press():
                    return

            for (i, btn) in enumerate(self.buttons):
                if btn.on_mouse_press():
                    self.state.select_territory(self.owner, i)
                    return #exit before processing all buttons

            # use same card bounds hand is drawn with
            self.owner.hand.check_hover(x, y)
            which_hovered = self.owner.hand.hovered()
            if which_hovered != -1:
                self.state.select_card(self.owner, which_hovered)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        self.mouse_pos = (x, y)
        world_x, world_y = self.camera.unproject((x, y))[:2]

        for button in self.buttons:
            button.check_hover(int(world_x), int(world_y))

        for action_button in self.action_buttons.values():
            action_button.check_hover(x, y)

        self.owner.hand.check_hover(x,y)

    def on_update(self, delta_time):
        zoom = 1.0
        x, y = self.window.width / 2, self.window.height / 2

        selected = self.state.turn.selected

        if selected is not None:
            circle = self.buttons[selected.type.value].circle
            zoom = CAMERA_ZOOM

            half_width = self.window.width / (2 * zoom)
            half_height = self.window.height / (2 * zoom)

            x = min(max(circle.x, half_width), self.window.width - half_width)
            y = min(max(circle.y, half_height), self.window.height - half_height)

        ease = min(CAMERA_SPEED * delta_time, 1.0)
        self.camera.position = (self.camera.position[0] + (x - self.camera.position[0]) * ease,
                                self.camera.position[1] + (y - self.camera.position[1]) * ease)

        self.camera.zoom += (zoom - self.camera.zoom) * ease

        self.on_mouse_motion(self.mouse_pos[0], self.mouse_pos[1], 0, 0)

    def on_draw(self):
        """ Render the screen. """
        self.clear()
        assert self.map is not None

        self.camera.use()

        arcade.draw_texture_rect(self.map,
                    arcade.LBWH(0,0,self.window.width, self.window.height))
        self.refresh_buttons()
        self.update_highlights()
        for button in self.buttons:
            button.draw()

        self.gui_camera.use()

        if self.action_buttons:
            flex_button = self.action_buttons["flex_button"]

            if self.state.can_finish_trading(self.owner):
                flex_button.text = "Finish Trading"
                flex_button.active = True
            elif self.state.can_skip_fortify(self.owner):
                flex_button.text = "Skip Fortify"
                flex_button.active = True
            elif self.state.can_skip(self.owner):
                flex_button.text = "End Turn"
                flex_button.active = True
            else:
                flex_button.text = "Skip"
                flex_button.active = False

            for action_button in self.action_buttons.values():
                action_button.draw()
        self.draw_dice()
        self.draw_turn_banner()
        self.draw_phase_banner()
        self.draw_tooltip()
        self.draw_hand()
        if self.state.winner is not None:
            self.draw_game_over()

    def draw_game_over(self):
        """Dim the map and show the winner. Quit stays on top so it can still be clicked."""
        assert self.state.winner is not None
        arcade.draw_rect_filled(
            arcade.LBWH(0, 0, self.window.width, self.window.height),
            Color(0, 0, 0, 200)
        )
        arcade.Text("GAME OVER", self.window.width / 2, self.window.height / 2 + 40,
                    arcade.color.WHITE, font_size=48, bold=True,
                    anchor_x="center", anchor_y="center").draw()
        arcade.Text(f"{self.state.winner.name} wins!",
                    self.window.width / 2, self.window.height / 2 - 30,
                    arcade.color.WHITE, font_size=28,
                    anchor_x="center", anchor_y="center").draw()
        self.action_buttons["quit"].draw()

    def draw_turn_banner(self):
        """Top-left banner showing whose turn it is."""
        player = self.state.turn.player
        if player is None:
            return
        text = (f"{player.name}'s Turn; {self.state.turn.stage.name}; "
                f"Cards: {len(player.hand.cards)}")
        label = arcade.Text(text, 0, 0, arcade.color.WHITE, font_size=18, bold=True)
        label.x = 16
        label.y = self.window.height - label.content_height - 16
        arcade.draw_rect_filled(
            arcade.LBWH(label.x - 8, label.y - 6,
                        label.content_width + 16, label.content_height + 12),
            Color(player.color[0], player.color[1], player.color[2], 255)
        )
        label.draw()

    def draw_phase_banner(self):
        """Banner under the turn banner showing the phase and remaining reinforcements."""
        stage = self.state.turn.stage
        player = self.state.turn.player
        if stage == Stage.TURN_IN_CARDS and player is not None:
            text = f"TRADE CARDS: {self.state.armies_remaining[player]} troops banked"
            bg = Color(200, 120, 0, 255)
        elif stage in (Stage.TERRITORY_REINFORCEMENT, Stage.PLACE_ARMIES) and player is not None:
            text = f"REINFORCE: {self.state.armies_remaining[player]} troops left"
            bg = Color(200, 120, 0, 255)
        elif self.state.turn.stage == Stage.GAME_OVER:
            text = "GAME OVER"
            bg = Color(60, 60, 60, 255)
        else:
            text = "ATTACK PHASE"
            bg = Color(60, 60, 60, 255)

        label = arcade.Text(text, 0, 0, arcade.color.WHITE, font_size=16, bold=True)
        label.x = 16
        label.y = self.window.height - 90
        arcade.draw_rect_filled(
            arcade.LBWH(label.x - 8, label.y - 6,
                        label.content_width + 16, label.content_height + 12),
            bg
        )
        label.draw()

    def draw_dice(self):
        """Bottom-left row of dice showing the last roll, next to the Roll button."""
        dice_color: Color = arcade.color.RED
        dice_number: int = 2
        active = self.state.active_dice(self.owner)

        if self.owner == self.state.turn.player:
            dice_color = arcade.color.WHITE
            dice_number = 3

        dice_rolls = self.state.battle.last_attacker_rolls

        size = 50

        for i in range(dice_number):
            x = 150 + i * (size + 10)
            y = 80 - size / 2
            if i < active:
                arcade.draw_rect_filled(arcade.LBWH(x, y, size, size), dice_color)
            else:
                # inactive, color grayish
                dim = (dice_color[0] // 2, dice_color[1] // 2, dice_color[2] // 2)
                arcade.draw_rect_filled(arcade.LBWH(x, y, size, size), dim)

            arcade.draw_rect_outline(arcade.LBWH(x, y, size, size), arcade.color.BLACK, 2)


            text = "X" if i >= len(dice_rolls) else str(dice_rolls[i])
            label = arcade.Text(
                                text,
                                x + size / 2, y + size / 2, arcade.color.BLACK,
                                font_size=24, anchor_x="center",
                                                            anchor_y="center"
                            )
            label.draw()


    def draw_tooltip(self):
        for (i, button) in enumerate(self.buttons):
            if button.is_hovered:
                label = arcade.Text(
                    self.state.territories[i].type.name.replace("_", " ").title(),
                    0, 0, arcade.color.WHITE, font_size=12
                )

                label.x = min(self.mouse_pos[0] - label.content_width / 2,
                              self.window.width - label.content_width - 12)
                label.y = min(self.mouse_pos[1] + 20,
                              self.window.height - label.content_height - 12)

                arcade.draw_rect_filled(
                    arcade.LBWH(label.x - 6, label.y - 10,
                                label.content_width + 12, label.content_height + 12),
                                Color(0, 0, 0, 200)
                )

                label.draw()
                return

    def draw_hand(self):

        if len(self.owner.hand.cards) == 0:
            return

        if not self.owner.hand.arranged:
            self.owner.hand.arrange_components(self.window.width, self.window.height)


        self.owner.hand.draw(self.state.selectable_cards(self.owner),
                             self.state.turn.selected_cards)

        # draw tooltips over top of the cards
        hovered = self.owner.hand.hovered()
        if hovered == -1 or hovered >= len(self.owner.hand.cards):
            return

        card = self.owner.hand.cards[hovered]

        if card.wildcard:
            label = arcade.Text(
                "Wildcard",
                0, 0, arcade.color.WHITE, font_size=12
            )
        else:
            label = arcade.Text(
                self.state.territories[card.territory].type.name
                .replace("_", " ").title() + ", " + card.army_name(),
                0, 0, arcade.color.WHITE, font_size=12
            )

        label.x = min(self.mouse_pos[0] - label.content_width / 2,
                              self.window.width - label.content_width - 12)
        label.y = min(self.mouse_pos[1] + 20,
                        self.window.height - label.content_height - 12)

        arcade.draw_rect_filled(
            arcade.LBWH(label.x - 6, label.y - 10,
                        label.content_width + 12, label.content_height + 12),
                        Color(0, 0, 0, 200)
        )

        label.draw()
