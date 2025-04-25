import discord
import asyncio
import requests
import platform
from bs4 import BeautifulSoup
import re
import aiohttp
from datetime import datetime, timedelta, timezone
from io import BytesIO
import pytz
from typing import Optional, Union
import ast
import inspect
import sqlite3
import aiosqlite
from discord.ext import commands, tasks
from googletrans import Translator, LANGUAGES
import os
import time
import json
from typing import Union
from discord.ui import Button, View, Modal, TextInput
from collections import defaultdict
import importlib
import sys
import traceback
from colorthief import ColorThief
from PIL import Image, ImageDraw, ImageFont, ImageOps
import random
from io import BytesIO
import io
from discord import app_commands

class MyContext(commands.Context):
    async def send(self, content: str = None, *args, **kwargs) -> discord.Message:
        return await super().send(content, *args, **kwargs)

intents = discord.Intents.default()
intents.messages = True
intents.members = True
intents.presences = True
intents.message_content = True
intents.guilds = True
intents.voice_states = True

NP_ADD_IDS = [1074831330015191072, 1088466341020827721]  # Replace with actual user IDs

async def get_prefix(bot, message):
    # Fetch the no-prefix user list
    cursor = await bot.db.execute("SELECT users FROM Np")
    np_users = await cursor.fetchall()
    np_user_ids = [int(i[0]) for i in np_users]

    # Return prefixes based on user type
    if message.author.id in np_user_ids:
        return ('?', '')  # No prefix and default prefix for no-prefix users
    return '?'  # Default prefix for regular users

bot = commands.Bot(command_prefix=get_prefix, intents=intents, context_class=MyContext, help_command=None, case_insensitive=True)
#bot.add_cog(SayCommand(bot))

MESSAGE_CONTENT = "🥂 𝘞𝘢𝘯𝘵 𝘳𝘰𝘭𝘦𝘴 Or Become Staff Press Buttons For Details"
GUILD_ID = 1255928131160772618
C_ROLE_ID = 1269734411977363527

# Color list for role-changing
colors = [
    discord.Color.red(),
    discord.Color.orange(),
    discord.Color.gold(),
    discord.Color.green(),
    discord.Color.blue(),
    discord.Color.purple(),
    discord.Color.teal(),
    discord.Color.magenta(),
    discord.Color.dark_red(),
    discord.Color.dark_gold(),
    discord.Color.dark_green(),
    discord.Color.dark_blue(),
    discord.Color.light_grey(),
    discord.Color.dark_grey(),
    discord.Color.darker_grey(),
    discord.Color.lighter_grey(),
    discord.Color.dark_teal(),
    discord.Color.dark_purple(),
    discord.Color.dark_orange(),
    discord.Color.dark_magenta(),
    discord.Color.blurple(),
    discord.Color.greyple(),
]

current_color_index = 0

async def start_color_changing():
    global current_color_index
    await bot.wait_until_ready()
    guild = bot.get_guild(GUILD_ID)
    if guild is None:
        print('Guild not found!')
        return
    role = guild.get_role(C_ROLE_ID)
    if role is None:
        print('Role not found!')
        return

    while True:
        end_time = time.time() + 15 * 60  # 15 minutes
        while time.time() < end_time:
            await role.edit(color=colors[current_color_index])
            current_color_index = (current_color_index + 1) % len(colors)
            await asyncio.sleep(30)
        await asyncio.sleep(600)

@tasks.loop(hours=1)
async def send_message_every_hour():
    plain_message = MESSAGE_CONTENT
    channel = bot.get_channel(1259897047109341216)

    vanity_button = discord.ui.Button(label="Vanity", style=discord.ButtonStyle.danger)
    perks_button = discord.ui.Button(label="Perks", style=discord.ButtonStyle.danger)

    async def vanity_callback(interaction):
        await interaction.response.send_message(
            "Paste Vanity In Your About https://discord.gg/sinner",
            ephemeral=True
        )

    async def perks_callback(interaction):
        perks_message = (
            "Here are your perks:\n\n"
            "**Golden Sinner:** Display Role\n\n"
            "**Pic Perms:** Vanity or Boost\n\n"
            "**Vanity Roles:** Nick,Reaction,Emoji,Reaction\n\n"
            "**Wl Roles:** Spam wl, Caps wl, Characters wl\n\n"
            "Enjoy your benefits and make the most out of them!"
        )
        await interaction.response.send_message(perks_message, ephemeral=True)

    vanity_button.callback = vanity_callback
    perks_button.callback = perks_callback

    view = discord.ui.View()
    view.add_item(vanity_button)
    view.add_item(perks_button)

    await channel.send(plain_message, view=view)

@bot.event
async def on_ready():
    send_message_every_hour.start()
    bot.loop.create_task(start_color_changing())

    if not hasattr(bot, 'db'):
        bot.db = await aiosqlite.connect('your_database.db')
        await bot.db.execute('''CREATE TABLE IF NOT EXISTS Np (
                                users BIGINT PRIMARY KEY
                              )''')
        await bot.db.commit()

    # Set custom status
    activity = discord.Activity(type=discord.ActivityType.playing, name="SINNERS KE HATERZ KI MKL")
    await bot.change_presence(status=discord.Status.online, activity=activity)

    print(f"Bot is ready. Logged in as {bot.user}")

@bot.event
async def on_user_update(before, after):
    # Check if the avatar has changed
    if before.avatar != after.avatar:
        # Find the guild where you want to log the avatar changes
        log_channel = bot.get_channel(1286380456266432512)
        
        embed = discord.Embed(title="Avatar Update", color=discord.Color.red())
        embed.set_author(name=str(after), icon_url=after.display_avatar.url)
        
        # Old avatar
        if before.avatar:
            embed.set_thumbnail(url=before.avatar.url)
            embed.add_field(
                name="Old Avatar",
                value=f"[Link to Old Avatar]({before.avatar.url})",
                inline=False
            )
        else:
            embed.add_field(
                name="Old Avatar",
                value="No previous avatar.",
                inline=False
            )

        # New avatar
        if after.avatar:
            embed.set_image(url=after.avatar.url)
            embed.add_field(
                name="New Avatar",
                value=f"[Link to New Avatar]({after.avatar.url})",
                inline=False
            )

        # Mention the user in the log message
        await log_channel.send(content=f"{after.mention} has updated their avatar!", embed=embed)

allowed_roles_ids = [1259932815810625699, 1276928831524966484]  # Allowed role IDs
avatar_disallow_role_id = 1259933150461562882  # Role that disallows avatar viewing
av_log_id = 1259934096025718875  # Channel ID for logging
av_bypass_user_ids = [1088466341020827721, 1074831330015191072]

