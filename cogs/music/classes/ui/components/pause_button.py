import discord
from discord.ui import Button

from .... import colors

class PauseButton(Button):
    def __init__(self, onClick):
        super().__init__(label="Pause", style=discord.ButtonStyle.success)
        self.onClick = onClick

    async def callback(self, interaction: discord.Interaction) -> None:
        song = await self.onClick()
        await interaction.response.send_message(
            embed=discord.Embed(
                colour=colors.pink,
                description=f"Paused 🎶 **{song.title}**."
            ),
            delete_after=10
        )
