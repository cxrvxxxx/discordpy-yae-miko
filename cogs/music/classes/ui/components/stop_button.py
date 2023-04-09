import discord
from discord.ui import Button

from .... import colors

class StopButton(Button):
    def __init__(self, onClick):
        super().__init__(label="Stop", style=discord.ButtonStyle.danger)
        self.onClick = onClick

    async def callback(self, interaction: discord.Interaction) -> None:
        song = await self.onClick()
        await interaction.response.send_message(
            embed=discord.Embed(
                colour=colors.pink,
                description=f"Stopped 🎶 **{song.title}**."
            ),
            delete_after=10
        )