# Helper function to get dominant color from avatar URL asynchronously
async def get_avatar_color(avatar_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(avatar_url) as response:
            img_data = await response.read()  # Asynchronously get the image data
            img = BytesIO(img_data)

    # Process the image in a separate thread to avoid blocking
    dominant_color = await asyncio.to_thread(process_image_color, img)
    return discord.Color.from_rgb(*dominant_color) if dominant_color else discord.Color.red()

# This function runs in a separate thread to avoid blocking the main event loop
def process_image_color(image):
    color_thief = ColorThief(image)
    try:
        dominant_color = color_thief.get_color(quality=1)
        return dominant_color
    except Exception as e:
        print(f"Error processing image color: {e}")
        return None

@bot.command(name="av")
async def av(ctx, user: discord.User = None):
    # If no user is provided, default to the command author
    if user is None:
        user = ctx.author

    # Check if the command invoker has at least one of the allowed roles
    if not any(role.id in allowed_roles_ids for role in ctx.author.roles):
        return

    # Check if the target user has the avatar disallow role (if the target is a server member)
    if isinstance(user, discord.Member):
        if avatar_disallow_role_id in [role.id for role in user.roles] and ctx.author.id not in av_bypass_user_ids:
            return
    else:
        try:
            member = await ctx.guild.fetch_member(user.id)
            if avatar_disallow_role_id in [role.id for role in member.roles] and ctx.author.id not in av_bypass_user_ids:
                return
        except discord.errors.NotFound:
            pass

    # Determine if the command user is viewing their own avatar
    is_author = ctx.author.id

    # Set the default avatar and color
    initial_avatar_url = user.avatar.url
    avatar_color = await get_avatar_color(initial_avatar_url) if is_author else discord.Color.red()

    # Display the avatar by default with the dominant color if it's the author
    embed = discord.Embed(title=f"Avatar of {user.name}", color=avatar_color)
    embed.set_image(url=initial_avatar_url)

    # Send the message and create the view after sending
    message = await ctx.reply(embed=embed)
    view = AvatarView(bot, message, user, ctx.author, initial_avatar_url, is_author)
    await message.edit(view=view)

    # Log the information to the designated log channel
    log_channel = bot.get_channel(av_log_id)
    if log_channel:
        await log_channel.send(f"{ctx.author.mention} viewed the avatar of {user.mention} in channel {ctx.channel.mention}")


# Avatar view with buttons for switching between Global and Server Avatars
class AvatarView(View):
    def __init__(self, bot, message, target_user, command_user, initial_avatar_url, is_author, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.message = message
        self.target_user = target_user
        self.command_user = command_user
        self.initial_avatar_url = initial_avatar_url
        self.is_author = is_author

    @discord.ui.button(label="Global Avatar", style=discord.ButtonStyle.grey)
    async def global_avatar_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.command_user.id:
            await interaction.response.send_message("You can't use this button.", ephemeral=True)
            return

        embed = discord.Embed(title=f"Global Avatar of {self.target_user.name}", color=discord.Color.red())
        embed.set_image(url=self.initial_avatar_url)
        await self.message.edit(embed=embed, view=self)

        await interaction.response.defer()

    @discord.ui.button(label="Server Avatar", style=discord.ButtonStyle.primary)
    async def server_avatar_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.command_user.id:
            await interaction.response.send_message("You can't use this button.", ephemeral=True)
            return

        if isinstance(self.target_user, discord.User):
            try:
                self.target_user = await interaction.guild.fetch_member(self.target_user.id)
            except discord.errors.NotFound:
                await interaction.response.send_message(f"Could not retrieve server-specific avatar for {self.target_user.name}, showing global avatar.", ephemeral=True)
                embed = discord.Embed(title=f"Global Avatar of {self.target_user.name}", color=discord.Color.red())
                embed.set_image(url=self.initial_avatar_url)
                await self.message.edit(embed=embed, view=self)
                return

        if self.target_user.guild_avatar:
            avatar_url = self.target_user.guild_avatar.url
            embed = discord.Embed(title=f"Server Avatar of {self.target_user.name}", color=discord.Color.red())
        else:
            avatar_url = self.initial_avatar_url
            embed = discord.Embed(title=f"{self.target_user.name} does not have a server-specific avatar, showing global avatar", color=discord.Color.red())

        embed.set_image(url=avatar_url)
        await self.message.edit(embed=embed, view=self)

        await interaction.response.defer()


# Replace with actual role IDs
SB_ROLES = [1276928831524966484, 1259918163005542410]
BANNER_ROLES = [1259932815810625699, 1276928831524966484]  # Roles allowed to use the commands
banner_ignore_id = 1259933150461562882  # Role that will be ignored for banner display

@bot.command(name="sb")
@commands.has_any_role(*SB_ROLES)
async def server_banner(ctx):
    if not ctx.guild.banner:
        #await ctx.reply("This server does not have a banner.")
        return
    else:
        webp = ctx.guild.banner.replace(format='webp')
        jpg = ctx.guild.banner.replace(format='jpg')
        png = ctx.guild.banner.replace(format='png')
        embed = discord.Embed(
            color=0xFF0000,
            description=f"[`PNG`]({png}) | [`JPG`]({jpg}) | [`WEBP`]({webp})"
            if not ctx.guild.banner.is_animated() else
            f"[`PNG`]({png}) | [`JPG`]({jpg}) | [`WEBP`]({webp}) | [`GIF`]({ctx.guild.banner.replace(format='gif')})"
        )
        embed.set_image(url=ctx.guild.banner)
        embed.set_author(name=ctx.guild.name,
                         icon_url=ctx.guild.icon.url
                         if ctx.guild.icon else ctx.guild.default_icon.url)
        embed.set_footer(
            text=f"Requested By {ctx.author}",
            icon_url=ctx.author.avatar.url
            if ctx.author.avatar else ctx.author.default_avatar.url)
        await ctx.reply(embed=embed)

@bot.command(name="banner")
@commands.has_any_role(*BANNER_ROLES)
@commands.cooldown(1, 2, commands.BucketType.user)
@commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
@commands.guild_only()
async def user_banner(ctx, member: Optional[Union[discord.Member, discord.User]] = None):
    if member is None:
        member = ctx.author
    
    # Fetch the user and check for banner
    bannerUser = await bot.fetch_user(member.id)
    
    # Check if the user has the ignore role
    if isinstance(member, discord.Member) and banner_ignore_id in [role.id for role in member.roles]:
        return

    if not bannerUser.banner:
        await ctx.reply(f"{member} does not have a banner.", delete_after=12)
    else:
        webp = bannerUser.banner.replace(format='webp')
        jpg = bannerUser.banner.replace(format='jpg')
        png = bannerUser.banner.replace(format='png')
        embed = discord.Embed(
            color=0xFF0000,
            description=f"[`PNG`]({png}) | [`JPG`]({jpg}) | [`WEBP`]({webp})"
            if not bannerUser.banner.is_animated() else
            f"[`PNG`]({png}) | [`JPG`]({jpg}) | [`WEBP`]({webp}) | [`GIF`]({bannerUser.banner.replace(format='gif')})"
        )
        embed.set_author(name=f"{member}",
                         icon_url=member.avatar.url
                         if member.avatar else member.default_avatar.url)
        embed.set_image(url=bannerUser.banner)
        embed.set_footer(
            text=f"Requested By {ctx.author}",
            icon_url=ctx.author.avatar.url
            if ctx.author.avatar else ctx.author.default_avatar.url)

        await ctx.reply(embed=embed)

# Error handler for missing roles
@server_banner.error
@user_banner.error
async def banner_error(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        #await ctx.reply("You don't have the required role to use this command.")
        return
    else:
        raise error

icon_allowed_roles_ids = [1259918163005542410, 1276928831524966484]  # Replace with the IDs of the required roles
icon_log_channel_id = 1259934096025718875  # Replace with your actual log channel ID

@bot.command(name="gi")
async def server_icon(ctx):
    if not any(role.id in icon_allowed_roles_ids for role in ctx.author.roles):
        return

    icon = ctx.guild.icon
    if icon:
        icon_url = icon.url  # Updated to use icon.url
        embed = discord.Embed(title=f"Icon of {ctx.guild.name}.", description="", color=discord.Color.red())
        embed.set_image(url=icon_url)
        await ctx.send(embed=embed)
    else:
        await ctx.send("This server doesn't have an icon.")

    # Log the command usage
    log_channel = bot.get_channel(icon_log_channel_id)
    if log_channel:
        log_message = f"{ctx.author} used the server_icon command at {datetime.datetime.utcnow()}."
        await log_channel.send(log_message)
    else:
        print("Log channel not found.")

import discord
import asyncio
import datetime
import pytz

# Constants
LINK_IMAGE_CHANNELS = [1259897041006628905, 234567890123456789, 345678901234567890]
IMAGE_ONLY_CHANNELS = [1263608468414271499, 1259897051467087985, 1259897050410254356, 1297612304325808212]
EXEMPT_ROLE_ID = 1275490817930166272
SPECIFIC_ROLES = [1259918163005542410, 1259918163005542410, 1259918163005542410, 1276928831524966484]
PIC_ALLOWED_USERS = [1074831330015191072, 987654321]  # Replace with specific user IDs allowed to trigger the "pic" role assignment
WHITELIST_IDS = [1080499576206798969, 1074831330015191072, 1088466341020827721]
LOG_CHANNEL_ID = 1263815985870143603
PIC_ROLE_ID = 1259899072714637344  # Replace with the role ID to be managed
PIC_ALLOWED_ROLE_ID = 1282303150232965200  # Replace with the allowed role ID
pakistan_timezone = pytz.timezone('Asia/Karachi')


AFK_ROLE_IDS = [1259932815810625699, 1276928831524966484]
afk_users = {}  # Track AFK users with reason and timestamp
notified_users = {}  # Track notified users to prevent multiple notifications

# Helper function to format timedelta
def format_timedelta(delta):
    seconds = delta.total_seconds()
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    formatted = []
    if days:
        formatted.append(f"{int(days)} days")
    if hours:
        formatted.append(f"{int(hours)} hours")
    if minutes:
        formatted.append(f"{int(minutes)} minutes")
    if seconds:
        formatted.append(f"{int(seconds)} seconds")
    return ', '.join(formatted)

class AFKRemoveView(discord.ui.View):
    def __init__(self, mentioned_by_links, afk_user):
        super().__init__()
        self.mentioned_by_links = mentioned_by_links
        self.afk_user = afk_user  # Store the AFK user who triggered the removal

    @discord.ui.button(label="View Mentions", style=discord.ButtonStyle.blurple)
    async def view_mentions_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if the user interacting with the button is the AFK user
        if interaction.user != self.afk_user:
            return await interaction.response.send_message("You can't view the mentions for this user.", ephemeral=True)
        
        mentions_list = [f"{user.mention}: [Jump to Message]({link})" for user, link in self.mentioned_by_links.items()]
        mention_message = "\n".join(mentions_list) if mentions_list else "No one mentioned you."
        await interaction.response.send_message(mention_message, ephemeral=True)

@bot.command()
async def afk(ctx, *, reason: str = 'No reason provided'):
    # Check if the user has any of the allowed roles
    if not any(role.id in AFK_ROLE_IDS for role in ctx.author.roles):
        return

    # Check if the user is already AFK
    if ctx.author in afk_users:
        await ctx.reply("You are already AFK.", delete_after=7)
        return

    # Check for invalid reasons
    if '@everyone' in reason or '@here' in reason or any(word.startswith(('http://', 'https://')) for word in reason.split()):
        return

    if any(word.startswith('<@&') for word in reason.split()) or any(word.startswith('<@') for word in reason.split()):
        return

    # Set the AFK status
    afk_users[ctx.author] = (reason, datetime.datetime.now())

    # Reset the notifications for this user in notified_users
    for user_id in notified_users:
        if ctx.author.id in notified_users[user_id]:
            notified_users[user_id].remove(ctx.author.id)

    embed = discord.Embed(title="AFK Set", description=f"Your AFK has been set with reason: {reason}", color=discord.Color.red())
    await ctx.reply(embed=embed)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    exempt_role = discord.utils.get(message.guild.roles, id=EXEMPT_ROLE_ID)

    # Check if the user has AFK status and remove it if they send a message
    if message.author in afk_users:
        afk_start_time = afk_users[message.author][1]
        afk_reason = afk_users[message.author][0]
        del afk_users[message.author]  # Remove AFK status
        afk_duration = datetime.datetime.now() - afk_start_time
        afk_removed_message = f"***Your AFK status has been removed. You were AFK for*** ****__: {format_timedelta(afk_duration)}__****"

        mentioned_by_links = {}
        async for msg in message.channel.history(limit=50):
            if msg.author.bot:
                continue
            for user in msg.mentions:
                if user == message.author and msg.author != message.author:
                    mentioned_by_links[msg.author] = msg.jump_url
        
        view = AFKRemoveView(mentioned_by_links, message.author)
        await message.reply(afk_removed_message, view=view, delete_after=15)

    mentioned_afk_users = [user for user in message.mentions if user in afk_users]
    for afk_user in mentioned_afk_users:
        if afk_user.id not in notified_users.get(message.author.id, []):
            afk_reason, afk_time = afk_users[afk_user]
            afk_duration = datetime.datetime.now() - afk_time
            reply_message = f'****__{afk_user.name} is AFK with reason: {afk_reason} (AFK Duration: {format_timedelta(afk_duration)})__****'
            await message.reply(reply_message)
            notified_users.setdefault(message.author.id, []).append(afk_user.id)

    if exempt_role not in message.author.roles:
        if message.channel.id in LINK_IMAGE_CHANNELS:
            if not (message.attachments or "http://" in message.content or "https://" in message.content):
                await message.delete()
                return

        if message.channel.id in IMAGE_ONLY_CHANNELS:
            if not message.attachments:
                await message.delete()
                return

    if any(role.id in SPECIFIC_ROLES for role in message.author.roles):
        if 'vanity' in message.content.lower():
            res_msg = await message.channel.send("𝘞𝘢𝘯𝘵 𝘙𝘰𝘭𝘦𝘴?𝘗𝘶𝘵 𝘷𝘢𝘯𝘪𝘵𝘺 𝘪𝘯 𝘺𝘰𝘶𝘳 𝘈𝘣𝘰𝘶𝘵 https://discord.gg/sinner")
            await asyncio.sleep(13)
            await res_msg.delete()
        elif 'tag' in message.content.lower():
            res_msg = await message.channel.send(f" ! 〆(name) ˢᶦⁿⁿᵉʳˢ")
            await asyncio.sleep(13)
            await res_msg.delete()
        elif 'staff' in message.content.lower():
            res_msg = await message.channel.send("***Apply for Staff Reqs vanity must***")
            await asyncio.sleep(13)
            await res_msg.delete()
        elif 'mc' in message.content.lower():
            guild = message.guild
            member_count = guild.member_count
            emoji = '<a:red_batimentos:1260717998415810715>'
            res_msg = await message.channel.send(f'{emoji} 𝐌𝐞𝐦𝐛𝐞𝐫𝐬 {member_count} {emoji}')
            await asyncio.sleep(13)
            await res_msg.delete()

    await bot.process_commands(message)

sniped_messages = {}

@bot.event
async def on_raw_message_delete(payload):
    channel_id = payload.channel_id
    guild = bot.get_guild(payload.guild_id)
    channel = guild.get_channel(channel_id)

    if channel:
        # Fetch the message if it's not cached
        if payload.cached_message:
            message = payload.cached_message
        else:
            try:
                message = await channel.fetch_message(payload.message_id)
            except discord.NotFound:
                # The message was not found (e.g., it may have been deleted by another process)
                return
            except discord.Forbidden:
                # The bot does not have permission to fetch the message
                return

        if message and not message.author.bot:  # Ignore bot messages
            if len(sniped_messages.get(channel_id, [])) < 5:  # Limit to 5 messages
                sniped_messages.setdefault(channel_id, []).append((message.author, message.content))
            else:
                sniped_messages[channel_id].pop(0)  # Remove the oldest message
                sniped_messages[channel_id].append((message.author, message.content))

class SnipeView(View):
    def __init__(self, messages, initial_index, author_id):
        super().__init__(timeout=60)
        self.messages = messages
        self.current_index = initial_index
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.author_id

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.primary, custom_id="snipe:prev")
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_index > 0:
            self.current_index -= 1
            await self.update_message(interaction.message)

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.primary, custom_id="snipe:next")
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_index < len(self.messages) - 1:
            self.current_index += 1
            await self.update_message(interaction.message)

    async def update_message(self, message):
        embed = discord.Embed(
            title="Sniped Messages",
            description=f"Message {self.current_index + 1} of {len(self.messages)}",
            color=discord.Color.red()
        )
        author, content = self.messages[self.current_index]
        embed.add_field(
            name=f"**Author:** {author.display_name}",
            value=f"**Content:** {content}",
            inline=False
        )
        await message.edit(embed=embed)

@bot.command(name="snipe")
async def snipe(ctx):
    snipe_ids = [1259918163005542410, 1276928831524966484]  # Replace with the IDs of the roles
    user_roles = [discord.utils.get(ctx.guild.roles, id=role_id) for role_id in snipe_ids]

    if not any(role in ctx.author.roles for role in user_roles):
        # The user does not have any of the required roles, no message is sent
        return

    channel_id = ctx.channel.id
    if channel_id in sniped_messages and sniped_messages[channel_id]:
        messages = sniped_messages[channel_id]
        initial_index = len(messages) - 1

        embed = discord.Embed(
            title="Sniped Messages",
            description=f"Message {initial_index + 1} of {len(messages)}",
            color=discord.Color.red()
        )
        author, content = messages[initial_index]
        embed.add_field(
            name=f"**Author:** {author.display_name}",
            value=f"**Content:** {content}",
            inline=False
        )

        view = SnipeView(messages, initial_index, ctx.author.id)
        await ctx.send(embed=embed, view=view)

@bot.command(name="su")
async def snipe_user(ctx, user: discord.User):
    allowed_users = [1074831330015191072, 1088466341020827721]  # Replace with the user IDs of those allowed to use the command
    
    if ctx.author.id not in allowed_users:
        return await ctx.send("")

    channel_id = ctx.channel.id
    if channel_id in sniped_messages and sniped_messages[channel_id]:
        messages = [(author, content) for author, content in sniped_messages[channel_id] if author == user]

        if not messages:
            return await ctx.send(f"No recent deleted messages found for {user.display_name}.")

        current_index = len(messages) - 1

        embed = discord.Embed(
            title=f"Sniped Messages from {user.display_name}",
            description=f"Message {current_index + 1} of {len(messages)}",
            color=discord.Color.red()
        )
        author, content = messages[current_index]
        embed.add_field(
            name=f"**Author:** {author.display_name}",
            value=f"**Content:** {content}",
            inline=False
        )

        message = await ctx.send(embed=embed)
        if len(messages) > 1:
            await message.add_reaction("⬅️")  # Add reaction to navigate backwards
            await message.add_reaction("➡️")  # Add reaction to navigate forwards

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡️"] and reaction.message.id == message.id

            while True:
                try:
                    reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
                except asyncio.TimeoutError:
                    await message.clear_reactions()
                    break

                if str(reaction.emoji) == "⬅️":
                    current_index = max(0, current_index - 1)
                elif str(reaction.emoji) == "➡️":
                    current_index = min(len(messages) - 1, current_index + 1)

                embed = discord.Embed(
                    title=f"Sniped Messages from {user.display_name}",
                    description=f"Message {current_index + 1} of {len(messages)}",
                    color=discord.Color.red()
                )
                author, content = messages[current_index]
                embed.add_field(
                    name=f"**Author:** {author.display_name}",
                    value=f"**Content:** {content}",
                    inline=False
                )
                await message.edit(embed=embed)
                await reaction.remove(user)
    else:
        await ctx.send("There are no recent deleted messages from that user.")

# Replace with your bot's token and role IDs
PURGE_ROLE_IDS = [1259918163005542410, 1276928831524966484]

# Modal for bot message purge
class BotsPurgeModal(Modal):
    def __init__(self):
        super().__init__(title="Purge Bot Msgs")  # Shortened title
        self.limit_input = TextInput(label="Number of bot messages (max 50):", max_length=2)  # Shortened label
        self.add_item(self.limit_input)

    async def on_submit(self, interaction):
        try:
            limit = int(self.limit_input.value)
            if limit <= 0 or limit > 50:
                await interaction.response.send_message("Limit must be between 1 and 50.", ephemeral=True)
                return

            # Purge bot messages
            deleted_messages = await interaction.channel.purge(limit=limit, check=lambda m: m.author.bot)
            await interaction.response.send_message(f"Deleted {len(deleted_messages)} bot messages.", delete_after=4)
        except ValueError:
            await interaction.response.send_message("Please enter a valid number.", ephemeral=True)

# Modal for user message purge
class UserPurgeModal(Modal):
    def __init__(self):
        super().__init__(title="Purge User Msgs")  # Shortened title
        self.user_id_input = TextInput(label="Enter the user ID:", max_length=19)
        self.limit_input = TextInput(label="Number of messages (max 50):", max_length=2)  # Shortened label
        self.add_item(self.user_id_input)
        self.add_item(self.limit_input)

    async def on_submit(self, interaction):
        try:
            user_id = int(self.user_id_input.value)
            limit = int(self.limit_input.value)

            if limit <= 0 or limit > 50:
                await interaction.response.send_message("Limit must be between 1 and 50.", ephemeral=True)
                return

            user = interaction.guild.get_member(user_id)
            if user is None:
                await interaction.response.send_message("Invalid user ID.", ephemeral=True)
                return

            # Purge user messages
            deleted_messages = await interaction.channel.purge(limit=limit, check=lambda m: m.author == user)
            await interaction.response.send_message(f"Deleted {len(deleted_messages)} messages from that user.", delete_after=4)
        except ValueError:
            await interaction.response.send_message("Invalid input.", ephemeral=True)

# Modal for purging all messages
class AllPurgeModal(Modal):
    def __init__(self):
        super().__init__(title="Purge All Msgs")  # Shortened title
        self.limit_input = TextInput(label="Number of messages (max 50):", max_length=2)  # Shortened label
        self.add_item(self.limit_input)

    async def on_submit(self, interaction):
        try:
            limit = int(self.limit_input.value)
            if limit <= 0 or limit > 50:
                await interaction.response.send_message("Limit must be between 1 and 50.", ephemeral=True)
                return

            # Purge all messages
            deleted_messages = await interaction.channel.purge(limit=limit)
            await interaction.response.send_message(f"Deleted {len(deleted_messages)} messages.", delete_after=4)
        except ValueError:
            await interaction.response.send_message("Please enter a valid number.", ephemeral=True)

@bot.command(name='purge')
async def purge(ctx):
    # Check if the author has any of the required roles
    has_role = any(ctx.guild.get_role(role_id) in ctx.author.roles for role_id in PURGE_ROLE_IDS)
    
    if not has_role:
        return

    # Create the buttons with shorter labels
    bots_button = Button(label="Bot Msgs", style=discord.ButtonStyle.primary)  # Shortened label
    user_button = Button(label="User Msgs", style=discord.ButtonStyle.secondary)  # Shortened label
    all_button = Button(label="All Msgs", style=discord.ButtonStyle.danger)  # Shortened label

    # Create a view and add buttons
    view = View()
    view.add_item(bots_button)
    view.add_item(user_button)
    view.add_item(all_button)

    embed = discord.Embed(
        title="Purge Options",
        description="Choose an option to delete messages.",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=view, delete_after=25)

    # Define button callbacks
    async def bots_callback(interaction):
        if interaction.user == ctx.author:
            await interaction.response.send_modal(BotsPurgeModal())
        else:
            await interaction.response.send_message("You are not allowed to use this button.", ephemeral=True)

    async def user_callback(interaction):
        if interaction.user == ctx.author:
            await interaction.response.send_modal(UserPurgeModal())
        else:
            await interaction.response.send_message("You are not allowed to use this button.", ephemeral=True)

    async def all_callback(interaction):
        if interaction.user == ctx.author:
            await interaction.response.send_modal(AllPurgeModal())
        else:
            await interaction.response.send_message("You are not allowed to use this button.", ephemeral=True)

    # Assign callbacks to buttons
    bots_button.callback = bots_callback
    user_button.callback = user_callback
    all_button.callback = all_callback

@bot.event
async def on_reaction_remove(reaction, user):
    await bot.wait_until_ready()
    
    if user == bot.user:  # Ignore reactions removed by the bot
        return
    
    log_channel_id = 1263815985870143603  # Replace with the ID of the log channel
    log_channel = bot.get_channel(log_channel_id)
    
    if log_channel is None:
        print("Log channel not found.")
        return
    
    message_author = reaction.message.author
    channel = reaction.message.channel
    message_link = f"https://discord.com/channels/{reaction.message.guild.id}/{channel.id}/{reaction.message.id}"
    
    embed = discord.Embed(
        title="Reaction Removed",
        description=f"{user.mention} removed their reaction {reaction.emoji} from a message in {channel.mention}",
        color=discord.Color.red()
    )
    embed.add_field(name="Message Author", value=message_author.mention, inline=True)
    embed.add_field(name="Channel", value=channel.mention, inline=True)
    embed.add_field(name="Message Link", value=f"[Jump to message]({message_link})", inline=False)
    
    try:
        await log_channel.send(embed=embed)
    except Exception as e:
        print(f"Error sending log message: {e}")

# Replace these with actual IDs from your server
REQUIRED_ROLE_ID = 1259935683791818753  # Role required to use the mute/unmute commands
WL_ROLE_ID = 1273976123163672576  # Whitelist role that might bypass the mute
BYPASS_USER_IDS = {1074831330015191072, 1088466341020827721}  # Users allowed to bypass whitelist role check
MUTED_ROLE_ID = 1259935501214027827  # Muted role ID
LOG_CHANNEL_ID = 1259936298492366890  # Log channel ID

muted_members = set()

async def log_mute_unmute(author, member, reason, action):
    channel = bot.get_channel(LOG_CHANNEL_ID)
    embed = discord.Embed(title=f"Member {action}", color=discord.Color.red() if action == "Muted" else discord.Color.green())
    embed.add_field(name="Member", value=member.mention, inline=False)
    embed.add_field(name=f"{action} By", value=author.mention, inline=False)
    if reason:
        embed.add_field(name="Reason", value=reason, inline=False)
    await channel.send(embed=embed)

# Dictionary to keep track of removed roles during muting
removed_roles = {}

# Function to parse duration into seconds
def parse_duration(duration: str):
    # Add your implementation to convert duration string into seconds
    # e.g., "10m" to 600 seconds, "2h" to 7200 seconds, etc.
    if duration[-1] == 's':
        return int(duration[:-1])
    elif duration[-1] == 'm':
        return int(duration[:-1]) * 60
    elif duration[-1] == 'h':
        return int(duration[:-1]) * 3600
    elif duration[-1] == 'd':
        return int(duration[:-1]) * 86400
    return 0  # Default to 0 seconds for invalid format

@bot.command()
async def mute(ctx, member: discord.Member, duration: str = None, *, reason: str = None):
    author_roles_ids = [role.id for role in ctx.author.roles]
    
    # Check if the author has the required role to mute members
    if REQUIRED_ROLE_ID not in author_roles_ids:
        return

    if member.bot:
        return

    whitelist_role_ids = [role.id for role in member.roles]
    
    # Check if the member has the whitelist role
    if WL_ROLE_ID in whitelist_role_ids:
        if ctx.author.id not in BYPASS_USER_IDS:
            return

    # If the member has the Admin role, remove it before muting
    admin_role = discord.utils.get(ctx.guild.roles, id=1260193783484514434)
    removed_roles[member.id] = []

    if admin_role and admin_role in member.roles:
        try:
            await member.remove_roles(admin_role, reason=f"Admin role removed by {ctx.author.name} before muting.")
            removed_roles[member.id].append(admin_role)
        except discord.Forbidden:
            await ctx.send("I do not have permission to remove the Admin role.", delete_after=5)
            return

    muted_role = discord.utils.get(ctx.guild.roles, id=MUTED_ROLE_ID)
    if muted_role:
        # Create a confirmation view
        confirm_button = Button(label="Confirm", style=discord.ButtonStyle.red)
        cancel_button = Button(label="Cancel", style=discord.ButtonStyle.green)

        async def confirm_callback(interaction):
            reason_with_author = f"{ctx.author.name} muted this user - Reason: {reason if reason else 'No reason provided.'}"
            await member.add_roles(muted_role, reason=reason_with_author)
            muted_members.add(member.id)
            await log_mute_unmute(ctx.author, member, reason, "Muted")

            embed = discord.Embed(title="Member Muted", color=discord.Color.red())
            embed.add_field(name="Member", value=member.mention, inline=False)
            embed.add_field(name="Muted By", value=ctx.author.mention, inline=False)
            if reason:
                embed.add_field(name="Reason", value=reason, inline=False)

            message = await ctx.send(embed=embed)
            await asyncio.sleep(9)
            await message.delete()

            # Unmute after duration if specified
            if duration:
                total_seconds = parse_duration(duration)
                if total_seconds > 0:  # Only wait if the duration is valid
                    await asyncio.sleep(total_seconds)
                    await unmute_member(member, ctx.author, reason)
                else:
                    return
            else:
                await ctx.send(f"{member.mention} has been muted indefinitely.", delete_after=7)

        async def cancel_callback(interaction):
            await ctx.send("Mute action cancelled.", delete_after=5)

        confirm_button.callback = confirm_callback
        cancel_button.callback = cancel_callback

        view = View()
        view.add_item(confirm_button)
        view.add_item(cancel_button)
        await ctx.send("Are you sure you want to mute this member?", view=view)
    else:
        await ctx.send("Muted role not found.", delete_after=3)

async def unmute_member(member, moderator, reason):
    muted_role = discord.utils.get(member.guild.roles, id=MUTED_ROLE_ID)
    if muted_role and muted_role in member.roles:
        reason_with_author = f"{moderator.name} unmuted this user - Reason: {reason}"
        await member.remove_roles(muted_role, reason=reason_with_author)
        muted_members.discard(member.id)
        await log_mute_unmute(moderator, member, reason, "Unmuted")

        # Restore any roles that were removed during muting
        if member.id in removed_roles:
            for role in removed_roles[member.id]:
                await member.add_roles(role, reason=f"Admin role restored by {moderator.name} after unmuting.")
            del removed_roles[member.id]  # Clean up after restoration

        embed = discord.Embed(title="Member Unmuted", color=discord.Color.green())
        embed.add_field(name="Member", value=member.mention, inline=False)
        embed.add_field(name="Unmuted By", value=moderator.mention, inline=False)
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)

        message = await member.send(embed=embed)
        await asyncio.sleep(9)
        await message.delete()

