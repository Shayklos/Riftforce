from __future__ import annotations

import discord
import io 

from RiftforceView import RiftforceView
from Main import MainView

from image_manipulation import *
from Card import FACTION_EMOJI

class DraftButton(discord.ui.Button):
    async def callback(self, interaction: discord.Interaction):
        self.view: DraftView
        faction = self.label
        if interaction.user == self.view.player1 and not self.view.draft.isPlayer1Turn or interaction.user == self.view.player2 and self.view.draft.isPlayer1Turn:
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send(content = f"It's not your turn.", ephemeral=True)
            return

        self.view.draft.pick(faction)
        await interaction.response.defer()
        await self.view.update_attachments()
        if self.view.draft.isPlayer1Turn:
            await self.view.msg.edit(content = f"It's the turn of **{self.view.player1.display_name}** to pick a Faction.", view = self.view)
        else:
            await self.view.msg.edit(content = f"It's the turn of **{self.view.player2.display_name}** to pick a Faction.", view = self.view)

class DraftView(RiftforceView):
    #TODO: interaction_check to ensure player2 doesnt choose player1 factions
    def __init__(self, bot, draft: Draft, player1, player2, p1msg, dmsg, p2msg):
        super().__init__(bot = bot, timeout=1800)
        self.proposingPlayer = 0
        self.draft = draft
        self.player1: discord.User = player1
        self.player2: discord.User = player2
        self.p1msg: discord.Message = p1msg
        self.dmsg: discord.Message = dmsg
        self.p2msg: discord.Message = p2msg
        self.generate_buttons()

    async def update_attachments(self):
        p2_img, d_img, p1_img = draftImg_separate(self.draft)
        with io.BytesIO() as a:
            p2_img.save(a, 'JPEG')
            a.seek(0)
            await self.p2msg.edit(content = f"Player 2 {self.player2.display_name} factions {''.join(FACTION_EMOJI.get(f) for f in self.draft.player2_factions)}", attachments = [discord.File(a, filename = "e.jpg")])
        with io.BytesIO() as a:
            d_img.save(a, 'JPEG')
            a.seek(0)
            await self.dmsg.edit(attachments = [discord.File(a, filename = "e.jpg")])
        with io.BytesIO() as a:
            p1_img.save(a, 'JPEG')
            a.seek(0)
            await self.p1msg.edit(content = f"Player 1 {self.player1.display_name} factions {''.join(FACTION_EMOJI.get(f) for f in self.draft.player1_factions)}" , attachments = [discord.File(a, filename = "e.jpg")])

        self.clear_items()

        if len(self.draft.player2_factions) < 4: #should be 4
            self.generate_buttons()
        else: #Drafting finished
            self.game = Game(Player(self.draft.player1_factions), Player(self.draft.player2_factions))
            # self.game = GameTest()
            self.game.player1.userid = self.player1.id
            self.game.player2.userid = self.player2.id
            self.game.player1.username = self.player1.display_name
            self.game.player2.username = self.player2.display_name
            channel = self.dmsg.channel
            await self.dmsg.delete()
            board_img = boardImg(self.game.board)
            with io.BytesIO() as a:
                board_img.save(a, 'JPEG')
                a.seek(0)
                playView = MainView(self)
                playView.msg = await channel.send(playView.log, 
                               view = playView, 
                               file = discord.File(a, filename = "e.jpg"))
            

    def generate_buttons(self):
        #This is intended to keep the same column/row format image_manipulation.draft_Img would generate
        if len(self.draft.factions) < 4:
            for faction in self.draft.factions:
                self.add_item(DraftButton(label = faction,style=discord.ButtonStyle.blurple))
            return 
        
        for i, faction in enumerate(self.draft.factions):
            if i < ceil(len(self.draft.factions)/2):
                self.add_item(DraftButton(label = faction,style=discord.ButtonStyle.primary, row = 0))
            else:
                self.add_item(DraftButton(label = faction,style=discord.ButtonStyle.primary, row = 1))