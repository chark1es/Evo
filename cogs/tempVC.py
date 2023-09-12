import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
import json
from functions import shortcuts as s


class tempVC(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    with open('config.json', 'r') as f:
        data = json.load(f)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.__class__.__name__} cog has been loaded!')

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):

        channels = s.getChannels(channel.guild.id)
        if channel.id in channels:
            s.removeChannels(channel.guild.id, channel_id=channel.id)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        channels = s.getChannels(member.guild.id)
        monitorChannels = s.getChannels(
            member.guild.id, vctype='monitor_voice_channel')

        try:
            if after.channel.id in channels:
                voiceChannel = await member.guild.create_voice_channel(name=f"{member.display_name}", category=after.channel.category)
                await member.move_to(voiceChannel)
                s.addChannels(member.guild.id, channel_id=voiceChannel.id,
                              vctype='monitor_voice_channel')
            elif before.channel.id in monitorChannels:
                if len(before.channel.members) == 0:
                    await before.channel.delete()
                    s.removeChannels(member.guild.id, channel_id=before.channel.id,
                                     vctype='monitor_voice_channel')
        except AttributeError as a:
            pass
        except Exception as e:
            print(e)

    # Main slash command, cannot be used

    @nextcord.slash_command(guild_ids=data["guilds"], description="main command")
    async def vc(self, interaction: Interaction):
        pass

    # Invites the user to a voice channel
    @vc.subcommand(description="invite user to voice channel")
    async def invite(self, interaction: Interaction, user: nextcord.Member = SlashOption(name="user", description="user to invite"),):

        currentVC = interaction.user.voice.channel
        overwrite = nextcord.PermissionOverwrite()
        overwrite.view_channel = True
        await currentVC.set_permissions(user, overwrite=overwrite)

        await interaction.response.send_message(f"{user.display_name} has been invite to the channel", ephemeral=True)

    # Creates a voice channel that sends the user to their own temporary voice channel
    @vc.subcommand(description="creates a voice channel that will create temporary voice channels when a user joins")
    async def create_vc(self, interaction: Interaction, category: nextcord.CategoryChannel = SlashOption(name="category", description="category, if any, to create a VC under.", required=False)):

        guildID = interaction.user.guild.id

        if category != None:
            # No category was specified
            voiceChannel = await interaction.guild.create_voice_channel(name="Join Here", category=category)
        else:
            try:
                category = await interaction.guild.create_category(name="Temp Voice Chat")
            except Exception as e:
                print(e)
            voiceChannel = await interaction.guild.create_voice_channel(name="Join Here", category=category)

        s.addChannels(interaction.guild.id, voiceChannel.id)

        await interaction.response.send_message(f"A voice channel named {voiceChannel.name} has been created and is under the category named {category.name}", ephemeral=True)


def setup(bot):
    bot.add_cog(tempVC(bot))