@bot.command()
async def unmute(ctx, member: discord.Member, *, reason: str = None):
    author_roles_ids = [role.id for role in ctx.author.roles]
    if REQUIRED_ROLE_ID not in author_roles_ids:
        return

    whitelist_role_ids = [role.id for role in member.roles]
    if WL_ROLE_ID in whitelist_role_ids and ctx.author.id not in BYPASS_USER_IDS:
        return

    muted_role = discord.utils.get(ctx.guild.roles, id=MUTED_ROLE_ID)
    if muted_role and muted_role in member.roles:
        reason_with_author = f"{ctx.author.name} unmuted this user - Reason: {reason}"
        await member.remove_roles(muted_role, reason=reason_with_author)
        muted_members.discard(member.id)
        await log_mute_unmute(ctx.author, member, reason, "Unmuted")

        # Restore any roles that were removed during muting
        if member.id in removed_roles:
            for role in removed_roles[member.id]:
                await member.add_roles(role, reason=f"Admin role restored by {ctx.author.name} after unmuting.")
            del removed_roles[member.id]  # Clean up after restoration

        embed = discord.Embed(title="Member Unmuted", color=discord.Color.green())
        embed.add_field(name="Member", value=member.mention, inline=False)
        embed.add_field(name="Unmuted By", value=ctx.author.mention, inline=False)
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)

        message = await ctx.send(embed=embed)
        await asyncio.sleep(9)
        await message.delete()
    else:
        await ctx.send(f"{member.mention} is not muted.", delete_after=3)

