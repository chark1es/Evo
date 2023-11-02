import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
import json
from functions import shortcuts as s
from pocketbase import PocketBase
from dotenv import dotenv_values


class clearMessages(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    with open('config.json', 'r') as f:
        data = json.load(f)

    @nextcord.slash_command(guild_ids=data["guilds"])
    async def clear_messages(self, interaction: Interaction, limit: int, type: str = SlashOption(
        name="type",
        description="Choose the type",
        choices={"text": "text", "images": "images", "all": "all"},
    )):

        await interaction.response.defer(ephemeral=True, with_message=True)

        try:
            if interaction.user.guild_permissions.manage_messages:
                if type == "text":
                    await interaction.channel.purge(limit=limit, check=lambda m: not m.attachments, bulk=True)
                elif type == "images":
                    await interaction.channel.purge(limit=limit, check=lambda m: len(m.attachments) > 0, bulk=True)
                elif type == "all":
                    await interaction.channel.purge(limit=limit, bulk=True)
                else:
                    await interaction.followup.send("Invalid type", ephemeral=True)
                    return
                await interaction.followup.send(f"Deleted {limit} messages", ephemeral=True)
            else:
                await interaction.response.send_message("You don't have the permission to do that", ephemeral=True)

        except Exception as e:
            s.throwError(self.__class__.__name__, e, "clear_messages")

            if interaction.response.is_done():
                await interaction.followup.send("Something went wrong. Please DM the developer of the discord bot", ephemeral=True)
            else:
                await interaction.response.send_message("Something went wrong. Please DM the developer of the discord bot", ephemeral=True)


def setup(bot):
    bot.add_cog(clearMessages(bot))
