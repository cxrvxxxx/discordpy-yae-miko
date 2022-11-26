import discord
import sqlite3
import os
from typing import Optional, Union

from discord.ext import commands
from core.logger import console_log
from core.prefix import prefix
from core import colors
from core.message import *

# create data directory if non existent
if not os.path.exists('data'):
    os.mkdir('data')

class Admin(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.config = client.config

    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     pf = prefix(self.client, message)
    #     if message.author == self.client.user:
    #         return

    #     ctx = await self.client.get_context(message)
    #     if ctx:
    #         if ctx.command and not ctx.command_failed:
    #             console_log(ascii(f"{ctx.guild.name}/{ctx.channel.name}/{ctx.author.nick if ctx.author.nick else ctx.author.name}: {ctx.message.content}"))

    #         # delete non yae command messages in yae channel
    #         config = self.config.get(ctx.guild.id)
    #         if config.getint(__name__, 'yae_channel') == ctx.channel.id:
    #             ctx = await self.client.get_context(message)
    #             if not message.content.startswith(pf) or not ctx.command:
    #                 await message.delete()
    #                 await ctx.send(embed = discord.Embed(description = f"Invalid command: '{message.content}'.\n\n**Invalid commands will be deleted in this channel.**", colour = colors.pink), delete_after=10)

    @commands.command()
    async def setprefix(self, ctx, *, pref) -> None:
        """Sets the bot prefix per guild"""
        model = Database(ctx.guild.id)

        if model.get_access(ctx.author.id) < 3:
            await ctx.send(
                embed = discord.Embed(
                    description = "You must have at least access level 3 to use this command.",
                    colour = colors.red
                )
            )
            return

        config = self.client.config[ctx.guild.id]

        config.set('main', 'prefix', pref)

        await ctx.send(
            embed = discord.Embed(
                description = f"Server prefix has been set to **[{pref}]**.",
                colour = colors.pink
            )
        )

    @commands.command()
    async def yaechannel(self, ctx, arg=None):
        config = self.config.get(ctx.guild.id)

        if arg == 'disable':
            config.delete(__name__, 'yae_channel')
        else:
            config.set(__name__, 'yae_channel', f"{ctx.channel.id}")
            await send_basic_response(ctx, "This channel can now only be used for **Yae Miko commands**.", colors.pink)

    # set a user's access level, 0 means the user will be removed from the database
    @commands.command(aliases=["sa"])
    async def setaccess(self, ctx, member: discord.Member, access):
        db = Database(ctx.guild.id)

        if db.get_access(ctx.author.id) <= db.get_access(member.id) or ctx.author == member:
            await send_basic_response(ctx, "You cannot change the access level for this user.", colors.red)
            return
        
        if access == 0:
            db.delete_user(member.id)
            await send_basic_response(ctx, f"Removed access for {member.nick if member.nick else member.name}.", colors.pink)
            return
            
        db.update(member.id, access)
        await send_basic_response(ctx, f"Set **{member.nick if member.nick else member.name}'s** access to {access}", colors.pink)

    # owner command only, skips the check and grants maximum access
    @commands.command()
    async def sudo(self, ctx):
        db = Database(ctx.guild.id)

        if ctx.author.id != 200034086444597248:
            await send_basic_response(ctx, "Only the bot owner is authorized to use this command.")
            return

        db.update(200034086444597248, 5)

        await send_basic_response(ctx, "You have been given the maximum access level.", colors.pink)

    # restart the bot
    @commands.command(aliases=["r"])
    async def restart(self, ctx):
        db = Database(ctx.guild.id)
        required_access = 5 # set access level for this command
        
        if db.get_access(ctx.author.id) < required_access:
            await send_basic_response(ctx, "You must have at least access level 5 to execute this command.", colors.red)
            return

        await send_basic_response(ctx, f"The **restart** command has been issued by **{ctx.author.nick if ctx.author.nick else ctx.author.name}**", colors.pink)
        await self.client.close()

    # echoes the message sent by the author
    @commands.command()
    async def echo(self, ctx, *, message):
        db = Database(ctx.guild.id)
        required_access = 3 # set access level for this command

        if db.get_access(ctx.author.id) < required_access:
            await send_basic_response(ctx, "You do not have access to this command.", colors.red)
            return

        await ctx.message.delete()
        await ctx.send(message)

    # user management commands
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        author = ctx.author.nick if ctx.author.nick else ctx.author.name
        target = member.nick if member.nick else member.name

        try:
            await ctx.guild.kick(member, reason=reason)
        except:
            await send_basic_response(ctx, f"Am error occurred while trying to kick **{target}**.", colors.red)
        else:
            await send_basic_response(ctx, f"**{author}** kicked **{target}**. Reason: {reason}", colors.pink)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        author = ctx.author.nick if ctx.author.nick else ctx.author.name
        target = member.nick if member.nick else member.name

        try:
            await ctx.guild.ban(member, reason=reason)
        except:
            await send_basic_response(ctx, f"An error occurred while trying to ban **{target}**.", colors.red)
        else:
            await send_basic_response(ctx, f"**{author}** banned **{target}**. Reason: {reason}", colors.pink)

    @commands.command()
    @commands.has_permissions(manage_nicknames=True)
    async def nickname(self, ctx, member: discord.Member, *, nick):
        author = ctx.author.nick if ctx.author.nick else ctx.author.name
        target = member.nick if member.nick else member.name

        try:
            await member.edit(nick=nick)
        except:
            await send_basic_response(ctx, f"An error occurred while trying to rename **{target}**.", colors.red)
        else:
            await send_basic_response(ctx, f"**{author}** renamed **{target}** to **{nick}**.", colors.pink)

class Database:
    def __init__(self, guild_id):
        # init database controller
        path_to_db = f'./data/{guild_id}.db'
        self.conn = sqlite3.connect(path_to_db)
        self.c = self.conn.cursor()

        # init database table
        with self.conn:
            self.c.execute("CREATE TABLE IF NOT EXISTS users (uid INTEGER, access INTEGER)")

    def get_access(self, uid):
        with self.conn:
            self.c.execute("SELECT access FROM users WHERE uid=:uid", {"uid": uid})
            access = self.c.fetchone()

        if access:
            return access[0]
        else:
            return 0

    def add_user(self, uid, access):
        with self.conn:
            self.c.execute("SELECT * FROM users WHERE uid=:uid", {"uid": uid})
            data = self.c.fetchone()

            if not data:
                self.c.execute("INSERT INTO users VALUES (:uid, :access)", {"uid": uid, "access": access})

    def delete_user(self, uid):
        with self.conn:
            self.c.execute("DELETE FROM users WHERE uid=:uid", {"uid": uid})

    def update(self, uid, access):
        self.add_user(uid, access)
        with self.conn:
            self.c.execute("UPDATE users SET access=:access WHERE uid=:uid", {"uid": uid, "access": access})

async def setup(client):
    await client.add_cog(Admin(client))