from __future__ import annotations

import discord
from discord.ext import commands
from random import random
import io 

from RiftforceView import RiftforceView
import Play, Activate
from image_manipulation import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Draft import DraftView


class MainView(RiftforceView):
    def __init__(self, draftView: DraftView):
        super().__init__(bot=draftView.bot, timeout=None)
        self.game = draftView.game 
        self.msg : discord.Message
        self.game.player1.userid : int
        self.game.player2.userid : int
        self.game.player1.username : str
        self.game.player2.username : str
        self.log = self.turn_msg(n = False)
        self.add_item(ShowHandButton(label='Show my hand', row = 0))
        self.add_item(PlayButton(label = "Play", row = 1))
        self.add_item(ActivateButton(label = "Activate", row = 1))
        self.add_item(CheckAndDrawButton(label = "Check & draw", row = 1))

    async def update_board(self, log = ""):
        print(self.game)
        board_img = boardImg(self.game.board)
        name = self.game.player1.username if self.game.isPlayer1Turn else self.game.player2.username
        self.log += f"{log}\nIt's the turn of {name}."

        if self.game.isFinished():
            winner = self.game.player1.username if self.game.player1.score > self.game.player2.score else self.game.player2.username
            self.log += f"__**{winner} has won!**__"
        with io.BytesIO() as a:
            board_img.save(a, 'JPEG')
            a.seek(0)
            await self.msg.edit(content = self.log[-2000:], 
                                view = self, 
                                attachments= [discord.File(a, filename = "e.jpg")])
            
            
    def turn_msg(self, n = True):
        l = f"**[Turn {self.game.turn_number}]** {self.game.player1.username} **{self.game.player1.score[0]}** - **{self.game.player2.score[0]}** {self.game.player2.username}"
        if n: return '\n' + l
        return l


    def activate_log(self, player, reference_card, selected_cards: list[Card], card_parameters):
        self.log += f"\n{player.username} has discarded {reference_card} and **activated** cards: "
        for card, param in zip(selected_cards, card_parameters):
            print(card, param)
            if card.faction == 'Water': self.log += f"{card} has dealt 2 damage to first enemy in column {card.column + 1}, moved to column {param+1}, and dealt 1 damage to first enemy in column {param+1}. "
            elif card.faction == 'Plant': self.log += f"{card} has dealt 2 damage to the first enemy in column {param+1} and moved that enemy to column {card.column + 1}. "
            elif card.faction == 'Thunderbolt': 
                if param[0] is None:
                    pass
                elif param[1] is None:
                    self.log += f"{card} has dealt damage to the {param[0] + 1}º enemy in column {card.column + 1}. "
                else:
                    self.log += f"{card} has dealt damage to the {param[0] + 1}º enemy, and after killing it, it dealt 2 damage to the {param[0] + 1}º in column {card.column + 1}. "
                
            elif card.faction == 'Air': self.log += f"{card} has moved to column {param+1} and dealt 1 damage to the first enemy in column {param+1} and the columns adjacent to it. "
            elif card.faction == 'Ice': self.log += f"{card} has dealt damage to the first enemy in column {card.column + 1}. "
            elif card.faction == 'Earth': self.log += f"{card} has dealt 2 damage to the first enemy in column {card.column + 1}. "
            elif card.faction == 'Light': self.log += f"{card} has dealt damage in column {card.column + 1}, and has healed 1 damage to the {param[1]+1}º ally in column {param[0]+1} ({player.columns[param[0]][param[1]]}). "
            elif card.faction == 'Crystal': self.log += f"{card} has dealt 4 damage to the first enemy in column {card.column + 1}. "
            elif card.faction == 'Fire': self.log += f"{card} has dealt 3 damage to the first enemy in column {card.column + 1}, and 1 damage to the ally behind it. "
            elif card.faction == 'Shadow': self.log += f"{card} has moved to column {param+1}, and dealt 1 damage to first enemy in column {param+1}. "
            # ---- Expansion ----
            elif card.faction == 'Sand': self.log += f"{card} has moved to column {param+1}, and dealt 1 damage to each enemy in column {param+1}. "
            elif card.faction == 'Acid': self.log += f"{card} has dealt 3 damage to the first enemy in column {card.column + 1}, and 1 damage to the second enemy. "
            elif card.faction == 'Magnet': self.log += f"{card} has dealt 2 damage to the last enemy in the column that it was and has moved that enemy and itself to column {param+1}."
            elif card.faction == 'Love': self.log += f"{card} has dealt 2 damage to the first enemy in column {card.column + 1}."
            elif card.faction == 'Star': self.log += f"{card} has dealt 2 damage to the first enemy in column {card.column + 1}. [...]"
            elif card.faction == 'Sound': self.log += f"{card} has dealt 2 damage to the first enemy in column {card.column + 1}. [...]"
            elif card.faction == 'Lava': self.log += f"{card} has dealt 2 damage to the first enemy in adjacent locations. And 1 damage to itself and each card in front of it."
            elif card.faction == 'Beast': self.log += f"{card} has moved to column {param+1}, and dealt {'3'*card.isDamaged()}{'2'*(not card.isDamaged())} damage to the first enemy in column {param+1}. "


