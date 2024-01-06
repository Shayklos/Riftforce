from __future__ import annotations
import discord
from discord.enums import ButtonStyle
from discord.emoji import Emoji
from discord.interactions import Interaction
from discord.partial_emoji import PartialEmoji

from copy import deepcopy, copy

from RiftforceView import RiftforceView
from typing import TYPE_CHECKING, Any, Optional, Union
if TYPE_CHECKING:
    from Main import MainView
    from Card import Card
    from Activate import *

FACTIONS_THAT_MOVE = ('Water', 'Plant', 'Beast', 'Magnet', 'Sound',
                      'Air', 'Shadow', 'Sand')

FACTIONS_THAT_MOVE_ADJACENT = ('Water', 'Plant', 'Beast', 'Magnet', 'Sound')
FACTIONS_THAT_MOVE_ANYWHERE = ('Air', 'Shadow', 'Sand')
FACTIONS_WITH_NO_CUSTOM_EFFECT = ('Crystal', 'Earth', 'Fire', 'Ice', 'Lava', 'Acid', 'Star')



class MoveButton(discord.ui.Button):
    def __init__(self, card, style: ButtonStyle = ButtonStyle.secondary, label: str | None = None, disabled: bool = False, custom_id: str | None = None, url: str | None = None, emoji: str | Emoji | PartialEmoji | None = None, row: int | None = None):
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
        self.card = card
    async def callback(self, interaction: discord.Interaction):
        self.view: View

        self.view.add_parameter(int(self.label[-1]) - 1)
        await self.view.go_next_card(interaction)


