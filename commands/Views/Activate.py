from __future__ import annotations
import discord
from discord.enums import ButtonStyle
from discord.emoji import Emoji
from discord.partial_emoji import PartialEmoji


from RiftforceView import RiftforceView
from typing import TYPE_CHECKING, Optional, Union
import EffectView
if TYPE_CHECKING:
    from Main import *
from image_manipulation import *

class CardSelectConfirm(discord.ui.Button):
    def __init__(self, *, style: ButtonStyle = ButtonStyle.secondary, label: str | None = None, disabled: bool = False, custom_id: str | None = None, url: str | None = None, emoji: str | Emoji | PartialEmoji | None = None, row: int | None = None):
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
        self.card = None 

    async def callback(self, interaction: discord.Interaction):
        self.view : CardSelectView

        max_column_len = max([len(column) for column in self.view.player.columns])
        print("Going SimpleView") if max_column_len < 5 else print("GoingComplexView")

        if max_column_len < 5:
            await interaction.response.edit_message(
                content= f"You're discarding {self.view.selected_cards[0]}. Which cards are you activating?", 
                view=SimpleView(self)) #when there is at most 4 cards in a column
        else:
            await interaction.response.edit_message(
                content= f"You're discarding {self.view.selected_cards[0]}. Which cards are you activating?", 
                view=ComplexView(self)) #when there is at most 4 cards in a column
        
class CardSelectCancel(discord.ui.Button):
    def __init__(self, *, style: ButtonStyle = ButtonStyle.secondary, label: str | None = None, disabled: bool = False, custom_id: str | None = None, url: str | None = None, emoji: str | Emoji | PartialEmoji | None = None, row: int | None = None):
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
        self.card = None 

    async def callback(self, interaction: discord.Interaction):
        self.view: CardSelectView
        for item in self.view.children:
            item.disabled = False if item.label != 'Confirm' else True
            if item.card : item.style = discord.ButtonStyle.blurple
        self.view.selected_cards = []
        await interaction.response.edit_message(view=self.view)

class CardSelectButton(discord.ui.Button):
    def __init__(self, card, *, style: ButtonStyle = ButtonStyle.secondary, label: str | None = None, disabled: bool = False, custom_id: str | None = None, url: str | None = None, emoji: str | Emoji | PartialEmoji | None = None, row: int | None = None):
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
        self.card = card

    async def callback(self, interaction: discord.Interaction):
        self.view : CardSelectView
        self.style = discord.ButtonStyle.green
        self.view.selected_cards.append(self.card)
        for item in self.view.children:
            if item.card: item.disabled = True
            else: item.disabled = False
        await interaction.response.edit_message(view=self.view)

class CardSelectView(RiftforceView):
    def __init__(self, button: ActivateButton, player):
        super().__init__(bot=button.view.bot, timeout=button.view.timeout)
        self.player: Player = player
        self.selected_cards = []
        self.playView = button.view

        self.add_item(CardSelectConfirm(style = discord.ButtonStyle.green,
                                        label = 'Confirm',
                                        row = 4,
                                        disabled = True))
        self.add_item(CardSelectCancel(style = discord.ButtonStyle.red,
                                        label = 'Cancel selection',
                                        row = 4))
        
        row = 0
        counter = 0
        for card in self.player.hand:
            self.add_item(
                CardSelectButton(card,
                                 style=discord.ButtonStyle.blurple, 
                                 row = row,
                                 label = str(card))
            )
            counter += 1
            if counter > 3: 
                row+=1
                counter = 0


