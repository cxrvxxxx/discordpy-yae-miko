import discord
from discord.ui import Button
from ... import colors

class PrevButton(Button):
    def __init__(self, onClick, disabled):
        super().__init__(label="Prev", style=discord.ButtonStyle.primary, disabled=disabled)
        self.onClick = onClick

    async def callback(self, interaction: discord.Interaction) -> None:
        song = await self.onClick()
        await interaction.response.send_message(
            embed=discord.Embed(
                colour=colors.pink,
                description=f"Skipped 🎶 **{song.title}**."
            ),
            delete_after=10
        )