class ThunderboltButton(discord.ui.Button):
    def __init__(self, card: Card, style: ButtonStyle = ButtonStyle.primary, disabled: bool = False, custom_id: str | None = None, url: str | None = None, emoji: str | Emoji | PartialEmoji | None = None, row: int | None = None):
        super().__init__(style=style, label=f"{card.position+1}. {card}", disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
        self.card = card

    async def callback(self, interaction: discord.Interaction):
        self.view: View
        
        if not self.view.thunderbolt_kill and self.card.health_left <= 2: #Thunderbolt kills and repeats action once
            #TODO thunderbolt when there is one card in column
            if len(self.view.children) == 1: #Thunderbolt has killed but there is only one card in the column
                self.view.add_parameter([0,None])
                await self.view.go_next_card(interaction)
                return 
            
            self.style = ButtonStyle.green
            self.disabled = True
            self.view.thunderbolt_kill.append(self.card.position)
            await interaction.response.edit_message(view = self.view)
            return

        self.view.thunderbolt_kill.append(self.card.position)

        if len(self.view.thunderbolt_kill) == 1: self.view.thunderbolt_kill.append(None) #Thunderbolt hasn't killed and thus doesnt activate twice


        self.view.add_parameter(self.view.thunderbolt_kill)
        await self.view.go_next_card(interaction)

class ThunderboltEmptyButton(discord.ui.Button):
    async def callback(self, interaction: discord.Interaction):
        self.view: View
        self.view.add_parameter([None,None])
        await self.view.go_next_card(interaction)


class LightButton(discord.ui.Button):
    def __init__(self, card: Card | None = None, style: ButtonStyle = ButtonStyle.secondary, label: str | None = None, disabled: bool = False, custom_id: str | None = None, url: str | None = None, emoji: str | Emoji | PartialEmoji | None = None, row: int | None = None):
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
        self.view : View
        self.card = card
        self.style = ButtonStyle.blurple if not self.disabled else ButtonStyle.grey

    async def callback(self, interaction: discord.Interaction):
        self.view.add_parameter((self.card.column, self.card.position))
        await self.view.go_next_card(interaction)

class LightColumnButton(discord.ui.Button):
    def __init__(self, column, *, disabled: bool = False, custom_id: str | None = None, url: str | None = None, emoji: str | Emoji | PartialEmoji | None = None, row: int | None = None):
        super().__init__(style=discord.ButtonStyle.primary, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
        self.column = column
        self.label = f'Column {column + 1}'
    
    async def callback(self, interaction: discord.Interaction):
        self.view: View
        
        self.view.clear_items()
        player = self.view.game.player1 if self.view.game.isPlayer1Turn else self.view.game.player2
        for card in player.columns[self.column]:
            self.view.add_item(LightButton(card, label = f"{card.position + 1}. {card}"))
        
        await interaction.response.edit_message(view=self.view)



class View(RiftforceView):
    def __init__(self, underlying_view: SimpleView, timeout: float | None = 180):
        super().__init__(bot=underlying_view.bot, timeout=underlying_view.timeout)
        self.underlying_view = underlying_view
        self.cards: list[Card] = self.underlying_view.cards_with_effects #aire, sombra
        self.n_cards = len(self.cards) # 2
        self.n_activated_cards = 0

        self.initial_content = self.content()

        self.game = deepcopy(self.underlying_view.playView.game)
        self.simulation_index = 0
        self.simulate()
        
        self.add_butons()
        

    def add_butons(self):
        card = self.cards[self.n_activated_cards]

        if card.faction in FACTIONS_THAT_MOVE: self.add_buttons_moving_card(card)
        elif card.faction == 'Thunderbolt' : self.add_buttons_thunderbolt(card) 
        elif card.faction == 'Light' : self.add_buttons_light() 
        elif card.faction == 'Love' : pass #TODO
            
  
    def add_buttons_moving_card(self, card: Card):
        if card.faction in FACTIONS_THAT_MOVE_ADJACENT:
            allowed = (card.column + 1, card.column - 1) #TODO if len(this) is 1 this can be skipped since there is only one option
        elif card.faction in FACTIONS_THAT_MOVE_ANYWHERE:
            allowed = [0,1,2,3,4]
            allowed.remove(card.column)
        
        for i in (0,1,2,3,4):
            self.add_item(MoveButton(card = card, label = f'Column {i + 1}', disabled= i not in allowed, style=ButtonStyle.primary))
    
    def add_buttons_thunderbolt(self, card: Card):
        self.thunderbolt_kill = []
        # game = self.underlying_view.playView.game
        game = self.game
        column = game.player2.columns[card.column] if game.isPlayer1Turn else game.player1.columns[card.column]

        assert len(column) <= 25, "Discord limitations only allows me to place 25 buttons" #TODO pages

        if not column:
            self.add_item(ThunderboltEmptyButton(label = 'None'))
            return

        for card in column:
            self.add_item(ThunderboltButton(card))

    def add_buttons_light(self):
        player = self.game.player1 if self.game.isPlayer1Turn else self.game.player2
        max_column_len = max([len(column) for column in player.columns])

        if max_column_len < 6:
            for column in player.columns: 
                for i in range(max_column_len):
                    if len(column) > i: self.add_item(LightButton(row = i, label = str(column[i]), card = column[i]))
                    else:               self.add_item(LightButton(row = i, label = '----', disabled=True))
        
        else:
            for i, column in enumerate(player.columns):
                self.add_item(LightColumnButton(i))
        
    async def go_next_card(self, interaction : discord.Interaction, log = None):
        if self.n_activated_cards == self.n_cards:
            game = self.underlying_view.playView.game #Do it with real game
            player = game.player1 if game.isPlayer1Turn else game.player2
            
            self.underlying_view.playView.activate_log(player, self.underlying_view.reference_card, self.underlying_view.selected_cards, self.underlying_view.card_parameters)
            player.activate_and_discard(self.underlying_view.reference_card, self.underlying_view.selected_cards, self.underlying_view.card_parameters)
            game.change_turn()
            await interaction.response.edit_message(content = "Done!", view = None)
            await self.underlying_view.playView.update_board()
            return 
        
        self.clear_items()
        self.add_butons()
        #log
        await interaction.response.edit_message(content = self.content(), view = self)

    def add_parameter(self, param):
        index = self.underlying_view.selected_cards.index(self.cards[self.n_activated_cards])
        
        #Play in the simulated game
        player = self.game.player1 if self.game.isPlayer1Turn else self.game.player2
        column = self.underlying_view.selected_cards[self.simulation_index].column
        position = self.underlying_view.selected_cards[self.simulation_index].position

        print()
        card = player.columns[column][position]
        player.activate(card, param)

        if self.n_activated_cards != self.n_cards:
            self.simulation_index += 1
            self.simulate()

        self.underlying_view.card_parameters[index] = param
        self.n_activated_cards += 1

    def simulate(self):
        print(f"Simulated game ----------\n {self.game}\n----------")
        #has no effect: true, false, false
        if self.simulation_index >= 3: return
        if not self.underlying_view.has_no_effect[self.simulation_index]: return
   
        #If card has no effect
        player = self.game.player1 if self.game.isPlayer1Turn else self.game.player2
        print(player.username)
        column = self.underlying_view.selected_cards[self.simulation_index].column
        position = self.underlying_view.selected_cards[self.simulation_index].position

        print('column', column, 'position', position)
        card = player.columns[column][position]

        player.activate(card)
        
        self.simulation_index += 1
        self.simulate()

    def content(self):
        faction = self.cards[self.n_activated_cards].faction
        match faction:
            case 'Water': return "To which column will this Water move?"
            case 'Beast': return "To which column will this Beast move?"
            case 'Magnet': return "To which column will this Magnet move?"
            case 'Air': return "To which column will this Air move?"
            case 'Shadow': return "To which column will this Shadow move?"
            case 'Sand': return "To which column will this Sand move?"
            case 'Sound': return "To which column will this Sound steal?"
            case 'Plant': return "To witch column will this Plant attack?"
            case 'Light': return "Which elemental will this Light heal?"
            case 'Thunderbolt': return "Which elemental will this Thunderbolt hit?"
            case 'Love': return "Which elemental will this Love heal?"