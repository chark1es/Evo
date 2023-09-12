import nextcord
from nextcord import Interaction, ApplicationCheckFailure
import os
import json
from nextcord.ext import commands
from nextcord.ext.commands import Greedy, Context
from dotenv import dotenv_values
from typing import Literal, Optional

# Load
botToken = dotenv_values(".env").get("TOKEN")

intents = nextcord.Intents.all()
intents.members = True
intents.presences = True
intents.voice_states = True
bot = commands.Bot(command_prefix="/", intents=intents,
                   application_id="1108673506780135475")
bot.remove_command("help")

excluded_files = ["functions.py"]

# Read configurations
with open('config.json', 'r') as f:
    data = json.load(f)


@bot.command()
async def load(ctx, extension):
    if ctx.author.id in data["authors"]:  # Replace with your nextcord ID
        try:
            bot.load_extension(f'cogs.{extension}')
            await ctx.send(f'Cog **{extension}** has been loaded')
        except Exception as e:
            await ctx.send(f'{extension} failed to load. \n[{e}]')


@bot.command()
async def unload(ctx, extension):
    if ctx.author.id in data["authors"]:  # Replace with your nextcord ID
        try:
            bot.unload_extension(f'cogs.{extension}')
            await ctx.send(f'Cog **{extension}** has been unloaded')
        except Exception as e:
            await ctx.send(f'{extension} failed to unload. \n[{e}]')


@bot.command()
async def reload(ctx, extension):
    if ctx.author.id in data["authors"]:  # Replace with your nextcord ID
        try:
            bot.unload_extension(f'cogs.{extension}')
            bot.load_extension(f'cogs.{extension}')
            await ctx.send(f'The cog **{extension}** has been reloaded')
        except Exception as e:
            await ctx.send(f"Failed to reload {extension}: {e}")


@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}!')

    # Load all cogs at startup
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and filename not in excluded_files:
            try:
                bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'Cog {filename[:-3]} loaded successfully')
            except Exception as e:
                print(f"Failed to load {filename[:-3]}: {e}")


@bot.command()
async def sync(ctx):
    if not ctx.author.id in data["authors"]:
        return None
    try:
        for guild_id in data["guilds"]:
            await bot.sync_application_commands(guild_id=guild_id)
        await ctx.send("Successfully synced", reference=ctx.message)
    except Exception as e:
        await ctx.send(f"ERROR: {e}", reference=ctx.message)


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    print(f'Message from {message.author}: {message.content}')

# Load all cogs at startup


bot.run(botToken)
