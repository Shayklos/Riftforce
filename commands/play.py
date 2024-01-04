import discord
from discord import app_commands
from discord.emoji import Emoji
from discord.enums import ButtonStyle
from discord.ext import commands
from discord.interactions import Interaction
from discord.partial_emoji import PartialEmoji
from discord.ui.item import Item
from typing import Any, Coroutine, Optional, Union
import sys, io
from random import random
sys.path.insert(0, './commands/Views')
sys.path.append('../Riftforce')
sys.path.insert(0, './riftforce')

from InitialView import InitialView

from Game import Draft, Game
from Player import Player
from image_manipulation import *
    
class Play(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot 

    @app_commands.command(description="Starts a Riftforce match.")
    async def play(self, interaction: discord.Interaction):
        view = InitialView(self.bot, interaction.user)
        await interaction.response.send_message(f"¡{interaction.user.display_name} wants to play a Riftforce match!", view = view)
        # p =  Player({'Agua', 'Fuego', 'Luz'})
        # p.draw()
        # p.sort_hand()
        # await interaction.response.send_message(f"test", view = CardColumnView(self.bot, p, p.hand[:3], playView = None))



async def setup(bot: commands.Bot):
    await bot.add_cog(Play(bot))
    print(f"Loaded /play command.")