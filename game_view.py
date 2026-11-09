# pylint: disable=C0114, C0116
import math
import random
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

    def setup(self, player_count: int):
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
            "end_turn": CircleButton(
                Circle(self.window.width - 80, 80, 50),
                text = "End Turn",
                action = self.state.end_turn,
            ),
            "skip_fortify": CircleButton(
                Circle(self.window.width - 200, 80, 50),
                text = "Skip Fortify",
                action = self.state.skip_fortify,
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

        # create & shuffle set of cards

        if player_count == 2:
            self.two_player_setup()
        else:
            raise NotImplementedError("Only the 2-player setup is implemented so far")


    def two_player_setup(self):
        # Both players are human for now, swap one for ArtificialPlayer later
        # start_play shuffles the turn order and deals the territories randomly
        self.state.add_player(Player(PLAYER_SETUPS[0][1], PLAYER_SETUPS[0][0]))
        self.state.add_player(ArtificialPlayer(PLAYER_SETUPS[1][1], PLAYER_SETUPS[1][0]))
        self.owner = self.state.players[0]
        self.state.start_play()

        self.refresh_buttons()


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

            height = self.window.height / 10
            low = self.window.width * 2 / 5
            which_hovered = int((self.mouse_pos[0] - low) //
                                (self.window.width / 5 / len(self.owner.hand.cards)))
            if self.mouse_pos[1] > self.window.height/15 + height / 2:
                which_hovered = -1

            self.state.select_card(self.owner, which_hovered)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        self.mouse_pos = (x, y)
        for button in self.buttons:
            button.check_hover(x, y)
        for action_button in self.action_buttons.values():
            action_button.check_hover(x, y)

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

        if self.action_buttons:
            self.action_buttons["end_turn"].active = self.state.can_skip(self.owner)
            self.action_buttons["skip_fortify"].active = self.state.can_skip_fortify(self.owner)
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
        if self.state.turn.stage == Stage.TERRITORY_REINFORCEMENT:
            text = f"REINFORCE: {self.state.armies_remaining[self.owner]} troops left"
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
        #draw the hand in the middle 5th of the screen

        width = self.window.width / 20
        height = self.window.height / 10

        low = self.window.width * 2 / 5
        delta = self.window.width / 5 / (len(self.owner.hand.cards) + 1)

        which_hovered = int((self.mouse_pos[0] - low) //
                            (self.window.width / 5 / len(self.owner.hand.cards)))
        selectable = self.state.selectable_cards(self.owner)

        if self.mouse_pos[1] > self.window.height/15 + height / 2:
            which_hovered = -1
        for i, card in enumerate(self.owner.hand.cards):
            if self.owner == self.state.turn.player and (
                    i in self.state.turn.selected_cards or which_hovered == i):
                bb = arcade.XYWH(low + delta * (i + 1), self.window.height/15,
                            width, height)
                arcade.draw_rect_filled(bb, Color(255, 255, 255))
            else:
                # print(self.state.selectable_cards(self.owner))
                bb = arcade.XYWH(low + delta * (i + 1), self.window.height/20,
                            width, height)
                if i in selectable:
                    arcade.draw_rect_filled(bb, Color(255, 255, 255))
                else:
                    arcade.draw_rect_filled(bb, Color(150, 150, 150))
            arcade.draw_rect_outline(bb, Color(0, 0, 0))


        # draw tooltips over top of the cards
        for i, card in enumerate(self.owner.hand.cards):
            if which_hovered == i:
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