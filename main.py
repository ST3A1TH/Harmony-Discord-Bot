import discord
from discord.ext import commands
from discord.utils import get
from discord.ext import commands, tasks 
from googlesearch import search as google_search
from collections import defaultdict
import requests
import asyncio  
import re
import json
import curses
import random 
import datetime
import time
import functools
import os


# Getting the token
TOKEN = ''

# Set your command prefix
bot_prefix = "."
# Create an instance of the bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=bot_prefix, intents=intents)
intents.members = True  # You need to enable the members intent explicitly

# Dictionary to store warnings
warnings = {}
queues = {}
custom_statuses = {}

@bot.event
async def on_ready():
    await bot.change_presence(status=default_status, activity=default_activity)
    print(f'Logged in as {bot.user.name}')
    print(f'----------------------------')
    print(f'User ID: {bot.user.id}')
    print(f'Servers: {len(bot.guilds)}')

    # Print server names
    for guild in bot.guilds:
        print(guild.name)

    print(f'Commands: {len(bot.commands)}')
    print(f'Ping: {round(bot.latency * 1000)}ms')
    print(f'----------------------------')
    print(f'Made by St3alth Devs')

    # Birthday event
    for guild_id, channel_id in bday_channels.items():
        guild = bot.get_guild(int(guild_id))
        channel = guild.get_channel(int(channel_id))
        if channel:
            for user_id, bday_date in user_birthdays.items():
                if datetime.datetime.now().strftime('%m-%d') == datetime.datetime.strptime(bday_date, '%Y-%m-%d').strftime('%m-%d'):
                    user = guild.get_member(int(user_id))
                    if user:
                        embed = discord.Embed(title="Happy Birthday!", description=f"It's {user.mention}'s birthday today! 🎉🎂", color=discord.Color.gold())
                        await channel.send(embed=embed)
        else:
            print(f"Channel not found in guild with ID {guild_id}")

@bot.event
async def on_guild_join(guild):
    # Set the default custom status for a new server
    custom_statuses[guild.id] = {'status': default_status, 'activity': default_activity}


# Set the bot's status

is_running = True  # A variable to track the bot's running state

# Function to update bot's presence for a specific guild
async def update_presence(guild):
    # Get the custom status for the guild
    guild_status = custom_statuses.get(guild.id)

    # If custom status is set for the guild, update presence
    if guild_status:
        status = guild_status['status']
        activity = guild_status['activity']
    else:
        # If no custom status set, use default status and activity
        status = default_status
        activity = default_activity

    # Update bot's presence
    await bot.change_presence(status=status, activity=activity)

# Function to update presence for all guilds
async def update_all_presences():
    for guild in bot.guilds:
        await update_presence(guild)

bot_owner_ids = ('1171067347801473125', '1165054507076554942')
default_status = discord.Status.online
default_activity = discord.Activity(type=discord.ActivityType.watching, name="Zen's Army")

@bot.command(name='setstatus')
async def set_status(ctx, status: str, *, activity_name: str = ' .commands'):
    # Check if the user is one of the bot owners
    if str(ctx.author.id) not in bot_owner_ids:
        await ctx.send("Only bot owners can use this command.")
        return

    # Convert status string to discord.Status
    status = getattr(discord.Status, status, None)
    if status is None:
        await ctx.send("Invalid status. Use 'online', 'idle', or 'dnd'.")
        return

    # Set the custom status for the server
    custom_statuses[ctx.guild.id] = {'status': status, 'activity': discord.Activity(type=discord.ActivityType.watching, name=activity_name)}

    # Update the bot's presence for this server
    await update_presence(ctx.guild)

    await ctx.send(f"Bot status updated to {status} with activity: {activity_name} for this server.")


# List of 20 quotes
quotes = [
    "The only limit to our realization of tomorrow will be our doubts of today. - Franklin D. Roosevelt",
    "The only way to do great work is to love what you do. - Steve Jobs",
    "Success is not final, failure is not fatal: It is the courage to continue that counts. - Winston Churchill",
    "In the middle of every difficulty lies opportunity. - Albert Einstein",
    "Believe you can and you're halfway there. - Theodore Roosevelt",
    "Your time is limited, don't waste it living someone else's life. - Steve Jobs",
    "The best way to predict the future is to create it. - Peter Drucker",
    "Strive not to be a success, but rather to be of value. - Albert Einstein",
    "It always seems impossible until it's done. - Nelson Mandela",
    "Success is stumbling from failure to failure with no loss of enthusiasm. - Winston Churchill",
    "The only place where success comes before work is in the dictionary. - Vidal Sassoon",
    "Don't watch the clock; do what it does. Keep going. - Sam Levenson",
    "Life is what happens when you're busy making other plans. - John Lennon",
    "Opportunities don't happen. You create them. - Chris Grosser",
    "The only person you are destined to become is the person you decide to be. - Ralph Waldo Emerson",
    "If you want to achieve greatness stop asking for permission. - Anonymous",
    "Do one thing every day that scares you. - Eleanor Roosevelt",
    "You miss 100% of the shots you don't take. - Wayne Gretzky",
    "It's not whether you get knocked down, it's whether you get up. - Vince Lombardi",
    "Don't count the days, make the days count. - Muhammad Ali"
]

