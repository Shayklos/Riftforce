import discord
from discord.ext import commands
from random import random
import io 

from RiftforceView import RiftforceView
from Draft import DraftView
from image_manipulation import *

class InitialView(RiftforceView):
    def __init__(self, bot, author):
        super().__init__(bot = bot, timeout=180)
        self.bot: commands.Bot = bot
        self.proposingPlayer: discord.User = author

    @discord.ui.button(label = "Play!", row = 0, style=discord.ButtonStyle.primary) 
    async def play_with_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        if random() > 0.5:
            player1 = interaction.user
            player2 = self.proposingPlayer
        else:
            player2 = interaction.user
            player1 = self.proposingPlayer
        
        content = f"""{player1.display_name} will be Player 1 (plays at the bottom) and {player2.display_name} will be Player 2 (plays at the top).
Player 1 starts drafting first, while Player 2 starts with a random elemental in their middle column."""
        await interaction.response.edit_message(content=content, view = None)
        draft = Draft()
        p2_img, d_img, p1_img = draftImg_separate(draft)
        
        channel = self.bot.get_channel(interaction.channel_id) or await self.bot.fetch_channel(interaction.channel_id)
        with io.BytesIO() as a:
            p2_img.save(a, 'JPEG')
            a.seek(0)
            player2_factions_msg = await channel.send("Player 2 factions:", file = discord.File(a, filename = "e.jpg"))
        with io.BytesIO() as a:
            d_img.save(a, 'JPEG')
            a.seek(0)
            draft_factions_msg = await channel.send("Available factions", file = discord.File(a, filename = "e.jpg"))
        with io.BytesIO() as a:
            p1_img.save(a, 'JPEG')
            a.seek(0)
            player1_factions_msg = await channel.send("Player 1 factions", file = discord.File(a, filename = "e.jpg"))
        draftView = DraftView(self.bot, draft, player1, player2, player1_factions_msg, draft_factions_msg, player2_factions_msg)
        draftView.msg = await channel.send(f"It's the turn of {player1.display_name} to pick a Faction.", 
                           view=draftView)

