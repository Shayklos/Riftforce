import discord
import io 

from RiftforceView import RiftforceView
from Main import MainView

from image_manipulation import *


class DraftButton(discord.ui.Button):
    async def callback(self, interaction: discord.Interaction):
        self.view: DraftView
        faction = self.label
        self.view.draft.pick(faction)
        await interaction.response.defer()
        await self.view.update_attachments()
        if self.view.draft.isPlayer1Turn:
            await self.view.msg.edit(content = f"It's the turn of {self.view.player1.display_name} to pick a Faction.", view = self.view)
        else:
            await self.view.msg.edit(content = f"It's the turn of {self.view.player2.display_name} to pick a Faction.", view = self.view)

class DraftView(RiftforceView):
    #TODO: interaction_check to ensure player2 doesnt choose player1 factions
    def __init__(self, bot, draft: Draft, player1, player2, p1msg, dmsg, p2msg):
        super().__init__(bot = bot, timeout=180)
        self.proposingPlayer = 0
        self.draft = draft
        self.player1: discord.User = player1
        self.player2: discord.User = player2
        self.p1msg: discord.Message = p1msg
        self.dmsg: discord.Message = dmsg
        self.p2msg: discord.Message = p2msg
        for faction in draft.factions:
            self.add_item(DraftButton(label = faction,style=discord.ButtonStyle.primary)) #TODO stylize row

    async def update_attachments(self):
        # p2_img, d_img, p1_img = draftImg_separate(self.draft)
        # with io.BytesIO() as a:
        #     p2_img.save(a, 'JPEG')
        #     a.seek(0)
        #     await self.p2msg.edit(attachments = [discord.File(a, filename = "e.jpg")])
        # with io.BytesIO() as a:
        #     d_img.save(a, 'JPEG')
        #     a.seek(0)
        #     await self.dmsg.edit(attachments = [discord.File(a, filename = "e.jpg")])
        # with io.BytesIO() as a:
        #     p1_img.save(a, 'JPEG')
        #     a.seek(0)
        #     await self.p1msg.edit(attachments = [discord.File(a, filename = "e.jpg")])

        self.clear_items()

        if len(self.draft.player2_factions) < 1: #should be 4
            for faction in self.draft.factions:
                self.add_item(DraftButton(label = faction,style=discord.ButtonStyle.blurple)) #TODO stylize row
        else: #Drafting finished
            # game = Game(Player(self.draft.player1_factions), Player(self.draft.player2_factions))
            game = GameTest()
            game.player1.userid = self.player1.id
            game.player2.userid = self.player2.id
            game.player1.username = self.player1.display_name
            game.player2.username = self.player2.display_name
            channel = self.dmsg.channel
            await self.dmsg.delete()
            board_img = boardImg(game.board)
            with io.BytesIO() as a:
                board_img.save(a, 'JPEG')
                a.seek(0)
                playView = MainView(game, bot = self.bot)
                playView.msg = await channel.send(f"It's the turn of {self.player1.display_name}", 
                               view = playView, 
                               file = discord.File(a, filename = "e.jpg"))
            