@bot.event
async def on_member_join(member):
    # Welcome messages
    welcome_data = {
        1259897038376669276: f'***{member.mention} Read Rules***',
        1259897039483965540: f'***{member.mention} Take Self Roles***',
        1259897043544182865: f'**{member.mention} Check it!!**'
    }

    for channel_id, message in welcome_data.items():
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(message, delete_after=4)
        else:
            print(f'Channel with ID {channel_id} not found')

    # Apply muted role if member is in muted_members
    if member.id in muted_members:
        muted_role = discord.utils.get(member.guild.roles, id=MUTED_ROLE_ID)
        if muted_role:
            await member.add_roles(muted_role, reason="Reapplying mute role on rejoin")

conn_roles_perms = sqlite3.connect('roles_permissions.db')
c_roles_perms = conn_roles_perms.cursor()

c_roles_perms.execute('''CREATE TABLE IF NOT EXISTS allowed_ids (
                       user_id INTEGER PRIMARY KEY
                       )''')

# Define the role IDs you want to grant
ROLE_ID_1 = 1259932815810625699
ROLE_ID_2 = 1281297260663279650
ROLE_ID_3 = 1260168414425776211
ROLE_ID_4 = 1280985037860507758
ROLE_ID_5 = 1263924901639885022
ROLE_ID_6 = 1280876597863387167
ROLE_ID_7 = 1259899072714637344

RP_ALLOWED_USERS = [1074831330015191072, 1088466341020827721]  # List of allowed user IDs for rp command
LOG_CHANNEL_ID = 1259936298492366890  # Replace this with the ID of the log channel

# Function to check if user ID is in the database
def is_allowed_id(user_id):
    c_roles_perms.execute("SELECT 1 FROM allowed_ids WHERE user_id=?", (user_id,))
    return c_roles_perms.fetchone() is not None

@bot.command(name="vr")
async def grant_roles(ctx, member: discord.Member):
    # Check if the member is allowed to use the command
    if not is_allowed_id(ctx.author.id):
        return

    # Get the guild object
    guild = ctx.guild

    # Get the role objects
    roles = [guild.get_role(role_id) for role_id in [ROLE_ID_1, ROLE_ID_2, ROLE_ID_3, ROLE_ID_4, ROLE_ID_5, ROLE_ID_6, ROLE_ID_7]]

    # Grant roles to the member
    if all(roles):
        await member.add_roles(*roles, reason=f"Add by {ctx.author.name}")
        message = await ctx.send(f"Roles granted to {member.mention}: {', '.join(role.name for role in roles)}")
        await asyncio.sleep(4)
        await message.delete()

        # Log the role granting
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(title="Roles Granted", color=discord.Color.green())
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
            embed.add_field(name="Member", value=member.mention, inline=False)
            embed.add_field(name="Roles", value=', '.join(role.name for role in roles), inline=False)
            await log_channel.send(embed=embed)
    else:
        message = await ctx.send("One or more roles not found. Make sure the role IDs are correct.")
        await asyncio.sleep(4)
        await message.delete()

@bot.command(name="vrr")
async def remove_roles(ctx, member: discord.Member):
    # Check if the member is allowed to use the command
    if not is_allowed_id(ctx.author.id):
        return

    # Get the guild object
    guild = ctx.guild

    # Get the role objects
    roles = [guild.get_role(role_id) for role_id in [ROLE_ID_1, ROLE_ID_2, ROLE_ID_3, ROLE_ID_4, ROLE_ID_5, ROLE_ID_6, ROLE_ID_7]]

    # Remove roles from the member
    if all(roles):
        await member.remove_roles(*roles, reason=f"Take by {ctx.author.name}")
        message = await ctx.send(f"Roles removed from {member.mention}: {', '.join(role.name for role in roles)}")
        await asyncio.sleep(4)
        await message.delete()

        # Log the role removal
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(title="Roles Removed", color=discord.Color.red())
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
            embed.add_field(name="Member", value=member.mention, inline=False)
            embed.add_field(name="Roles", value=', '.join(role.name for role in roles), inline=False)
            await log_channel.send(embed=embed)
    else:
        await ctx.send("One or more roles not found. Make sure the role IDs are correct.")

@bot.command(name="vrp")
async def add_allowed_id(ctx, member: discord.Member):
    # Check if the user invoking the command is in the allowed users list for rp command
    if ctx.author.id not in RP_ALLOWED_USERS:
        return

    # Extract user
    await add_allowed_id(member.id)
    message = await ctx.send(f"{member.mention} Khush huja vanity roles cmd use kar paye ga  mikey ko abu bol")
    await asyncio.sleep(4)
    await message.delete()

@bot.command(name="vrrp")
async def remove_allowed_member_cmd(ctx, member: discord.Member):
    # Check if the user invoking the command is in the allowed users list for rrp command
    if ctx.author.id not in RP_ALLOWED_USERS:
        return

    # Remove the member from the allowed users list for role permissions
    await remove_allowed_id(member.id)
    message = await ctx.send(f"{member.mention} Chal bete shakal ghum kr")
    await asyncio.sleep(4)
    await message.delete()

vprl_log_id = 1259936298492366890  # Replace with your actual log channel ID

@bot.command(name="vrpl")
async def vrpl(ctx):
    """Remove all user IDs from the allowed roles list and log the action."""
    # Check if the user invoking the command is in the allowed users list for this command
    if ctx.author.id not in RP_ALLOWED_USERS:
        await ctx.send("You are not authorized to use this command.")
        return

    log_channel = bot.get_channel(1259936298492366890)  # Get the log channel

    try:
        # Clear the allowed role IDs from the database
        c_roles_perms.execute("DELETE FROM allowed_ids")  # Delete all entries
        conn_roles_perms.commit()  # Commit the changes

        # Confirmation message
        await ctx.send("Fuck hogaye sab", delete_after=7)

        # Log the action in the specified log channel
        if log_channel:
            log_embed = discord.Embed(
                title="Allowed Roles Cleared",
                description=f"All user IDs have been removed from the allowed roles list by {ctx.author.mention}.",
                color=discord.Color.red()
            )
            log_embed.add_field(name="Moderator", value=ctx.author.name, inline=True)
            log_embed.add_field(name="User ID", value=ctx.author.id, inline=True)
            log_embed.set_footer(text=f"Command invoked in: {ctx.channel.name}")
            await log_channel.send(embed=log_embed)

    except sqlite3.Error as e:  # Catching specific SQLite errors
        print(f"Error clearing allowed role IDs: {e}")
        await ctx.send("An error occurred while trying to clear the allowed roles list.")

    except Exception as e:  # Catching general exceptions
        print(f"Unexpected error: {e}")
        await ctx.send("An unexpected error occurred.")


async def add_allowed_id(user_id):
    c_roles_perms.execute("INSERT INTO allowed_ids (user_id) VALUES (?)", (user_id,))
    conn_roles_perms.commit()

async def remove_allowed_id(user_id):
    c_roles_perms.execute("DELETE FROM allowed_ids WHERE user_id=?", (user_id,))
    conn_roles_perms.commit()

conn_role_perms = sqlite3.connect('role_permissions.db')
c_role_perms = conn_role_perms.cursor()

c_role_perms.execute('''CREATE TABLE IF NOT EXISTS allowed_ids (
                       user_id INTEGER PRIMARY KEY
                       )''')

async def add_allowed_role_id(user_id):
    if not is_allowed_role_id(user_id):
        c_role_perms.execute("INSERT INTO allowed_ids (user_id) VALUES (?)", (user_id,))
        conn_role_perms.commit()
        # Log the addition of the user ID
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            user = await bot.fetch_user(user_id)
            if user:
                embed = discord.Embed(title="Allowed ID Granted", color=discord.Color.green())
                embed.add_field(name="User", value=user.mention, inline=False)
                await log_channel.send(embed=embed)
    else:
        print("User ID already exists in allowed IDs.")


# Function to remove user ID from the database
'''def remove_allowed_role_id(user_id):
    c_role_perms.execute("DELETE FROM allowed_ids WHERE user_id=?", (user_id,))
    conn_role_perms.commit()
    # Log the removal of the user ID
    asyncio.create_task(log_removed_id(user_id))'''

# Function to check if user ID is in the database
def is_allowed_role_id(user_id):
    c_role_perms.execute("SELECT 1 FROM allowed_ids WHERE user_id=?", (user_id,))
    return c_role_perms.fetchone() is not None


# Define the role IDs you want to grant
ROLE_ID = 1260182004129988618

RP_ALLOWED_USERS = [1074831330015191072, 1088466341020827721]  # List of allowed user IDs for rp comma
GIRL_LOG_ID = 1259936298492366890  # Replace this with the ID of the log channel

