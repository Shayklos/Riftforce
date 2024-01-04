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
            view=SimpleView(self.view.bot, self.view.player, self.view.selected_cards[0], self.view.playView)) #when there is at most 4 cards in a column

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
            if item.card: item.disabled = True
            
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


class MenuSimpleButton(discord.ui.Button):
    def callback(self, interaction: discord.Interaction):
        self.style = ButtonStyle.green

class SimpleView(RiftforceView):
    def __init__(self, bot, player, reference_card, playView, timeout: float | None = 180):
        super().__init__(bot=bot, timeout=timeout)
        self.player: Player = player
        self.reference_card = reference_card
        self.playView: MainView = playView
        self.placements, self.card_parameters
        self.columns = []

        self.generate_buttons()

    def generate_buttons(self):
        max_column_len = max([len(column) for column in self.player.columns])
        for column in self.player.columns: 
            for i in range(max_column_len):
                if len(column) > i: self.add_item(MenuSimpleButton(row = i, label = str(column[i])))
                else:               self.add_item(MenuSimpleButton(row = i, label = '----', style=ButtonStyle.grey))
        
    @discord.ui.button(label = "Confirm", row = 1, style=discord.ButtonStyle.green, disabled=True) 
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.clear_items()
        # self.player.play_and_discard(self.selected_cards, self.columns)
        self.player.activate_and_discard(self.reference_card, self.placements, self.card_parameters)
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