@bot.command(name='quote')
async def quote(ctx):
    # Select a random quote
    selected_quote = random.choice(quotes)

    # Create an embed to display the quote
    embed = discord.Embed(title='Quote of the Day', description=selected_quote, color=0x00ff00)

    # Send the embed to the channel
    await ctx.send(embed=embed)


# Define the event to delete commands after execution
@bot.event
async def on_command_completion(ctx):
    await asyncio.sleep(5)  # Adjust the delay as needed
    await ctx.message.delete()


# Command to ban a user
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, user: discord.User):
    # Replace 'Your Server Name' with your actual server name
    server_name = ctx.guild.name

    # Create the embedded message
    embed = discord.Embed(
        title="You have been banned!",
        description=f"You have been banned from {server_name}.",
        color=0xFF0000  # You can customize the color
    )

    # Send the embedded message to the banned user
    try:
        await user.send(embed=embed)
    except discord.Forbidden:
        # Unable to send a direct message to the user
        pass

    await ctx.guild.ban(user)
    await ctx.send(f"{user.name} has been banned from {server_name}.")


@bot.command()
@commands.has_permissions(administrator=True)
async def announce(ctx, *, message):
    # Find the mentioned channel
    mentioned_channel = ctx.message.channel_mentions
    if not mentioned_channel:
        await ctx.send("Please mention a channel to send the announcement.")
        return

    channel = mentioned_channel[0]

    # Craft the embed
    embed = discord.Embed(title="Announcement", description=message, color=discord.Color.blue())
    embed.set_footer(text=f"Announced by {ctx.author.display_name}")

    # Send the announcement
    await channel.send("@everyone", embed=embed)


@bot.command()
@commands.has_permissions(administrator=True)
async def addrole(ctx, role_name, hex_color):
    # Convert hex color to discord.Color
    try:
        color = discord.Color(int(hex_color, 16))
    except ValueError:
        await ctx.send("Invalid hex color format.")
        return

    # Create the role
    try:
        new_role = await ctx.guild.create_role(name=role_name, color=color)
        await ctx.send(f"Role '{role_name}' created successfully with color {hex_color}.")
    except discord.Forbidden:
        await ctx.send("I don't have permission to create roles.")
    except discord.HTTPException:
        await ctx.send("An error occurred while creating the role.")


# Command to kick a user
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, user: discord.User, *, reason="No reason provided."):
    # Replace 'Your Server Name' with your actual server name
    server_name = ctx.guild.name
    # Get the moderator who performed the kick
    moderator = ctx.author

    # Create the embedded message
    embed = discord.Embed(
        title="You have been kicked!",
        description=f"You have been kicked from {server_name} by {moderator.mention}.",
        color=0xFF0000  # You can customize the color
    )
    embed.add_field(name="Reason", value=reason)

    # Send the embedded message to the kicked user
    try:
        await user.send(embed=embed)
    except discord.Forbidden:
        # Unable to send a direct message to the user
        pass

    await ctx.guild.kick(user, reason=reason)
    await ctx.send(f"{user.name} has been kicked from {server_name} by {moderator.mention} for the reason: {reason}.")



# Load birthdays and birthday channels from a JSON file
try:
    with open('birthdays.json', 'r') as file:
        user_birthdays = json.load(file)
except FileNotFoundError:
    user_birthdays = {}

try:
    with open('bday_channels.json', 'r') as file:
        bday_channels = json.load(file)
except FileNotFoundError:
    bday_channels = {}


# Function to save data to the JSON file
def save_data(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file)