@bot.command(name="g")
async def grant_roles(ctx, member: discord.Member):

    if not is_allowed_role_id(ctx.author.id):
#        await ctx.send("You are not allowed to use this command.")
        return

    # Get the guild object
    guild = ctx.guild

    # Get the role object you want to grant
    role = guild.get_role(ROLE_ID)  # Change ROLE_ID_1 to the desired role ID

    # Grant the role to the member
    if role:
        await member.add_roles(role)
        message = await ctx.send(f"Role granted to {member.mention}: {role.name}")
        await asyncio.sleep(4)
        await message.delete()

        # Log the role granting
        log_channel = bot.get_channel(GIRL_LOG_ID)
        if log_channel:
            embed = discord.Embed(title="Role Granted", color=discord.Color.green())
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
            embed.add_field(name="Member", value=member.mention, inline=False)
            embed.add_field(name="Role", value=role.name, inline=False)
            await log_channel.send(embed=embed)
    else:
        await ctx.send("The role was not found. Make sure the role ID is correct.")


@bot.command(name="gr")
async def remove_roles(ctx, member: discord.Member):

    if not is_allowed_role_id(ctx.author.id):
        return

    # Get the guild object
    guild = ctx.guild

    # Get the role objects
    role = guild.get_role(ROLE_ID)

    # Remove roles from the member
    if role:
        await member.remove_roles(role)
        message = await ctx.send(f"Roles removed from {member.mention}: {role.name}")
        await asyncio.sleep(4)
        await message.delete()

        # Log the role removal
        log_channel = bot.get_channel(GIRL_LOG_ID)
        if log_channel:
            embed = discord.Embed(title="Roles Removed", color=discord.Color.red())
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
            embed.add_field(name="Member", value=member.mention, inline=False)
            embed.add_field(name="Roles", value=f"{role.name}, {role2.name}, {role3.name}", inline=False)
            await log_channel.send(embed=embed)
    else:
        await ctx.send("One or more roles not found. Make sure the role IDs are correct.")


@bot.command(name="grl")
async def allowed_role_ids(ctx):
    # Check if the user invoking the command is in the allowed users list for rrp command
    if ctx.author.id not in RP_ALLOWED_USERS:
        return

    # Get the list of allowed user IDs for role permissions
    c_role_perms.execute("SELECT user_id FROM allowed_ids")
    allowed_user_ids = [row[0] for row in c_role_perms.fetchall()]

    # Fetch user information and format into embed
    embed = discord.Embed(title="Girl Cmd User IDs", color=discord.Color.green())
    for user_id in allowed_user_ids:
        user = await bot.fetch_user(user_id)
        if user:
            embed.add_field(name=user.name, value=f"ID: {user_id}", inline=False)

    # Send the embed
    await ctx.send(embed=embed)

@bot.command(name="gp")
async def add_allowed_role_id_cmd(ctx, member: discord.Member):
    # Check if the user invoking the command is in the allowed users list for rp command
    if ctx.author.id not in RP_ALLOWED_USERS:
        return

    # Extract user ID from mentioned member
    user_id = member.id

    # Add the user ID to the allowed users list for role permissions
    await add_allowed_role_id(user_id)

    log_channel = bot.get_channel(GIRL_LOG_ID)
    if log_channel:
        embed = discord.Embed(title="Allowed ID Granted", color=discord.Color.green())
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
        embed.add_field(name="Member", value=member.mention, inline=False)
        await log_channel.send(embed=embed)

    message = await ctx.send(f"{member.mention} chal bete khush huja girl role cmd mil gayi mikey ko abu bol")
    await asyncio.sleep(4)
    await message.delete()

@bot.command(name="grp")
async def remove_allowed_member_cmd(ctx, member: discord.Member):
    # Check if the user invoking the command is in the allowed users list for rrp command
    if ctx.author.id not in RP_ALLOWED_USERS:
        await ctx.send("You are not authorized to use this command.")
        return

    # Attempt to remove the member from the allowed users list for role permissions
    try:
        remove_allowed_role_id(member.id)  # Assuming this function exists and works as intended

        # Log the removal of member from the allowed users list
        log_channel = bot.get_channel(GIRL_LOG_ID)
        if log_channel:
            embed = discord.Embed(title="Allowed ID Removed", color=discord.Color.red())
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
            embed.add_field(name="Member", value=member.mention, inline=False)
            await log_channel.send(embed=embed)

        # Send a confirmation message to the command invoker
        message = await ctx.send(f"{member.mention} chal bro shakal ghum kar.")
        await asyncio.sleep(4)
        await message.delete()  # Delete the message after a short delay

    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

def remove_allowed_role_id(user_id):
    try:
        # Assuming you have established a connection to the database
        c_role_perms.execute("DELETE FROM allowed_ids WHERE user_id = ?", (user_id,))
        conn_role_perms.commit()
        print(f"User ID {user_id} removed from allowed role IDs.")
    except sqlite3.Error as e:
        print(f"Error removing allowed role ID: {e}")


ALLOWED_ROLE_IDS = [1260193783484514434, 1276928831524966484]  # Replace with your role IDs

# Specific user ID to ignore
IGNORED_USER_ID = 1074831330015191072  # Replace with the user ID to ignore

# Channel IDs for logging
NICK_CHANNEL_ID = 1259936298492366890  # Replace with your channel ID
WARN_CHANNEL_ID = 1259936298492366890  # Replace with your channel ID

@bot.command(name="nick")
async def changenick(ctx, member: discord.Member, *, new_nickname: str = None):
    # Check if the user has any of the allowed roles
    if any(role.id in ALLOWED_ROLE_IDS for role in ctx.author.roles):
        if new_nickname is None:
            await member.edit(nick=None, reason=f"Remove by {ctx.author}")
            embed = discord.Embed(description=f'Nickname of {member.mention} has been removed.', color=discord.Color.red())
        else:
            await member.edit(nick=new_nickname, reason=f"Change by {ctx.author}")
            embed = discord.Embed(description=f'Nickname of {member.mention} has been changed to {new_nickname}', color=discord.Color.red())
        
        message = await ctx.send(embed=embed)
        await asyncio.sleep(5)  # Wait for 5 seconds
        await ctx.message.delete()
        await message.delete()

        # Log the nickname change
        log_channel = bot.get_channel(NICK_CHANNEL_ID)
        log_embed = discord.Embed(title="Nickname Change Log", color=discord.Color.red())
        log_embed.add_field(name="User", value=member.mention)
        log_embed.add_field(name="Changed By", value=ctx.author.mention)
        log_embed.add_field(name="New Nickname", value=new_nickname if new_nickname else "None")
        await log_channel.send(embed=log_embed)
    else:
        return

@bot.command()
async def warn(ctx, user: discord.Member, *, reason: str):
    # Check if the user has any of the allowed roles
    if any(role.id in ALLOWED_ROLE_IDS for role in ctx.author.roles):
        # Check if the user is not the specified user to ignore
        if user.id != IGNORED_USER_ID:
            # Send warn message to the user
            try:
                warn_embed = discord.Embed(
                    title="You have been warned!",
                    description=f'You have been warned in **{ctx.guild.name}** for the following reason:\n{reason}',
                    color=discord.Color.red()
                )
                await user.send(embed=warn_embed)
            except discord.HTTPException:
                fail_message = await ctx.send("Failed to send warning message to the user.")
                await asyncio.sleep(5)
                await fail_message.delete()

            # Notify the moderator about the warn
            mod_embed = discord.Embed(
                description=f'{user.mention} has been warned for:\n{reason}',
                color=discord.Color.red()
            )
            mod_message = await ctx.send(embed=mod_embed)

            # Log the warn action
            log_channel = bot.get_channel(WARN_CHANNEL_ID)
            if log_channel:
                log_embed = discord.Embed(
                    title="Warn Log",
                    color=discord.Color.red()
                )
                log_embed.add_field(name="User Warned", value=user.mention, inline=False)
                log_embed.add_field(name="Warned By", value=ctx.author.mention, inline=False)
                log_embed.add_field(name="Reason", value=reason, inline=False)
                log_message = await log_channel.send(embed=log_embed)

                # Delete all messages after 5 seconds
                await asyncio.sleep(5)
                await ctx.message.delete()
                await mod_message.delete()
        else:
            return
    else:
        return

# Replace with your role ID and user ID to ignore
R = 1271062224374464603
Ui = 1074831330015191072

# Replace with your log channel ID
L_ID = 1259934096025718875

@bot.command(name="ben")
async def fakeban(ctx, member: discord.Member, *, reason=None):
    await ctx.message.delete()
    # Check if the command user has the allowed role or is the ignored user
    if R not in [role.id for role in ctx.author.roles] and ctx.author.id != Ui:
        return
    
    # Check if the target user is the ignored user
    if member.id == Ui:
        return

    # Create an embed for the fake ban message
    embed = discord.Embed(title="YE SINNERS HA TERA GHAR NAHI", color=discord.Color.red())
    embed.add_field(name="User", value=member.mention, inline=False)
    embed.add_field(name="WJA KIA BANI", value=reason if reason else "No reason provided", inline=False)
    embed.set_footer(text="Niklo kahin aur ja ke rr kro")

    # Send the embed to the channel
    message = await ctx.send(embed=embed)
    await message.delete(delay=8)

    # Optionally, send a DM to the banned user (if desired)
    try:
        await member.send(f"Maa chud gayi teri Is Server ma {ctx.guild.name}. Reason: {reason if reason else 'No reason provided.'}")
    except discord.Forbidden:
        await ctx.send(f"Couldn't send a DM to {member.mention}, they might have DMs disabled.")

    # Log the command usage
    log_channel = bot.get_channel(L_ID)
    if log_channel:
        log_embed = discord.Embed(title="Command Used", color=discord.Color.blue())
        log_embed.add_field(name="Command", value="`!ben`", inline=False)
        log_embed.add_field(name="User", value=ctx.author.mention, inline=False)
        log_embed.add_field(name="Target", value=member.mention, inline=False)
        log_embed.add_field(name="Reason", value=reason if reason else "No reason provided", inline=False)
        log_embed.set_footer(text=f"Command used in #{ctx.channel.name}")

        await log_channel.send(embed=log_embed)
    else:
        print("Log channel not found.")

translator = Translator()

# Define the allowed translation role IDs
allowed_tl_ids = [1259936621021626460, 1276928831524966484]  # Adjust with your role IDs

# Dictionary for common phrases (expand this as needed)
phrase_mappings = {
    "aja": "come",
    "aja ajao": "come on",
    "kya kar rahe ho": "what are you doing",
    "kya scene hai": "what's going on",
    "abhi tak": "until now",
    "kuch nahi": "nothing",
    "kaise ho": "how are you",
    "theek ho": "are you okay",
    # Add more phrases here
}

def preprocess_text(text):
    # Convert text to lowercase for consistent matching
    text_lower = text.lower()

    # Replace mapped phrases with their equivalents
    for urdu_phrase, english_equivalent in phrase_mappings.items():
        text_lower = text_lower.replace(urdu_phrase, english_equivalent)

    return text_lower

def has_allowed_tl(ctx):
    """Check if the command invoker has one of the allowed translation roles."""
    return any(role.id in allowed_tl_ids for role in ctx.author.roles)

@bot.command()
async def tl(ctx, target_language: str):
    if not has_allowed_tl(ctx):
        return

    if ctx.message.reference:
        try:
            replied_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            original_text = replied_message.content  # Keep the original text as is
            preprocessed_text = preprocess_text(original_text)  # Preprocess the text for translation
        except Exception as e:
            await ctx.send(f"An error occurred while fetching the message: {e}")
            return
    else:
        reply_message = await ctx.send("Please reply to a message to translate.")
        await asyncio.sleep(4)  # Wait for 4 seconds
        await reply_message.delete()
        return

    try:
        # Translate the preprocessed text
        translated_text = translator.translate(preprocessed_text, dest=target_language).text

        # Create and send the embed message
        embed = discord.Embed(title="Translator", color=0xff0000)  # Red color
        embed.add_field(name="Original text", value=original_text, inline=False)  # Show original text
        embed.add_field(name=f"Translation in {target_language.upper()}", value=translated_text, inline=False)

        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"An error occurred during translation: {e}")

