import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
import json


class tempVC(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    with open('config.json', 'r') as f:
        data = json.load(f)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.__class__.__name__} cog has been loaded!')

    @nextcord.slash_command(guild_ids=data["guilds"], description="invite user to voice channel")
    async def invite(self, interaction: Interaction, user: nextcord.Member = SlashOption(name="user", description="user to invite"),):

        currentVC = interaction.user.voice.channel
        overwrite = nextcord.PermissionOverwrite()
        overwrite.view_channel = True
        await currentVC.set_permissions(user, overwrite=overwrite)

        await interaction.response.send_message(f"{user.display_name} has been invite to the channel", ephemeral=True)


def setup(bot):
    bot.add_cog(tempVC(bot))