# Command to set a user's birthday
@bot.command()
async def setbday(ctx, date: str):
    try:
        # Parse the input date string to a datetime object
        birthday_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        # Store the user's birthday in the dictionary
        user_birthdays[str(ctx.author.id)] = birthday_date.strftime('%Y-%m-%d')
        save_data(user_birthdays, 'birthdays.json')  # Save the updated birthdays
        await ctx.send(f"Your birthday has been set to {birthday_date.strftime('%B %d, %Y')}.")
    except ValueError:
        await ctx.send("Invalid date format. Please use YYYY-MM-DD.")


# Command to view a user's birthday
@bot.command()
async def viewbday(ctx, user: discord.User):
    # Check if the user has set their birthday
    user_id = str(user.id)
    if user_id not in user_birthdays:
        await ctx.send("This user has not set their birthday.")
        return

    # Get the birthday of the mentioned user
    birthday = user_birthdays[user_id]

    # Send an embed with the user's birthday
    embed = discord.Embed(title="User Birthday", color=discord.Color.blue())
    embed.add_field(name="User", value=user.mention, inline=False)
    embed.add_field(name="Birthday", value=birthday, inline=False)
    await ctx.send(embed=embed)


# Command to set the birthday channel for the server
@bot.command()
async def setbdaychannel(ctx, channel: discord.TextChannel):
    bday_channels[str(ctx.guild.id)] = channel.id
    save_data(bday_channels, 'bday_channels.json')
    await ctx.send(f"Birthday channel set to {channel.mention}.")


@bot.command()
@commands.has_permissions(ban_members=True)
async def unban_user(ctx, user_id: int, *, reason="No reason provided."):
    # Replace 'Your Server Name' with your actual server name
    server_name = ctx.guild.name
    # Get the moderator who performed the unban
    moderator = ctx.author

    # Create the embedded message
    embed = discord.Embed(
        title="You have been unbanned!",
        description=f"You have been unbanned from {server_name} by {moderator.mention}.",
        color=0x00ff00  # You can customize the color
    )
    embed.add_field(name="Reason", value=reason)

    # Fetch the banned user by ID
    banned_user = await bot.fetch_user(user_id)

    if banned_user:
        # Unban the user
        await ctx.guild.unban(banned_user, reason=reason)

        # Send the embedded message to the unbanned user
        try:
            await banned_user.send(embed=embed)
        except discord.Forbidden:
            # Unable to send a direct message to the user
            pass

        await ctx.send(f"{banned_user.name} has been unbanned from {server_name} by {moderator.mention} for the reason: {reason}.")
    else:
        await ctx.send(f"Unable to find the user with ID {user_id}.")

@bot.command(name='invite')
async def invite_command(ctx):
    # Create an embed with the invite link
    embed = discord.Embed(
        title="Invite Flow to Your Server",
        description="Click the button below to add Flow to your server.",
        color=discord.Color.blue()
    )

    invite_link = "https://discord.com/api/oauth2/authorize?client_id=1201490343300960326&permissions=8&scope=bot"
    add_to_server_button = discord.ui.Button(
        style=discord.ButtonStyle.link,
        label="Add to Server",
        url=invite_link
    )
    view = discord.ui.View()
    view.add_item(add_to_server_button)

    # Send the embed to the channel
    await ctx.send(embed=embed, view=view)


@bot.command(name='serverinfo', aliases=['server'])
@commands.has_permissions(administrator=True)
async def server_info(ctx):
    # Get information about the server
    server = ctx.guild

    # Create an embed with server information
    embed = discord.Embed(title=f"Server Information - {server.name}", color=discord.Color.blue())
    embed.add_field(name="Server ID", value=server.id, inline=False)
    embed.add_field(name="Owner", value=server.owner, inline=False)
    embed.add_field(name="Members", value=server.member_count, inline=False)
    embed.add_field(name="Creation Date", value=server.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)

    # Send the embed to the channel
    await ctx.send(embed=embed)




# Command to mute a user
@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member):
  role = discord.utils.get(ctx.guild.roles, name="Muted")
  if not role:
    role = await ctx.guild.create_role(name="Muted")
    for channel in ctx.guild.channels:
      await channel.set_permissions(role, send_messages=False)
  await member.add_roles(role)
  await ctx.send(f"{member.mention} has been muted.")


# Command to warn a user
@bot.command(name='warn')
@commands.has_permissions(kick_members=True)
async def warn(ctx, user: discord.Member, *, reason):
    # Generate a unique case number
    case_number = len(warnings) + 1

    # Add the warning to the dictionary
    warnings.setdefault(user.id, []).append({'case': case_number, 'reason': reason})

    # Send a message indicating the warning
    await ctx.send(f'{user.mention} has been warned (Case {case_number}): {reason}')
    await user.send(f'You have been warned in {ctx.guild.name} (Case {case_number}): {reason}')

