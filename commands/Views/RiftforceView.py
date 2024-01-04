import discord

#TODO asyncio.to_thread for PIL logic
class RiftforceView(discord.ui.View):
    def __init__(self, *, bot, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.bot = bot

    # async def interaction_check(self, interaction: discord.Interaction):
    #     #checks if user who used the button is the same who called the command
    #     if interaction.user == self.proposingPlayer:
    #         return True
    #     else:
    #         await interaction.user.send("Only the user who called the command can use the buttons.")
    
    # async def on_error(self, interaction: discord.Interaction, error: Exception, item: Item[Any]) -> None:
    #     print(error)
    #     await interaction.user.send("Something went horribly wrong. Uh oh. Please report it to `shayklos` on Discord!")

    def enable_buttons(self, list):
     for item in self.children:
         if item.label in list:
             item.disabled = False

    def disable_buttons(self, list):
     for item in self.children:
         if item.label in list:
             item.disabled = True