allowed_user_ids = [1074831330015191072, 1088466341020827721]

def is_allowed_user(ctx):
    return ctx.author.id in allowed_user_ids

@bot.command(aliases=['seal', 'talla'])
@commands.check(is_allowed_user)
async def lock(ctx):
    channel = ctx.channel  # The channel where the command is invoked
    role = ctx.guild.default_role  # @everyone role

    # Deny sending messages for @everyone in the current channel
    await channel.set_permissions(role, send_messages=False)
    done_message = await ctx.send('Done Seal')
    await done_message.delete(delay=8)

@bot.command(aliases=['unseal', 'chabi'])
@commands.check(is_allowed_user)
async def unlock(ctx):
    channel = ctx.channel  # The channel where the command is invoked
    role = ctx.guild.default_role  # @everyone role

    # Allow sending messages for @everyone in the current channel
    await channel.set_permissions(role, send_messages=True)
    done_message = await ctx.send('Done Unseal ')
    await done_message.delete(delay=8)

UI_USER_IDS = [1074831330015191072, 1088466341020827721]  # Replace with allowed user IDs

@bot.command(name='ui')
async def userinfo(ctx, user: discord.User = None):
    # Check if the command invoker is allowed to use the command
    if ctx.author.id not in UI_USER_IDS:
        return

    # If no user is mentioned or provided, use the command invoker's info
    if user is None:
        user = ctx.author

    # Fetch user profile to get banner and other details
    user = await bot.fetch_user(user.id)

    # Embed for user information
    embed = discord.Embed(title=f"{user.display_name}", color=discord.Color(0x99AAB5))
    embed.set_thumbnail(url=user.avatar.url)

    # User Info without avatar decoration
    embed.add_field(name="**User**", value=(
        f"**Display Name:** {user.display_name}\n"
        f"**Username:** {user}\n"
        f"**ID:** {user.id}\n"
        f"**Color:** #99AAB5\n"
        f"**Badges:** {get_user_badges(user, ctx.guild)}"  # Updated badges function
    ), inline=False)

    # Discord Membership Info
    embed.add_field(name="**Discord Membership**", value=(
        f"{user.created_at.strftime('%B %d, %Y %I:%M %p')} "
        f"({user.created_at.strftime('%b %d, %Y')})"
    ), inline=True)

    # Server Membership Info for the current server
    member = ctx.guild.get_member(user.id)
    if member:
        embed.add_field(name=f"**Membership in {ctx.guild.name}**", value=(
            f"{member.joined_at.strftime('%B %d, %Y %I:%M %p')} "
            f"({member.joined_at.strftime('%b %d, %Y')})"
        ), inline=True)
    else:
        embed.add_field(name=f"**Membership in {ctx.guild.name}**", value="User is not in this server.", inline=True)

    # Highest Role Section
    highest_role = member.top_role.mention if member and len(member.roles) > 1 else "@EVERYONE"
    embed.add_field(name="**Highest Role**", value=highest_role, inline=False)

    # Display the user's banner if available
    if user.banner:
        embed.set_image(url=user.banner.url)
    else:
        embed.add_field(name="Banner", value="No banner set.", inline=False)

    # Creating buttons for additional information
    view = discord.ui.View()
    avatar_button = discord.ui.Button(label="🖼️ View avatar", style=discord.ButtonStyle.primary)
    banner_button = discord.ui.Button(label="View banner", style=discord.ButtonStyle.primary)
    permissions_button = discord.ui.Button(label="View permissions", style=discord.ButtonStyle.primary)

    # Button callbacks
    async def avatar_callback(interaction: discord.Interaction):
        await interaction.response.send_message(f"**Avatar for {user.display_name}:**\n{user.avatar.url}", ephemeral=True)
    
    async def banner_callback(interaction: discord.Interaction):
        banner_url = user.banner.url if user.banner else "No banner set."
        await interaction.response.send_message(f"**Banner for {user.display_name}:**\n{banner_url}", ephemeral=True)
    
    async def permissions_callback(interaction: discord.Interaction):
        if member:
            perms = member.guild_permissions
            permissions = [perm.replace("_", " ").title() for perm, value in perms if value]
            permissions_text = "\n".join(permissions) if permissions else "No special permissions."
            # Truncate if permissions_text exceeds 1024 characters
            if len(permissions_text) > 1024:
                permissions_text = permissions_text[:1021] + "..."
            await interaction.response.send_message(f"**Permissions for {user.display_name}:**\n{permissions_text}", ephemeral=True)
        else:
            await interaction.response.send_message("This user is not in the server, so permissions cannot be displayed.", ephemeral=True)

    # Set the button callbacks
    avatar_button.callback = avatar_callback
    banner_button.callback = banner_callback
    permissions_button.callback = permissions_callback

    # Add buttons to the view
    view.add_item(avatar_button)
    view.add_item(banner_button)
    view.add_item(permissions_button)

    # Send the embed and the button view
    await ctx.send(embed=embed, view=view)

def get_user_badges(user: discord.User, guild: discord.Guild) -> str:
    # Combine badges from user and member
    badges = []
    
    # Check if the user is a member of the guild
    member = guild.get_member(user.id)
    
    # Check available flags and add corresponding badges from the user
    if user.public_flags.partner:
        badges.append("🤝 Partner")
    if user.public_flags.hypesquad:
        # Check which HypeSquad group the user is in
        if user.public_flags.hypesquad_bravery:
            badges.append("🛡️ HypeSquad Bravery")
        if user.public_flags.hypesquad_balance:
            badges.append("⚖️ HypeSquad Balance")
        if user.public_flags.hypesquad_brilliance:
            badges.append("💡 HypeSquad Brilliance")
    if user.public_flags.bug_hunter:
        badges.append("🐞 Bug Hunter")
    if user.public_flags.verified_bot:
        badges.append("✅ Verified Bot")
    if user.public_flags.early_verified_bot_developer:
        badges.append("🔧 Early Verified Bot Developer")

    # Check available flags and add corresponding badges from the member
    if member:
        if member.public_flags.hypesquad:
            badges.append("<:hypesquad_flag:1052741566097264702>")
        if member.public_flags.hypesquad_balance:
            badges.append("<:balance:1059415997729226793>")
        if member.public_flags.hypesquad_bravery:
            badges.append("<:bravery:1059416107733221386>")
        if member.public_flags.hypesquad_brilliance:
            badges.append("<:brilliance:1059416199605272587>")
        if member.public_flags.early_supporter:
            badges.append("<a:earlysup:1003952039807696937>")
        if member.public_flags.active_developer:
            badges.append("<:active_dev:1040559350034473000>")
        if member.public_flags.verified_bot_developer:
            badges.append("<:activedev:1044968012932976750>")
        if member.public_flags.discord_certified_moderator:
            badges.append("<:discord_certified_moderator_flag:1052742235541737553>")
        if member.public_flags.staff:
            badges.append("<:staff_flag:1052742379741925406>")
        if member.public_flags.partner:
            badges.append("<:partner_flag:1052742550647218196>")
    
    return " ".join(badges) if badges else "No badges"


#Emoji symbols for the game
X_SYMBOL = "❌"
O_SYMBOL = "⭕"
EMPTY_SYMBOL = "⬜"

