from __future__ import annotations
import discord
from discord.enums import ButtonStyle
from discord.emoji import Emoji
from discord.interactions import Interaction
from discord.partial_emoji import PartialEmoji


from RiftforceView import RiftforceView
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from Main import MainView, PlayButton
from image_manipulation import *

class CardSelectConfirm(discord.ui.Button):
    def __init__(self, *, style: ButtonStyle = ButtonStyle.secondary, label: str | None = None, disabled: bool = False, custom_id: str | None = None, url: str | None = None, emoji: str | Emoji | PartialEmoji | None = None, row: int | None = None):
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
        self.card = None 

    async def callback(self, interaction: discord.Interaction):
        self.view : CardSelectView
        view = CardColumnView(self.view.bot, self.view.player, self.view.selected_cards, self.view.playView)
        view.index = 0
        await interaction.response.edit_message(
            content= f"You've chosen {self.view.selected_cards}. Where are you placing {self.view.selected_cards[view.index]}?", 
            view=view)

class CardSelectCancel(discord.ui.Button):
    def __init__(self, *, style: ButtonStyle = ButtonStyle.secondary, label: str | None = None, disabled: bool = False, custom_id: str | None = None, url: str | None = None, emoji: str | Emoji | PartialEmoji | None = None, row: int | None = None):
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
        self.card = None 

    async def callback(self, interaction: discord.Interaction):
        self.view: CardSelectView
        for item in self.view.children:
            item.disabled = False
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
            if item.card and not item.card.isCompatible(self.view.selected_cards):
                item.disabled = True 
            
        await interaction.response.edit_message(view=self.view)

class CardSelectView(RiftforceView):
    def __init__(self, button: PlayButton, player):
        super().__init__(bot=button.view.bot, timeout=button.view.timeout)
        self.player: Player = player
        self.selected_cards = []
        self.playView = button.view

        self.add_item(CardSelectConfirm(style = discord.ButtonStyle.green,
                                        label = 'Confirm',
                                        row = 4))
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



class CardColumnButton(discord.ui.Button):
    def __init__(self, column, *, disabled: bool = False, custom_id: str | None = None, url: str | None = None, emoji: str | Emoji | PartialEmoji | None = None, row: int | None = None):
        super().__init__(style=discord.ButtonStyle.primary, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
        self.column = column
        self.label = f'Column {column + 1}'
    
    async def callback(self, interaction: discord.Interaction):
        self.view: CardColumnView
        self.view.columns.append(self.column)

        enable_confirm_button = len(self.view.columns) == len(self.view.selected_cards)
        
        if  len(self.view.selected_cards) - len(self.view.columns) == 2:
            for item in self.view.children:
                if 'Column' in item.label and item.column - self.column > 2:
                    item.disabled = True
            
            if len(self.view.selected_cards) > len(self.view.columns):
                await interaction.response.edit_message(content = f'Where are you placing {self.view.selected_cards[len(self.view.columns)]}?', view=self.view)
            else:
                content = "You're placing "
                for card, column in zip(self.view.selected_cards, self.view.columns):
                    content += f"{card} in column {column + 1}, "
                content = content[:-2] + '. Is this correct?'
                await interaction.response.edit_message(content = content, view=self.view)
            return
        
        for item in self.view.children:
            if enable_confirm_button and 'Confirm' in item.label:
                item.disabled = False
            if 'Column' in item.label:
                if not self.view.isColumnCompatible(item.column):
                    item.disabled = True


        if len(self.view.selected_cards) > len(self.view.columns):
                await interaction.response.edit_message(content = f'Where are you placing {self.view.selected_cards[len(self.view.columns)]}?', view=self.view)
        else:
            content = "You're placing "
            for card, column in zip(self.view.selected_cards, self.view.columns):
                content += f"{card} in column {column + 1}, "
            content = content[:-2] + '. Is this correct?'
            await interaction.response.edit_message(content=content, view=self.view)
        return

class CardColumnView(RiftforceView):
    def __init__(self, bot, player, selected_cards, playView, timeout: float | None = 180):
        super().__init__(bot=bot, timeout=timeout)
        self.player: Player = player
        self.selected_cards: list[Card] = selected_cards
        self.playView: MainView = playView
        self.columns = []

        for i in range(5):
            self.add_item(CardColumnButton(i))
    
    def isColumnCompatible(self, column:int):
        if len(self.columns) > len(self.selected_cards) - 1: return False #TODO test for each num of cards

        c_copy = self.columns.copy()
        c_copy.append(column)
        l = sorted(c_copy, reverse=True)
        if len(set(l)) == 1 : return True 
        for i in range(len(l) - 1):
            if l[i] - l[i+1] != 1: return False
        return True

    @discord.ui.button(label = "Confirm", row = 1, style=discord.ButtonStyle.green, disabled=True) 
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.clear_items()
        self.player.play_and_discard(self.selected_cards, self.columns)

        self.playView.log += f"\n{self.player.username} has **played** cards: "
        for card, column in zip(self.selected_cards, self.columns):
            self.playView.log += f"{card} in column {column + 1}, "
        self.playView.log = self.playView.log[:-2] + "."

        self.playView.game.change_turn()
        if self.playView.game.isPlayer1Turn: self.playView.log += self.playView.turn_msg()
        for card in self.selected_cards:
            if card.faction == 'Love':
                await interaction.response.edit_message(content=f"Which card will your Love heal?.", view = LoveView(self))
                return
        await self.playView.update_board()
        await interaction.response.edit_message(content=f"You've chosen {self.selected_cards}.", view = None)
        
    
    @discord.ui.button(label = "Cancel selection", row = 1, style=discord.ButtonStyle.red) 
    async def cancelselection(self, interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            item.disabled = False if item.label != 'Confirm' else True
            if 'Column' in item.label : item.style = discord.ButtonStyle.blurple
        self.columns = []
        await interaction.response.edit_message(view=self)


class LoveButton(discord.ui.Button):
    def __init__(self, card: Card, *, style: ButtonStyle = ButtonStyle.blurple, label: str | None = None, disabled: bool = False, custom_id: str | None = None, url: str | None = None, emoji: str | Emoji | PartialEmoji | None = None, row: int | None = None):
        super().__init__(style=style, label=f"{card.position + 1} {card}", disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
        self.card = card
        self.view : LoveView
    
    async def callback(self, interaction:discord.Interaction) -> Any:
        self.card.health_left = self.card.health
        self.view.columns.pop(0)
        if self.view.columns:
            self.view.clear_items()
            for card in self.view.player.columns[self.view.columns[0]]:
                self.view.add_item(LoveButton(card))
            await interaction.response.edit_message(view=self.view)
        else:
            await self.view.underlying_view.playView.update_board()
            await interaction.response.edit_message(content=f"You've chosen {self.view.selected_cards}.", view = None)


class LoveView(RiftforceView):
    def __init__(self, underlying_view: CardColumnView):
        super().__init__(bot=underlying_view.bot, timeout=underlying_view.timeout)
        self.underlying_view = underlying_view
        self.selected_cards: list[Card] = underlying_view.selected_cards
        self.columns: list[int] = [card.column for card in self.selected_cards if card.faction == 'Love']
        self.player: Player = underlying_view.player 

        for card in self.player.columns[self.columns[0]]:
            self.add_item(LoveButton(card))
    