@bot.command(name='warnings')
@commands.has_permissions(kick_members=True)
async def user_warnings(ctx, user: discord.Member):
    # Get the user's warnings from the dictionary
    user_warnings = warnings.get(user.id, [])

    if not user_warnings:
        await ctx.send(f'{user.mention} has no warnings.')
        return

    # Create and send an embed with the user's warnings
    embed = discord.Embed(title=f'Warnings for {user.name}', color=0xff0000)
    for warning in user_warnings:
        embed.add_field(name=f'Case {warning["case"]}', value=warning['reason'], inline=False)
  
    await ctx.send(embed=embed)



#command to dm a user
@bot.command()
@commands.has_permissions(administrator=True)
async def dm(ctx, user: discord.User, *, message: str):
    # Check if the user is a member of the server
    if user in ctx.guild.members:
        # User is in the server, tag them
        user_mention = user.mention
    else:
        # User is outside the server, use their ID
        user_mention = f"<@{user.id}>"

    # Create an embed message
    embed = discord.Embed(
        title=f"Message from {ctx.guild.name}",
        description=message,
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Sent at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")

    # Send the direct message
    try:
        await user.send(embed=embed)
        await ctx.send(f"Message sent to {user_mention} from server: {ctx.guild.name}.")
    except discord.Forbidden:
        await ctx.send(f"Unable to send a message to {user_mention}. Their DM settings Must be off.")


@bot.command(name='userinfo', aliases=['user', 'uinfo'])
@commands.has_permissions(administrator=True)
async def user_info(ctx, member: discord.Member = None):
    # If no member is specified, default to the command invoker
    member = member or ctx.author

    # Create and send an embed with user information
    embed = discord.Embed(
        title=f"User Information - {member.display_name}",
        color=member.color if isinstance(member, discord.Member) else discord.Color.default()
    )

    embed.add_field(name="User ID", value=member.id, inline=False)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime('%Y-%m-%d %H:%M:%S UTC'), inline=False)
    embed.add_field(name="Account Created", value=member.created_at.strftime('%Y-%m-%d %H:%M:%S UTC'), inline=False)

    # Display roles
    roles = [role.mention for role in member.roles if role.name != "@everyone"]
    if roles:
        embed.add_field(name="Roles", value=" ".join(roles), inline=False)
    else:
        embed.add_field(name="Roles", value="No roles", inline=False)

    await ctx.send(embed=embed)



@bot.command()
@commands.has_permissions(manage_messages=True)
async def say(ctx, *, message):
  # Delete the user's message
  await ctx.message.delete()

  # Say the provided message as the bot
  await ctx.send(message)


# Define the bot command
@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, limit: int = 100):
    if limit > 10000000:
        await ctx.send("You cannot purge more than 10,000,000 messages.")
        return

    await ctx.channel.purge(limit=limit + 1)  # Add 1 to include the command message
    await ctx.send(f"Purged {limit} messages.", delete_after=5)  # Delete the confirmation message after 5 seconds

# Handle errors for the purge command
@purge.error
async def purge_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid argument. Please provide a valid number.")
    else:
        await ctx.send("An error occurred while processing the command.")


@bot.command(name='unwarn')
@commands.has_permissions(mute_members=True)
async def unwarn(ctx, user: discord.Member, case_number: int):
    # Check if the user has any warnings
    user_warnings = warnings.get(user.id, [])

    if not user_warnings:
        await ctx.send(f'{user.mention} has no warnings.')
        return

    # Check if the specified case number exists for the user
    case_exists = any(warning['case'] == case_number for warning in user_warnings)

    if not case_exists:
        await ctx.send(f'Case {case_number} not found for {user.mention}.')
        return

    # Remove the specified warning
    warnings[user.id] = [warning for warning in user_warnings if warning['case'] != case_number]

    # Send a message indicating the unwarning
    await ctx.send(f'Removed warning (Case {case_number}) for {user.mention}.')


@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx, channel: discord.TextChannel = None):
  if not channel:
    channel = ctx.channel

  # Create overwrite permissions to deny sending messages for everyone
  overwrites = {
      ctx.guild.default_role: discord.PermissionOverwrite(send_messages=False)
  }
  await channel.edit(overwrites=overwrites)

  await ctx.send(f"{channel.mention} has been locked.")


