import discord
from discord.ext import commands

from os import listdir, getenv
from dotenv import load_dotenv

load_dotenv() 
TOKEN = getenv('DISCORD_TOKEN')
GUILD_ID = getenv('DISCORD_GUILD_ID')
PREFIX = '/'

class RiftforceBot(commands.Bot):
    def __init__(self, intents: discord.Intents):
        super().__init__(command_prefix = PREFIX, intents = intents, activity=discord.Game(name="Riftforce"))
        self.image_directory = 'files/imgs/Original/'

    async def setup_hook(self):
        
        #Loads all commands in 'commands' folder
        for command in ["".join(('commands.', command[:-3])) for command in listdir('commands') if command[-3:] == '.py']:
            await self.load_extension(command)
            
        print("Bot is ready!")


intents = discord.Intents.default()
intents.message_content = True

riftforceBot = RiftforceBot(intents = intents)


if __name__ == '__main__':
    riftforceBot.run(TOKEN)