class SimpleButton(discord.ui.Button):
    def __init__(self, card: Card | None = None, style: ButtonStyle = ButtonStyle.secondary, label: str | None = None, disabled: bool = False, custom_id: str | None = None, url: str | None = None, emoji: str | Emoji | PartialEmoji | None = None, row: int | None = None):
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
        self.view : SimpleView
        self.card = card
        self.style = ButtonStyle.blurple if not self.disabled else ButtonStyle.grey

    async def callback(self, interaction: discord.Interaction):
        self.style = ButtonStyle.green
        self.disabled = True 

        self.view.selected_cards.append( self.card )
        for item in self.view.children:
            if item.label not in ['Confirm', 'Cancel selection', '----'] and not self.view.compatible(item.card):
                item.style = ButtonStyle.grey
                item.disabled = True
            elif len(self.view.selected_cards) and item.label == 'Confirm':
                item.disabled = False

        await interaction.response.edit_message(view = self.view)

class SimpleView(RiftforceView):
    def __init__(self, button: CardSelectConfirm):
        super().__init__(bot=button.view.bot, timeout=button.view.timeout)
        self.player: Player = button.view.player
        self.reference_card: Card = button.view.selected_cards[0]
        self.playView: MainView = button.view.playView
        self.selected_cards: list[Card] = []
        self.generate_buttons()

    def compatible(self, proposed_card):
        #Check what reference_card and selected_cards have in common
        if proposed_card in self.selected_cards: return True
        if len(self.selected_cards) >= 3: return False

        cards: list[Card] = self.selected_cards.copy()
        cards.append(self.reference_card)
        cards.append(proposed_card)

        if len({card.health for card in cards}) == 1:   return True
        if len({card.faction for card in cards}) == 1:  return True
        return False        

    def generate_buttons(self):
        max_column_len = max([len(column) for column in self.player.columns])
        print("Requisite achieved:", max_column_len - 1 < 5)
        for column in self.player.columns: 
            for i in range(max_column_len):
                if len(column) > i: self.add_item(SimpleButton(row = i, label = str(column[i]), card = column[i], 
                                        disabled= not (self.reference_card.faction == column[i].faction or self.reference_card.health == column[i].health)))
                else:               self.add_item(SimpleButton(row = i, label = '----', disabled=True))
        
    @discord.ui.button(label = "Confirm", row = 4, style=discord.ButtonStyle.green, disabled=True) 
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.card_parameters = [None] * len(self.selected_cards)
        self.has_no_effect = [card.faction in EffectView.FACTIONS_WITH_NO_CUSTOM_EFFECT for card in self.selected_cards]
        if all(self.has_no_effect): #activate cards, no entering view
            game = self.playView.game
            player = game.player1 if game.isPlayer1Turn else game.player2
            player.activate_and_discard(self.reference_card, self.selected_cards, self.card_parameters)
            # game.isPlayer1Turn = not game.isPlayer1Turn # UNCOMMENT
            await interaction.response.edit_message(view=None)
            await self.playView.update_board()
            return
               
        self.cards_with_effects = list(filter(
            lambda a: not self.has_no_effect[self.selected_cards.index(a)], 
            self.selected_cards))
        view = EffectView.View(self)
        await interaction.response.edit_message(content=f"You've chosen, in this order, {self.selected_cards}. {view.initial_content}", view = view)
        
    
    @discord.ui.button(label = "Cancel selection", row = 4, style=discord.ButtonStyle.red) 
    async def cancelselection(self, interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            if item.label != '----' and item.label != 'Confirm' and item.label != 'Cancel selection':
                item.disabled = not (self.reference_card.faction == item.card.faction or self.reference_card.health == item.card.health)
                item.style = ButtonStyle.blurple if not item.disabled else ButtonStyle.grey
        self.selected_cards = []
        self.card_parameters = []
        await interaction.response.edit_message(view=self)



class ComplexCardsInColumnButton(discord.ui.Button):
    def __init__(self, card: Card, style: ButtonStyle = ButtonStyle.primary, disabled: bool = False, custom_id: str | None = None, url: str | None = None, emoji: str | Emoji | PartialEmoji | None = None, row: int | None = None):
        super().__init__(style=style, label=f"{card.position+1}. {card}", disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
        self.card = card
        self.view: ComplexView

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_cards.append(self.card)

        #if selected cards > 3 -> all columns should be disabled
        self.view.clear_items()
        self.view.generate_buttons()
        await interaction.response.edit_message(view=self.view)

class ComplexColumnButton(discord.ui.Button):
    def __init__(self, column, *, disabled: bool = False, custom_id: str | None = None, url: str | None = None, emoji: str | Emoji | PartialEmoji | None = None, row: int | None = None):
        super().__init__(style=discord.ButtonStyle.primary, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
        self.column = column
        self.label = f'Column {column + 1}'
    
    async def callback(self, interaction: discord.Interaction):
        self.view: ComplexView
        
        self.view.clear_items()
        for card in self.view.player.columns[self.column]:
            self.view.add_item(ComplexCardsInColumnButton(card, disabled = not self.view.compatible(card)))
        
        for item in self.view.children:
            if item.label == 'Confirm': 
                item.disabled = False
                break 

        await interaction.response.edit_message(view=self.view)

class ComplexViewConfirmButton(discord.ui.Button):
    async def callback(self, interaction: discord.Interaction):
        self.view: ComplexView
        self.view.card_parameters = [None] * len(self.view.selected_cards)
        self.view.has_no_effect = [card.faction in EffectView.FACTIONS_WITH_NO_CUSTOM_EFFECT for card in self.view.selected_cards]
        if all(self.view.has_no_effect): #activate cards, no entering view
            game = self.view.playView.game
            player = game.player1 if game.isPlayer1Turn else game.player2
            player.activate_and_discard(self.view.reference_card, self.view.selected_cards, self.view.card_parameters)
            # game.isPlayer1Turn = not game.isPlayer1Turn # UNCOMMENT
            await interaction.response.edit_message(view=None)
            await self.view.playView.update_board()
            return
               
        self.view.cards_with_effects = list(filter(
            lambda a: not self.view.has_no_effect[self.view.selected_cards.index(a)], 
            self.view.selected_cards))
        view = EffectView.View(self.view)
        await interaction.response.edit_message(content=f"You've chosen, in this order, {self.view.selected_cards}. {view.initial_content}", view = view)

class ComplexViewCancelButton(discord.ui.Button):
    async def callback(self, interaction: discord.Interaction):
        self.view : ComplexView
        self.view.clear_items()
        self.view.selected_cards = []
        self.view.card_parameters = []
        self.view.generate_buttons()
        await interaction.response.edit_message(view=self.view)

class ComplexView(RiftforceView):
    def __init__(self, button: CardSelectConfirm):
        super().__init__(bot=button.view.bot, timeout=button.view.timeout)
        self.player: Player = button.view.player
        self.reference_card: Card = button.view.selected_cards[0]
        self.playView: MainView = button.view.playView
        self.selected_cards: list[Card] = []
        self.card_parameters = []

        self.generate_buttons()

    def compatible(self, proposed_card):
        #Check what reference_card and selected_cards have in common
        if proposed_card in self.selected_cards: return False
        if len(self.selected_cards) >= 3: return False

        cards: list[Card] = self.selected_cards.copy()
        cards.append(self.reference_card)
        cards.append(proposed_card)

        if len({card.health for card in cards}) == 1:   return True
        if len({card.faction for card in cards}) == 1:  return True
        return False        

    def generate_buttons(self):
        self.add_item(ComplexViewConfirmButton(label = 'Confirm', disabled = not  self.selected_cards, row = 4))
        self.add_item(ComplexViewCancelButton(label = 'Cancel selection', row = 4))

        # if len(self.selected_cards) >= 3: return

        for i, column in enumerate(self.player.columns):

            incompatible = []
            for card in column:
                incompatible.append( not self.compatible(card) )

            if all(incompatible): #Disallow entering a column without activable cards / an empty column
                self.add_item(ComplexColumnButton(i, disabled=True))
            else:
                self.add_item(ComplexColumnButton(i))