@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx, channel: discord.TextChannel = None):
  if not channel:
    channel = ctx.channel

  # Reset the channel permissions to allow sending messages for everyone
  await channel.set_permissions(ctx.guild.default_role, send_messages=True)

  await ctx.send(f"{channel.mention} has been unlocked.")




@bot.command()
async def poll(ctx, *options):
  if len(options) < 2:
    await ctx.send("You need to provide at least two options for the poll.")
    return

  question = " ".join(options[:-1])
  choices = options[-1].split(",")

  if len(choices) < 2:
    await ctx.send("You need to separate options with commas.")
    return

  poll_embed = discord.Embed(
      title="Poll",
      description=question,
      color=0x3498db  # You can customize the color
  )

  poll_options = ""
  for i, choice in enumerate(choices, start=1):
    poll_options += f"{i}. {choice.strip()}\n"

  poll_embed.add_field(name="Options", value=poll_options, inline=False)
  poll_embed.set_footer(text=f"Poll created by {ctx.author.display_name}")

  poll_message = await ctx.send(embed=poll_embed)

  for i in range(len(choices)):
    await poll_message.add_reaction(f"{i + 1}\N{COMBINING ENCLOSING KEYCAP}")




commands_data = {
    "Moderation": [
        {"name": ".ban", "description": "Bans a user from the server.", "permissions": ["ban_members"]},
        {"name": ".kick", "description": "Kicks a user from the server.", "permissions": ["kick_members"]},
        {"name": ".lock", "description": "Locks a channel, preventing messages.", "permissions": ["manage_channels"]},
        {"name": ".mute", "description": "Mutes a user in the server.", "permissions": ["mute_members"]},
        {"name": ".unban_user", "description": "Unbans a user from the server.", "permissions": ["ban_members"]},
        {"name": ".unlock", "description": "Unlocks a previously locked channel.", "permissions": ["manage_channels"]},
        {"name": ".warn", "description": "Warns a user with a specified reason.", "permissions": ["kick_members"]},
      {"name": ".announce", "description": "Announce any message in any channel.", "permissions": ["kick_members"]},
      {"name": ".addrole", "description": "Create a new role in the server using hex and name of the role.", "permissions": ["manage_roles"]}
    ],
    "Fun": [
        {"name": ".dm", "description": "Sends a direct message to a user.", "permissions": []},
        {"name": ".poll", "description": "Creates a simple poll.", "permissions": ["manage_messages"]},
        {"name": ".say", "description": "Makes the bot say something.", "permissions": ["manage_messages"]},
        {"name": ".search", "description": "Performs a Google search.", "permissions": []},
      {"name": ".quote", "description": "Gives you quote of the day.", "permissions": ["All can use"]},
      {"name": ".setbday", "description": "Set your birthday so you get wished a happy birthday!", "permissions": ["All can use"]},
      {"name": ".viewbday", "description": "View someone in the servers bday", "permissions": ["All can use"]},

    ],
}

@bot.command(name='commands')
async def commands_command(ctx):
    # Create a list of categories
    categories = list(commands_data.keys())

    # Create an embed for each category
    embeds = []
    for category in categories:
        category_commands = commands_data[category]
        embed = discord.Embed(title=f"Bot Commands - {category}", color=discord.Color.blue())

        # Add commands and descriptions to the embed
        for command_info in category_commands:
            permissions = ", ".join(command_info["permissions"])
            embed.add_field(name=f"{command_info['name']} (Permissions: {permissions})", value=command_info['description'], inline=False)

        embeds.append(embed)

    # Send the first embed
    message = await ctx.send(embed=embeds[0])

    # Add reactions for pagination
    for emoji in ['⬅️', '➡️']:
        await message.add_reaction(emoji)

    current_page = 0

    # Reaction check
    def check(reaction, user):
        return user == ctx.author and reaction.emoji in ['⬅️', '➡️']

    # Reaction handling loop
    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)

            # Handle pagination
            if reaction.emoji == '➡️':
                current_page = (current_page + 1) % len(embeds)
            elif reaction.emoji == '⬅️':
                current_page = (current_page - 1) % len(embeds)

            # Update the message with the new embed
            await message.edit(embed=embeds[current_page])

            # Remove the user's reaction
            await message.remove_reaction(reaction.emoji, user)

        except TimeoutError:
            # Stop the loop after a timeout
            break



# Run the bot
bot.run(TOKEN)

# Run the bot with your token

# Define your commands and event handlers here...
# Your bot token (replace with your actual token)

token =os.environ['TOKEN']
while True:
  try:
    bot.run(token)
  except Exception as e:
    print(f"An error occurred: {e}")






