import discord
from discord.ext import commands
from random import random
import io 

from RiftforceView import RiftforceView
import Play
from image_manipulation import *


class MainView(RiftforceView):
    def __init__(self, game: Game, bot):
        super().__init__(bot=bot, timeout=None)
        self.game = game 
        self.msg : discord.Message
        self.game.player1.user : discord.User
        self.game.player2.user : discord.User

        self.add_item(ShowHandButton(label='Show my hand', row = 0))
        self.add_item(PlayButton(label = "Play", row = 1))
        self.add_item(ActivateButton(label = "Activate", row = 1))
        self.add_item(CheckAndDrawButton(label = "Check & draw", row = 1))

    async def update_board(self):
        board_img = boardImg(self.game.board)
        name = self.game.player1.user.display_name if self.game.isPlayer1Turn else self.game.player2.user.display_name
        with io.BytesIO() as a:
            board_img.save(a, 'JPEG')
            a.seek(0)
            await self.msg.edit(content = f"It's the turn of {name}", 
                                view = self, 
                                attachments= [discord.File(a, filename = "e.jpg")])
            


class ShowHandButton(discord.ui.Button):
    async def callback(self, interaction: discord.Interaction):
        self.view: MainView
        await interaction.response.defer(ephemeral=True)
        if interaction.user == self.view.game.player1.user:
            cards = self.view.game.player1.hand
            n_cards_opponent = len(self.view.game.player2.hand)
        elif interaction.user == self.view.game.player2.user:
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
        if interaction.user == self.view.game.player1.user:
            if self.view.game.isPlayer1Turn:
                player = self.view.game.player1
            else:
                await interaction.followup.send(content = f"It's not your turn.", ephemeral=True)
                return 
            
        elif interaction.user == self.view.game.player2.user:
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
        
        view = Play_CardSelectView(self.view.bot, player, self.view)
        await interaction.followup.send(content = f"Which cards do you want to play?", ephemeral=True, view = view)

class ActivateButton(discord.ui.Button):
    async def callback(self, interaction: discord.Interaction):
        self.view: MainView
        await interaction.response.defer(ephemeral=True)
        if interaction.user == self.view.game.player1.user:
            if self.view.game.isPlayer1Turn:
                player = self.view.game.player1
            else:
                await interaction.followup.send(content = f"It's not your turn.", ephemeral=True)
                return 
            
        elif interaction.user == self.view.game.player2.user:
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
        
        view = Play.CardSelectView(self.view.bot, player, self.view)
        await interaction.followup.send(content = f"Which cards do you want to play?", ephemeral=True, view = view)

class CheckAndDrawButton(discord.ui.Button):
    async def callback(self, interaction: discord.Interaction):
        self.view: MainView
        await interaction.response.defer(ephemeral=True)
        if interaction.user == self.view.game.player1.user:
            if self.view.game.isPlayer1Turn:
                player = self.view.game.player1
            else:
                await interaction.followup.send(content = f"It's not your turn.", ephemeral=True)
                return 
            
        elif interaction.user == self.view.game.player2.user:
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
        await interaction.followup.send(content = f"You gained {player.controled_factions()} points.", ephemeral=True)

