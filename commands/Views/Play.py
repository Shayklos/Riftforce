import discord
from discord.enums import ButtonStyle
from discord.emoji import Emoji
from discord.partial_emoji import PartialEmoji


from RiftforceView import RiftforceView
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Main import MainView
from image_manipulation import *

class CardSelectConfirm(discord.ui.Button):
    def __init__(self, *, style: ButtonStyle = ButtonStyle.secondary, label: str | None = None, disabled: bool = False, custom_id: str | None = None, url: str | None = None, emoji: str | Emoji | PartialEmoji | None = None, row: int | None = None):
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
        self.card = None 

    async def callback(self, interaction: discord.Interaction):
        self.view : CardSelectView
        await interaction.response.edit_message(
            content= f"You've chosen {self.view.selected_cards}. Where are you placing {self.view.selected_cards[0]}?", 
            view=CardColumnView(self.view.bot, self.view.player, self.view.selected_cards, self.view.playView))

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
    def __init__(self, bot, player, playView, timeout: float | None = 180):
        super().__init__(bot=bot, timeout=timeout)
        self.player: Player = player
        self.selected_cards = []
        self.playView = playView

        self.add_item(CardSelectConfirm(style = discord.ButtonStyle.green,
                                        label = 'Confirm',
                                        row = 4))
        self.add_item(CardSelectCancel(style = discord.ButtonStyle.red,
                                        label = 'Cancel selection',
                                        row = 4))
        
        row = 1
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
        self.column = column - 1
        self.label = f'Column {column}'
    
    async def callback(self, interaction: discord.Interaction):
        self.view: CardColumnView
        self.view.columns.append(self.column)

        enable_confirm_button = len(self.view.columns) == len(self.view.selected_cards)
        
        if  len(self.view.selected_cards) - len(self.view.columns) == 2:
            for item in self.view.children:
                if 'Column' in item.label and item.column - self.column > 2:
                    item.disabled = True
            await interaction.response.edit_message(view=self.view)
            return
        
        for item in self.view.children:
            if enable_confirm_button and 'Confirm' in item.label:
                item.disabled = False
            if 'Column' in item.label:
                if not self.view.isColumnCompatible(item.column):
                    item.disabled = True

        await interaction.response.edit_message(view=self.view)

class CardColumnView(RiftforceView):
    def __init__(self, bot, player, selected_cards, playView, timeout: float | None = 180):
        super().__init__(bot=bot, timeout=timeout)
        self.player: Player = player
        self.selected_cards = selected_cards
        self.playView: MainView = playView
        self.columns = []

        for i in (1,2,3,4,5):
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
        self.playView.game.isPlayer1Turn = not self.playView.game.isPlayer1Turn
        await self.playView.update_board()
        await interaction.response.edit_message(content=f"You've chosen {self.selected_cards}.", view = self)
        
    
    @discord.ui.button(label = "Cancel selection", row = 1, style=discord.ButtonStyle.red) 
    async def cancelselection(self, interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            item.disabled = False if item.label != 'Confirm' else True
            if 'Column' in item.label : item.style = discord.ButtonStyle.blurple
        self.columns = []
        await interaction.response.edit_message(view=self)