class ShowHandButton(discord.ui.Button):
    async def callback(self, interaction: discord.Interaction):
        self.view: MainView
        await interaction.response.defer(ephemeral=True)
        if interaction.user.id == self.view.game.player1.userid:
            cards = self.view.game.player1.hand
            n_cards_opponent = len(self.view.game.player2.hand)
        elif interaction.user.id == self.view.game.player2.userid:
            cards = self.view.game.player2.hand
            n_cards_opponent = len(self.view.game.player1.hand)
        else:
            await interaction.followup.send(content = f"You're not playing.", ephemeral=True)
            return
        if not cards:
            await interaction.followup.send(content = f"Your hand is empty! Your opponent has **{n_cards_opponent}** cards.", ephemeral = True)
            return
        hand_img = createImgHand(cards)
        with io.BytesIO() as a:
            hand_img.save(a, 'JPEG')
            a.seek(0)
            await interaction.followup.send(content = f"Your cards! Your opponent has **{n_cards_opponent}** cards.", 
                                file= discord.File(a, filename = "e.jpg"),
                                ephemeral=True)

class PlayButton(discord.ui.Button):
    async def callback(self, interaction: discord.Interaction):
        self.view: MainView
        await interaction.response.defer(ephemeral=True)
        if interaction.user.id == self.view.game.player1.userid:
            if self.view.game.isPlayer1Turn:
                player = self.view.game.player1
            else:
                await interaction.followup.send(content = f"It's not your turn.", ephemeral=True)
                return 
            
        elif interaction.user.id == self.view.game.player2.userid:
            if not self.view.game.isPlayer1Turn:
                player = self.view.game.player2
            else:
                await interaction.followup.send(content = f"It's not your turn.", ephemeral=True)
                return 
            
        else:
            await interaction.followup.send(content = f"You're not playing.", ephemeral=True)
            return
        
        if not len(player.hand):
            await interaction.followup.send(content = f"You can't do this with an empty hand.", ephemeral=True)
            return 
        
        view = Play.CardSelectView(self, player)
        await interaction.followup.send(content = f"Which cards do you want to play?", ephemeral=True, view = view)

class ActivateButton(discord.ui.Button):
    async def callback(self, interaction: discord.Interaction):
        self.view: MainView
        await interaction.response.defer(ephemeral=True)
        if interaction.user.id == self.view.game.player1.userid:
            if self.view.game.isPlayer1Turn:
                player = self.view.game.player1
            else:
                await interaction.followup.send(content = f"It's not your turn.", ephemeral=True)
                return 
            
        elif interaction.user.id == self.view.game.player2.userid:
            if not self.view.game.isPlayer1Turn:
                player = self.view.game.player2
            else:
                await interaction.followup.send(content = f"It's not your turn.", ephemeral=True)
                return 
            
        else:
            await interaction.followup.send(content = f"You're not playing.", ephemeral=True)
            return
        
        if not len(player.hand):
            await interaction.followup.send(content = f"You can't do this with an empty hand.", ephemeral=True)
            return 
        
        view = Activate.CardSelectView(self, player)
        await interaction.followup.send(content = f"Which card do you want to discard and use its stats to activate?", ephemeral=True, view = view)

class CheckAndDrawButton(discord.ui.Button):
    async def callback(self, interaction: discord.Interaction):
        self.view: MainView
        await interaction.response.defer(ephemeral=True)
        if interaction.user.id == self.view.game.player1.userid:
            if self.view.game.isPlayer1Turn:
                player = self.view.game.player1
            else:
                await interaction.followup.send(content = f"It's not your turn.", ephemeral=True)
                return 
            
        elif interaction.user.id == self.view.game.player2.userid:
            if not self.view.game.isPlayer1Turn:
                player = self.view.game.player2
            else:
                await interaction.followup.send(content = f"It's not your turn.", ephemeral=True)
                return 
            
        else:
            await interaction.followup.send(content = f"You're not playing.", ephemeral=True)
            return
        
        if len(player.hand) == 7:
            await interaction.followup.send(content = f"You can't do this with a full hand.", ephemeral=True)
            return 
        
        player.draw()
        player.sort_hand()
        player.score[0] += player.controled_factions()
        self.view.log += f"\n{player.username} has **checked and drawn**. {player.username} gained {player.controled_factions()} points."
        self.view.game.change_turn()
        await self.view.msg.edit(content = self.view.log[-2000:])
        await interaction.followup.send(content = f"You gained {player.controled_factions()} points.", ephemeral=True)