class TicTacToeButton(Button):
    def __init__(self, x: int, y: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=EMPTY_SYMBOL, row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        view: TicTacToeView = self.view
        
        # Ensure only the current player can click the button
        if interaction.user != view.current_player:
            await interaction.response.send_message("It's not your turn!", ephemeral=True)
            return
        
        # If the cell is already filled, do nothing
        if view.board[self.y][self.x] != EMPTY_SYMBOL:
            await interaction.response.defer()
            return

        # Update the button's label and style based on the current player's symbol
        self.label = X_SYMBOL if view.current_turn else O_SYMBOL
        self.style = discord.ButtonStyle.green if view.current_turn else discord.ButtonStyle.red
        self.disabled = True
        view.board[self.y][self.x] = self.label

        # Check if there's a winner or if the board is full (draw)
        if view.check_winner():
            for button in view.children:
                button.disabled = True
            winner = view.current_player
            await interaction.response.edit_message(content=f"{winner.mention} ({self.label}) wins!", view=view)
            await asyncio.sleep(8)  # Wait for 8 seconds
            await interaction.delete_original_response()  # Delete the message
        elif view.is_full():
            await interaction.response.edit_message(content="It's a draw!", view=view)
            await asyncio.sleep(8)  # Wait for 8 seconds
            await interaction.delete_original_response()  # Delete the message
        else:
            # Switch turn and update the current player
            view.current_turn = not view.current_turn
            view.current_player = view.player_x if view.current_turn else view.player_o
            await interaction.response.edit_message(content=f"It's {view.current_player.mention}'s turn!", view=view)

class TicTacToeView(View):
    def __init__(self, player_x: discord.Member, player_o: discord.Member):
        super().__init__()
        self.current_turn = True  # True for X's turn, False for O's turn
        self.player_x = player_x
        self.player_o = player_o
        self.current_player = player_x  # Start with X (player_x)
        self.board = [[EMPTY_SYMBOL for _ in range(3)] for _ in range(3)]

        for y in range(3):
            for x in range(3):
                self.add_item(TicTacToeButton(x, y))

    def check_winner(self):
        for row in self.board:
            if row[0] == row[1] == row[2] != EMPTY_SYMBOL:
                return True

        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != EMPTY_SYMBOL:
                return True

        if self.board[0][0] == self.board[1][1] == self.board[2][2] != EMPTY_SYMBOL:
            return True

        if self.board[0][2] == self.board[1][1] == self.board[2][0] != EMPTY_SYMBOL:
            return True

        return False

    def is_full(self):
        return all(cell != EMPTY_SYMBOL for row in self.board for cell in row)

def has_any_role(*role_ids):
    async def predicate(ctx):
        return any(role.id in role_ids for role in ctx.author.roles)
    return commands.check(predicate)

@bot.command(name='ttt')
@has_any_role(1277191933168717864, 1276928831524966484)
async def tictactoe(ctx, opponent: discord.Member):
    """Start a Tic-Tac-Toe game with buttons, restricted to specific role IDs."""
    if opponent == ctx.author:
        return await ctx.send("You can't play against yourself!")

    view = TicTacToeView(ctx.author, opponent)
    await ctx.send(
        f"Tic-Tac-Toe: {ctx.author.mention} (X) vs {opponent.mention} (O)!\n"
        f"It's {ctx.author.mention}'s turn!",
        view=view
    )

@tictactoe.error
async def tictactoe_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("")

TAG_ROLE_ID = 1278742064238034986  # Replace with your role ID

# List of allowed user IDs
TAG_USER_IDS = {123456789012345678, 1074831330015191072}  # Replace with the IDs of allowed users

def convert_to_bold_italic_thicker(text):
    normal_to_bold_italic_thicker = {
        'a': '𝙖', 'b': '𝙗', 'c': '𝙘', 'd': '𝙙', 'e': '𝙚', 'f': '𝙛', 'g': '𝙜',
        'h': '𝙝', 'i': '𝙞', 'j': '𝙟', 'k': '𝙠', 'l': '𝙡', 'm': '𝙢', 'n': '𝙣',
        'o': '𝙤', 'p': '𝙥', 'q': '𝙦', 'r': '𝙧', 's': '𝙨', 't': '𝙩', 'u': '𝙪',
        'v': '𝙫', 'w': '𝙬', 'x': '𝙭', 'y': '𝙮', 'z': '𝙯',
        'A': '𝘼', 'B': '𝘽', 'C': '𝘾', 'D': '𝘿', 'E': '𝙀', 'F': '𝙁', 'G': '𝙂',
        'H': '𝙃', 'I': '𝙄', 'J': '𝙅', 'K': '𝙆', 'L': '𝙇', 'M': '𝙈', 'N': '𝙉',
        'O': '𝙊', 'P': '𝙋', 'Q': '𝙌', 'R': '𝙍', 'S': '𝙎', 'T': '𝙏', 'U': '𝙐',
        'V': '𝙑', 'W': '𝙒', 'X': '𝙓', 'Y': '𝙔', 'Z': '𝙕',
        ' ': ' ', '!': '!', '?': '?', '.': '.', ',': ','
    }
    return ''.join(normal_to_bold_italic_thicker.get(char, char) for char in text)

class NameModal(Modal):
    def __init__(self):
        super().__init__(title="Enter your name")
        self.name_input = TextInput(label="Your Name")
        self.add_item(self.name_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        name = self.name_input.value
        styled_name = f"! 〆 {convert_to_bold_italic_thicker(name)} ˢᶦⁿⁿᵉʳˢ"
        
        # Send the styled name in DMs
        await interaction.user.send(f"Here is your tag name: {styled_name}")
        await interaction.response.send_message("Check your DMs for the styled name!", ephemeral=True)

@bot.command(name='b')
async def send_button(ctx):
    if ctx.author.id not in TAG_USER_IDS:
        return

    button = Button(label="Get your tag Name", style=discord.ButtonStyle.primary)

    async def button_callback(interaction):
        role = discord.utils.get(interaction.user.roles, id=TAG_ROLE_ID)
        if role:
            # User has the required role, show modal
            modal = NameModal()
            await interaction.response.send_modal(modal)
            
            # Remove the role from the user
            role_obj = discord.utils.get(interaction.guild.roles, id=TAG_ROLE_ID)
            if role_obj:
                await interaction.user.remove_roles(role_obj)
                await interaction.followup.send("Your role has been removed after pressing the button.", ephemeral=True)
        else:
            await interaction.response.send_message("Role Mang Mikey Abu se pehle phr aio", ephemeral=True)
    
    button.callback = button_callback
    view = View()
    view.add_item(button)
    
    await ctx.send("Click the button to get your styled name:", view=view)

AUTHORIZED_USER_ID = 1074831330015191072  # Replace with the actual user ID

@bot.command(name='rh')
async def giverole(ctx, role: discord.Role):
    if ctx.author.id != AUTHORIZED_USER_ID:
        return

    start_time = time.time()
    guild = ctx.guild
    role_assigned = 0

    for member in guild.members:
        if not member.bot:
            if role not in member.roles:
                await member.add_roles(role)
                role_assigned += 1

    end_time = time.time()
    duration = end_time - start_time

    embed = discord.Embed(
        title="Role Assignment Complete",
        description=f"Role `{role.name}` has been assigned to {role_assigned} human members.",
        color=discord.Color.red()
    )
    embed.add_field(name="Time Taken", value=f"{duration:.2f} seconds", inline=False)

    await ctx.send(embed=embed)

@giverole.error
async def giverole_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please specify a role to assign.")
    elif isinstance(error, commands.RoleNotFound):
        await ctx.send("The specified role was not found.")

allowed_users = [1074831330015191072, 1088466341020827721]

class RoleView(View):
    def __init__(self, ctx, role_name, chunks, member_count):
        super().__init__()
        self.ctx = ctx
        self.role_name = role_name
        self.chunks = chunks
        self.member_count = member_count
        self.page = 0
        self.author_id = ctx.author.id

    async def send_embed(self, interaction=None):
        embed = discord.Embed(
            title=f"Members with the {self.role_name} role ({self.member_count} members)",
            color=0xFF0000
        )

        for member in self.chunks[self.page]:
            avatar_url = member.display_avatar.url if member.display_avatar else "https://discordapp.com/assets/322c936a8c8be1b803cd94861bdfa868.png"
            embed.add_field(
                name=f"{member.display_name}", 
                value=f"[Avatar]({avatar_url})\n`{member.id}`", 
                inline=True
            )

        embed.set_footer(text=f"Page {self.page + 1}/{len(self.chunks)}")

        if interaction:
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await self.ctx.send(embed=embed, view=self)

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary, disabled=True)
    async def previous_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message("You are not authorized to use this button.", ephemeral=True)
        
        self.page -= 1
        if self.page == 0:
            button.disabled = True
        self.children[1].disabled = False
        await self.send_embed(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message("You are not authorized to use this button.", ephemeral=True)
        
        self.page += 1
        if self.page == len(self.chunks) - 1:
            button.disabled = True
        self.children[0].disabled = False
        await self.send_embed(interaction)


@bot.command(name="r")
async def role_count(ctx, *, role: Union[discord.Role, str]):
    if ctx.author.id in allowed_users:
        if isinstance(role, str):
            try:
                role = await commands.RoleConverter().convert(ctx, role)
            except commands.BadArgument:
                return

        if role in ctx.guild.roles:
            members_with_role = role.members
            member_count = len(members_with_role)

            if member_count > 0:
                per_page = 6  # Per page item ko 6 members tak limit karna
                chunks = [members_with_role[i:i + per_page] for i in range(0, member_count, per_page)]
                view = RoleView(ctx, role.name, chunks, member_count)

                await view.send_embed()
            else:
                await ctx.send(f"No members have the {role.name} role.")
        else:
            await ctx.send("Invalid role.")

# Function to fetch roast from API
async def get_roast():
    url = 'https://evilinsult.com/generate_insult.php?lang=en&type=json'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data['insult']
            else:
                return "I couldn't think of a roast right now!"

def has_any_role(*role_ids):
    async def predicate(ctx):
        return any(role.id in role_ids for role in ctx.author.roles)
    return commands.check(predicate)

@bot.command()
@has_any_role(1277191933168717864, 1276928831524966484)
async def roast(ctx, member: discord.Member = None):
    if member is None:
        return await ctx.send("Kisi ko mention to karo jisko roast karna hai!", delete_after=10)
    else:
        embed = discord.Embed(color=discord.Color.red())

        if member.id == 1074831330015191072:
            embed.description = f"{member.mention}, Mikey tera baap hai, kaise roast kare ga 🙊"
            await ctx.send(embed=embed, delete_after=15)
        else:
            roast_message = await get_roast()
            embed.description = f"{member.mention}, {roast_message}"
            await ctx.send(embed=embed, delete_after=15)

@roast.error
async def roast_error(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
#        await ctx.send("You don't have permission to use this command!")
         return
# List of allowed user IDs
ALLOWED_R_IDS = [1074831330015191072, 987654321098765432]  # Add your allowed user IDs here

# Check if the user is allowed to use the command
def is_allowed_user():
    async def predicate(ctx):
        return ctx.author.id in ALLOWED_R_IDS
    return commands.check(predicate)

# List all commands (restricted to allowed user IDs)
@bot.command(name="listc")
@is_allowed_user()
async def list_commands(ctx):
    commands_list = [command.name for command in bot.commands]
    await ctx.send(f"Available commands: {', '.join(commands_list)}")

# List all events (restricted to allowed user IDs)
'''@bot.command(name="le")
@is_allowed_user()
async def list_events(ctx):
    events_list = [event for event in dir(bot) if event.startswith('on_')]
    await ctx.send(f"Available events: {', '.join(events_list)}")

def reload_command(command_name):
    if command_name in bot.all_commands:
        bot.remove_command(command_name)
        for name, obj in globals().items():
            if callable(obj) and isinstance(obj, commands.Command) and obj.name == command_name:
                bot.add_command(obj)
                return f"Command '{command_name}' reloaded successfully."
    return f"Command '{command_name}' not found."

def reload_event(event_name):
    # Event reload is simulated by restarting the bot
    return f"Event '{event_name}' cannot be dynamically reloaded. Restarting the bot to apply changes."

@bot.command()
@is_allowed_user()
async def reload(ctx, item: str):
    try:
        if item in bot.all_commands:
            result = reload_command(item)
        elif item.startswith('on_'):
            result = reload_event(item)
            # Restart the bot to apply event changes
            await ctx.send(f"🔄 reload done. Bot restart and done apply changes.", delete_after=10)
            os.execv(sys.executable, ['python'] + sys.argv)
        else:
            result = f"'{item}' is neither a command nor an event."

        await ctx.send(f"🔄 {result}", delete_after=10)
    except Exception as e:
        await ctx.send(f"❌ Failed to reload '{item}'.\nError: `{e}`", delete_after=6)'''

# Define allowed user IDs (replace with actual IDs)
VC_USER_IDS = {1074831330015191072, 1088466341020827721}  # Example IDs

async def send_and_delete_reply(ctx, embed):
    reply_message = await ctx.reply(embed=embed)
    await asyncio.sleep(10)
    await reply_message.delete()

@bot.command(name="muteall", help="Mute all members in the voice channel.", usage="!muteall")
@commands.cooldown(1, 10, commands.BucketType.user)
async def muteall(ctx):
    if ctx.author.id not in VC_USER_IDS:
        return
    
    if not ctx.author.voice:
        embed = discord.Embed(
            title="FUCKER",
            description="You are not connected to any voice channel.",
            color=0xFF0000
        ).set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        return await send_and_delete_reply(ctx, embed)

    channel = ctx.author.voice.channel
    count = 0
    for member in channel.members:
        if not member.voice.mute:
            await member.edit(mute=True, reason=f"Muted by {ctx.author}")
            count += 1

    embed = discord.Embed(
        title="FUCKER",
        description=f"Muted {count} members in {channel.mention}.",
        color=0xFF0000
    ).set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
    return await send_and_delete_reply(ctx, embed)

@bot.command(name="unmuteall", help="Unmute all members in the voice channel.", usage="!unmuteall")
@commands.cooldown(1, 10, commands.BucketType.user)
async def unmuteall(ctx):
    if ctx.author.id not in VC_USER_IDS:
        return
    
    if not ctx.author.voice:
        embed = discord.Embed(
            title="FUCKER",
            description="You are not connected to any voice channel.",
            color=0xFF0000
        ).set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        return await send_and_delete_reply(ctx, embed)

    channel = ctx.author.voice.channel
    count = 0
    for member in channel.members:
        if member.voice.mute:
            await member.edit(mute=False, reason=f"Unmuted by {ctx.author}")
            count += 1

    embed = discord.Embed(
        title="FUCKER",
        description=f"Unmuted {count} members in {channel.mention}.",
        color=0xFF0000
    ).set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
    return await send_and_delete_reply(ctx, embed)

@bot.command(name="moveall", help="Moves all members from the voice channel to another voice channel.", usage="!moveall <voice channel>")
@commands.cooldown(1, 10, commands.BucketType.user)
async def moveall(ctx, *, channel: discord.VoiceChannel):
    if ctx.author.id not in VC_USER_IDS:
        return

    if ctx.author.voice is None:
        embed = discord.Embed(
            title="FUCKER",
            description="You are not connected to any voice channel.",
            color=0xFF0000
        ).set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        return await send_and_delete_reply(ctx, embed)

    try:
        source_channel = ctx.author.voice.channel
        destination_channel = channel
        count = 0
        for member in source_channel.members:
            await member.move_to(destination_channel, reason=f"Moved by {ctx.author}")
            count += 1

        embed = discord.Embed(
            title="FUCKER",
            description=f"Moved {count} members from {source_channel.mention} to {destination_channel.mention}.",
            color=0xFF0000
        ).set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        await send_and_delete_reply(ctx, embed)

    except Exception as e:
        embed = discord.Embed(
            title="FUCKER",
            description="An error occurred. Please make sure the voice channel is valid.",
            color=0xFF0000
        ).set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        await send_and_delete_reply(ctx, embed)


def is_allowed_np_user(ctx):
    return ctx.author.id in NP_ADD_IDS

@bot.command(name='npa')
async def add_noprefix(ctx, user: discord.User):
    """Adds a user to the no-prefix list by mentioning them or their user ID."""
    if not is_allowed_np_user(ctx):
        return

    cursor = await bot.db.execute("SELECT * FROM Np WHERE users = ?", (user.id,))
    result = await cursor.fetchone()

    if result:
        #await ctx.send(f"User {user} is already in the no-prefix list.")
        return
    else:
        await bot.db.execute("INSERT INTO Np(users) VALUES(?)", (user.id,))
        await bot.db.commit()
        await ctx.send(f"done", delete_after=7)

@bot.command(name='npr')
async def remove_noprefix(ctx, user: discord.User):
    """Removes a user from the no-prefix list by mentioning them or their user ID."""
    if not is_allowed_np_user(ctx):
        return

    cursor = await bot.db.execute("SELECT * FROM Np WHERE users = ?", (user.id,))
    result = await cursor.fetchone()

    if result:
        await bot.db.execute("DELETE FROM Np WHERE users = ?", (user.id,))
        await bot.db.commit()
        await ctx.send(f"done", delete_after=8)
    else:
        return

# Run the bot with your token
menu_user_ids = [1074831330015191072, 987654321098765432]  # Yahan par aap apni user IDs dalen

@bot.command(aliases=['bar', 'h'], description="Displays a list of all commands.")
async def help(ctx):
    # Check if the user is allowed to use this command
    if ctx.author.id not in menu_user_ids:
        return

    # Embed bana rahe hain
    embed = discord.Embed(
        title="**__Commands Bar__**",
        description="*Here is our commands*",
        color=discord.Color.red()
    )

    # Commands aur unki descriptions add kar rahe hain
    embed.add_field(name="> **__?av @user__**\n", value="*Note = If Member have Ignore role then bot does'nt*", inline=False)
    embed.add_field(name="> **__?afk any reason you want__**", value="*Note If You put any @ or link then bot does'nt response you*", inline=False)
    embed.add_field(name="> **__?sbn or ?bn__**", value="*Note = ?sbn for simple banners and bn for gifs and animated banners*", inline=False)
    embed.add_field(name="> **__?sb and ?gi __**", value="*Note = sb for server banner and gi for server icon*", inline=False)
    embed.add_field(name="> **__?snipe and ?su__**", value="*Note use buttons for see recent 5 delete msgs ans su for individiual user msgs*", inline=False)
    embed.add_field(name="> **__?purge limit and ?pu__**", value="*Note = Purge limit is only 50 and pu for individual purge user msgs*", inline=False)
    embed.add_field(name="> **__?warn reason__**", value="*Note no one is wl in warn*", inline=False)
    embed.add_field(name="> **__?nick @user nick__**", value="*Note Dont use for fun or personal hate*", inline=False)
    embed.add_field(name="> **__?mute @user reason must__**", value="*Note Don't mute anyone without any reason*", inline=False)
    embed.add_field(name="> **__?unmute @user__**", value="**", inline=False)
    embed.add_field(name="> **__?ban @user reason must__**", value="*Note Only for higher staff*", inline=False)
    embed.add_field(name="> **__?unban user id __**", value="*Note Only for higher Staff*", inline=False)
    embed.add_field(name="> **__?vr @user__**", value="*Note Bot give vanity roles*", inline=False)
    embed.add_field(name="> **__?vrr__**", value="*Note Bot remove vanity roles*", inline=False)
    embed.add_field(name="> **__?g @girl user__**", value="*Note Bot give verified girl role*", inline=False)
    embed.add_field(name="> **__?gr @girl user__**", value="*Note Bot Remove verified girl role*", inline=False)
    embed.add_field(name="> **__pic @user__**", value="*Note This is personal so only for serious staff*", inline=False)
    embed.add_field(name="> **__?ui @user__**", value="*Note Draken Mikey cmd*", inline=False)
    embed.add_field(name="> **__?ttt @user__**", value="**", inline=False)
    embed.add_field(name="> **__?roast @user__**", value="**", inline=False)
    embed.add_field(name="> **__?tl any language__**", value="*Note = It's only work in reply msg*", inline=False)
    embed.add_field(name="> **__?muteall in vc__**", value="*Note Owner cmds*", inline=False)
    embed.add_field(name="> **__?unmuteall in vc__**", value="*Note Owner cmds*", inline=False)
    embed.add_field(name="> **__?moveall channel__**", value="*Note Owner cmds*", inline=False)
    embed.add_field(name="> **__Auto tag system__**", value="*Note = Enter your name in button bot send your tag name in your dm*", inline=False)

    # Aap yahan aur commands add kar sakte hain

    await ctx.send(embed=embed)


@commands.cooldown(1, 5, commands.BucketType.user)
@bot.command()
async def ship(ctx, member1: discord.Member = None, member2: discord.Member = None):
    if member1 is None and member2 is None:
        member1 = ctx.author
        all_members = [m for m in ctx.guild.members if not m.bot and m != ctx.author]
        member2 = random.choice(all_members) if all_members else ctx.author
    elif member2 is None:
        member2 = member1
        member1 = ctx.author

    if member1 == member2:
        await ctx.send("Khud se kaise ship kre ga selflover ha kya")
        return

    mikey_id = 1074831330015191072
    role_id_1 = 1260191112384221264
    role_id_2 = 1260182004129988618

    if mikey_id in [member1.id, member2.id]:
        other = member2 if member1.id == mikey_id else member1
        role_ids = [role.id for role in other.roles]

        if role_id_1 in role_ids:
            await ctx.reply("Kya likhe... Gay ha kya jo ship kar raha Mikey ke sath?")
            return
        elif role_id_2 in role_ids:
            await ctx.send("Kia matlb qt abhi tak Mikey ka pyaar nahi samaj payi 🙊")
            return

    # --- normal ship logic niche chalega agar mikey special case nahi mila ---

    match_percentage = random.randint(0, 100)
    avatar1 = await (member1.avatar or member1.default_avatar).read()
    avatar2 = await (member2.avatar or member2.default_avatar).read()

    def make_circular(im):
        mask = Image.new("L", (180, 180), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, 180, 180), fill=255)
        output = ImageOps.fit(Image.open(BytesIO(im)).convert("RGBA"), (180, 180))
        output.putalpha(mask)
        return output

    avatar_img1 = make_circular(avatar1)
    avatar_img2 = make_circular(avatar2)

    bg = Image.new("RGBA", (500, 250), (255, 192, 203))
    bg.paste(avatar_img1, (40, 35), avatar_img1)
    bg.paste(avatar_img2, (280, 35), avatar_img2)

    embed = discord.Embed(title="💖 MATCHMAKING 💖", color=discord.Color.red())
    embed.add_field(name="Combined Name", value=f"**{member1.display_name} ✕ {member2.display_name}**", inline=False)
    embed.add_field(name="Status", value="`Loading... [▒▒▒▒▒▒▒▒▒▒] 0%`", inline=False)

    with BytesIO() as image_binary:
        bg.save(image_binary, "PNG")
        image_binary.seek(0)
        file = discord.File(fp=image_binary, filename="ship_result.png")
        embed.set_image(url="attachment://ship_result.png")
        msg = await ctx.reply(embed=embed, file=file)

    for i in range(1, 11):
        percent = i * 10
        bar = "█" * i + "▒" * (10 - i)
        embed.set_field_at(1, name="Status", value=f"`Loading... [{bar}] {percent}%`", inline=False)
        await msg.edit(embed=embed)
        await asyncio.sleep(0.4)

    if match_percentage < 20:
        result = f"💔 Very Bad Match ({match_percentage}%)"
    elif match_percentage < 50:
        result = f"😕 Could be better ({match_percentage}%)"
    elif match_percentage < 75:
        result = f"💖 Looks Promising! ({match_percentage}%)"
    else:
        result = f"❤️ Perfect Match! ({match_percentage}%)"

    embed.set_field_at(1, name="Status", value=result, inline=False)
    await msg.edit(embed=embed)

class PaginatedView(discord.ui.View):
    def __init__(self, users, ctx, author_id, title="User List"):
        super().__init__(timeout=60)
        self.users = users
        self.ctx = ctx
        self.author_id = author_id
        self.page = 0
        self.chunk_size = 10
        self.title = title
        self.chunks = [users[i:i + self.chunk_size] for i in range(0, len(users), self.chunk_size)]
        self.message = None

        self.previous_button = discord.ui.Button(label="Previous", style=discord.ButtonStyle.primary)
        self.next_button = discord.ui.Button(label="Next", style=discord.ButtonStyle.primary)

        self.previous_button.callback = self.previous_button_callback
        self.next_button.callback = self.next_button_callback

        self.update_buttons()

    def update_buttons(self):
        self.previous_button.disabled = self.page == 0
        self.next_button.disabled = self.page == len(self.chunks) - 1

        self.clear_items()
        self.add_item(self.previous_button)
        self.add_item(self.next_button)

    async def send_embed(self, interaction=None):
        embed = discord.Embed(
            title=f"{self.title} - Page {self.page + 1}",
            color=discord.Color.green()
        )

        for i, user_id in enumerate(self.chunks[self.page], start=self.page * self.chunk_size + 1):
            user = await bot.fetch_user(user_id)
            embed.add_field(
                name=f"**{i}.** {user.name}",
                value=f"**ID:** `{user_id}`",
                inline=False
            )

        if self.message is None:
            self.message = await self.ctx.send(embed=embed, view=self)
        else:
            if interaction and not interaction.response.is_done():
                await interaction.response.edit_message(embed=embed, view=self)
            else:
                await self.message.edit(embed=embed, view=self)

    async def previous_button_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message("You are not authorized to use this button.", ephemeral=True)

        if self.page > 0:
            self.page -= 1
            self.update_buttons()

        await interaction.response.defer()
        await self.send_embed(interaction)

    async def next_button_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message("You are not authorized to use this button.", ephemeral=True)

        if self.page < len(self.chunks) - 1:
            self.page += 1
            self.update_buttons()

        await interaction.response.defer()
        await self.send_embed(interaction)

@bot.command(name='npl')
async def list_noprefix(ctx):
    if not is_allowed_np_user(ctx):
        return

    cursor = await bot.db.execute("SELECT users FROM Np")
    np_users = await cursor.fetchall()

    if not np_users:
        return await ctx.send("No no-prefix users found.")

    user_ids = [user[0] for user in np_users]
    view = PaginatedView(user_ids, ctx, ctx.author.id, title="No-Prefix Users")
    await view.send_embed()


@bot.command(name="vrl")
async def allowed_role_ids(ctx):
    if ctx.author.id not in RP_ALLOWED_USERS:
        return

    c_roles_perms.execute("SELECT user_id FROM allowed_ids")
    allowed_user_ids = [row[0] for row in c_roles_perms.fetchall()]

    if not allowed_user_ids:
        return

    view = PaginatedView(allowed_user_ids, ctx, ctx.author.id, title="Vanity Cmd User IDs")
    await view.send_embed()

# Allowed user IDs
'''SLASH_USER_IDS = {1074831330015191072, 987654321098765432}  # Replace with your user IDs

# Log channel ID (replace with your log channel ID)
SLASH_CHANNEL_ID = 1259934096025718875

class SayCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="say", description="Bot repeats your message (restricted access)")
    @app_commands.describe(message="What you want the bot to say")
    async def say(self, interaction: discord.Interaction, message: str):
        # Permission check
        if interaction.user.id not in SLASH_USER_IDS:
            return await interaction.response.send_message(
                "You don't have permission to use this command.", ephemeral=True
            )

        # Block mentions
        if any(tag in message.lower() for tag in ["@everyone", "@here", "<@&"]):
            return await interaction.response.send_message(
                "Mentions like @everyone, @here, or role pings are not allowed.", ephemeral=True
            )

        # Say the message
        await interaction.response.send_message(content=message, allowed_mentions=discord.AllowedMentions.none())

        # Logging
        log_channel = self.bot.get_channel(SLASH_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="Say Command Used",
                description=f"**User:** {interaction.user.mention} (`{interaction.user.id}`)\n**Message:** {message}",
                color=discord.Color.orange(),
                timestamp=datetime.utcnow()
            )
            await log_channel.send(embed=embed)'''


if __name__ == "__main__":
    bot.run('')
