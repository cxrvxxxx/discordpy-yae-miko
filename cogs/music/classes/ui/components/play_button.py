import discord
from discord.ui import Button

from .... import colors

class PlayButton(Button):
    def __init__(self, onClick) -> None:
        super().__init__(label="Play", style=discord.ButtonStyle.primary)
        self.onClick = onClick

    async def callback(self, interaction: discord.Interaction) -> None:
        song = await self.onClick()
        await interaction.response.send_message(
            embed=discord.Embed(
                colour=colors.pink,
                description=f"Resumed 🎶 **{song.title}**."
            ),
            delete_after=10
        )
