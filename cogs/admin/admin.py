import discord
import logging
from discord.ext import commands

from core.bot import YaeMiko
from core.colors import *

class Admin(commands.Cog):
    def __init__(self, client: YaeMiko) -> None:
        self.client = client
        self.client.logging_config['loggers']['yaemiko.admin'] = {
            "handlers": ["debugHandler", "fileHandler"],
            "level": "DEBUG",
            "propagate": False
        }

        self.client.configure_logger()
        self.logger = logging.getLogger("yaemiko.admin")

    # async def validate(self, message: discord.Message) -> None:
    #     """Validates messages if 'yaechannel' is set"""
    #     # Checking for validity of the command
    #     ctx = await self.client.get_context(message)
    #     if not ctx.command or ctx.command_failed:
    #         return

    #     # Checking if the command is invoked in 'yaechannel'
    #     config = self.config.get(ctx.guild.id)
    #     if config.getint(__name__, 'yae_channel') != ctx.channel.id:
    #         return

    #     # Checking if the command starts with the prefix
    #     pref = self.client.prefix(self.client, message)
    #     if message.content.startswith(pref):
    #         self.client.logger.debug(f"Command {ctx.command.name} invoked in {ctx.guild.id}")
    #         return

    #     await message.delete()
    #     await send_error_message(
    #         ctx, f"Invalid command: '{message.content}'.\n\n**Invalid commands will be deleted in this channel.**"
    #     )

    # async def has_access(self, ctx: commands.Context, level: int) -> bool:
    #     """Check if a user has required access level"""
    #     flag: bool = True if Database(ctx.guild.id).get_access(ctx.author.id) >= level else False

    #     if not flag:
    #         await ctx.send(
    #             embed=discord.Embed(
    #                 colour=red,
    #                 description=f"You must have at least access level **{level}** to use this command."
    #             )
    #         )

    #     return flag

    # @commands.Cog.listener()
    # async def on_message(self, message: discord.Message) -> None:
    #     """Called whenever a message is sent"""
    #     # Ignore if message comes from bot
    #     if message.author == self.client.user:
    #         return

    #     await self.validate(message)

    # @commands.command()
    # async def setprefix(self, ctx: commands.Context, *, pref: Optional[str] = "y!") -> None:
    #     """Sets the bot prefix per guild"""
    #     if not await self.has_access(ctx, levels['setprefix']):
    #         return

    #     config = self.client.config[ctx.guild.id]
    #     config.set('main', 'prefix', pref)

    #     await ctx.send(
    #         embed=discord.Embed(
    #             colour=pink,
    #             description=f"Server prefix has been set to **[{pref}]**."
    #         )
    #     )

    # @commands.command()
    # async def yaechannel(self, ctx: commands.Context, arg: bool = True) -> None:
    #     """Enables/disables commands-only mode for text channels"""
    #     if not await self.has_access(ctx, levels['yaechannel']):
    #         return

    #     config = self.config.get(ctx.guild.id)

    #     if not arg:
    #         config.delete(__name__, 'yae_channel')
    #         self.client.logger.debug(f"Disabled command checking for guild: {ctx.guild.id}")
    #         await ctx.send(
    #             embed=discord.Embed(
    #                 colour=pink,
    #                 description="This channel can now be used **freely**."
    #             )
    #         )
    #     else:
    #         config.set(__name__, 'yae_channel', f"{ctx.channel.id}")
    #         await ctx.send(
    #             embed=discord.Embed(
    #                 colour=red,
    #                 description="This channel can now only be used for **Yae Miko commands**."
    #             )
    #         )
    #         self.client.logger.debug(f"Enabled command checking in channel: {ctx.channel.id} for guild: {ctx.guild.id}")

    # @commands.command(aliases=["sa"])
    # async def setaccess(self, ctx: commands.Context, member: discord.Member, access: int = 0) -> None:
    #     """Modify access level of specified user"""
    #     db = Database(ctx.guild.id)

    #     if db.compare_access(ctx.author.id, member.id) == member.id or ctx.author == member:
    #         await ctx.send(
    #             embed=discord.Embed(
    #                 colour=red,
    #                 description="You cannot change the access level for this user."
    #             )
    #         )
    #         return
        
    #     if access == 0:
    #         db.delete_user(member.id)
    #         await ctx.send(
    #             embed=discord.Embed(
    #                 colour=pink,
    #                 description=f"Removed access for {member.nick if member.nick else member.name}."
    #             )
    #         )
    #         self.client.logger.debug(f"Removed access for user: {member.id} in guild: {ctx.guild.id}")
    #         return
            
    #     db.update(member.id, access)
    #     await ctx.send(
    #         embed=discord.Embed(
    #             colour=pink,
    #             description=f"Set **{member.nick if member.nick else member.name}'s** access to {access}"
    #         )
    #     )

    # @commands.command()
    # async def sudo(self, ctx: commands.Context) -> None:
    #     """Gives bot owner highest access level (for debugging)"""
    #     if ctx.author.id != 200034086444597248:
    #         await ctx.send(
    #             embed=discord.Embed(
    #                 colour=red,
    #                 description="Only the bot owner is authorized to use this command."
    #             )
    #         )
    #         return

    #     db = Database(ctx.guild.id)
    #     db.update(200034086444597248, 5)

    #     await ctx.send(
    #         embed=discord.Embed(
    #             colour=pink,
    #             description="You have been given the maximum access level."
    #         )
    #     )

    @commands.command(aliases=["r"])
    async def restart(self, ctx: commands.Context) -> None:
        await ctx.send(
            embed=discord.Embed(
                colour=pink,
                description=f"The **restart** command has been issued by **{ctx.author.nick if ctx.author.nick else ctx.author.name}**"
            )
        )

        await self.client.close()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def echo(self, ctx: commands.Context, *, message: str) -> None:
        await ctx.message.delete()
        await ctx.send(message)

    @commands.command()
    async def sync(self, ctx: commands.Context, *, args: str = " ") -> None:
        params = args.split()

        clear = '-c' in params
        do_global = '-g' in params

        guild = self.client.test_guild

        if clear:
            ctx.bot.tree.clear_commands(guild=None if do_global else guild)

        if not do_global and not clear:
            ctx.bot.tree.copy_global_to(guild=guild)

        try:
            self.logger.debug("Sync started")
            synced = await ctx.bot.tree.sync(guild=None if do_global else guild)
        except discord.HTTPException:
            self.logger.debug("An error occurred while syncing application commands")
        finally:
            self.logger.debug("Sync finished")

        self.logger.debug(f"Synced {len(synced)} command{'s' if len(synced) > 1 else ''}{' globally.' if do_global else '.'}")
        
        await ctx.send(
            embed=discord.Embed(
                colour=pink,
                description=f"Synced {len(synced)} command{'s' if len(synced) > 1 else ''}{' globally.' if do_global else '.'}"
            )
        )
