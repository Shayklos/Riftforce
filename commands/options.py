import discord
from discord import app_commands
from discord.ext import commands
from discord.ui.item import Item
from typing import Any, Optional
import sys, PIL.Image, io
sys.path.append('../Riftforce')

class Options(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot 

    @app_commands.command(description="Displays what options you can do in a turn.")
    async def options(self, interaction: discord.Interaction):
        e = PIL.Image.open(self.bot.image_directory + 'options.png')
        with io.BytesIO() as a:
            e.save(a, 'PNG')
            a.seek(0)
            await interaction.response.send_message(file = discord.File(a, filename = "e.png"))


async def setup(bot: commands.Bot):
    await bot.add_cog(Options(bot))
    print(f"Loaded /options command.")