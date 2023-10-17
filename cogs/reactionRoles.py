import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
import json
from functions import shortcuts as s
from pocketbase import PocketBase
from dotenv import dotenv_values


class reactionRoles(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    with open('config.json', 'r') as f:
        data = json.load(f)

    def getGuildList(interaction: Interaction):
        try:
            guild_id = str(interaction.guild_id)
            email = dotenv_values(".env").get("DB_EMAIL")
            password = dotenv_values(".env").get("DB_PASSWORD")
            client = PocketBase(dotenv_values(".env").get("DB_URL"))
            admin_data = client.admins.auth_with_password(email, password)

            records = client.collection("Evo_reactionRoles").get_full_list(
                query_params={"expand": "id"})

            for record in records:
                if (guild_id in record.__dict__["guild_id"]):
                    record = record.__dict__
                    break

            try:
                lst = record["lst"].keys()
            except TypeError:
                print(
                    f"Error: 'record' object is not subscriptable. Type: {type(record)}")
                lst = []
            return {name: name for name in lst}
        except Exception as e:
            s.throwError("reactionRoles", e, "getGuildList")
            return []

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.__class__.__name__} cog has been loaded!')

    @nextcord.slash_command(guild_ids=data["guilds"], description="main command")
    async def reaction_roles(self, interaction: Interaction):
        pass

    @reaction_roles.subcommand(description="create list of reactions")
    async def create_list(self, interaction: Interaction, name: str):
        try:
            guild_id = str(interaction.user.guild.id)
            email = dotenv_values(".env").get("DB_EMAIL")
            password = dotenv_values(".env").get("DB_PASSWORD")
            client = PocketBase(dotenv_values(".env").get("DB_URL"))
            admin_data = client.admins.auth_with_password(email, password)

            records = client.collection("Evo_reactionRoles").get_full_list(
                query_params={"expand": "id"})
        except Exception as e:
            s.throwError(self.__class__.__name__, e)
            await interaction.response.send_message("An error occurred! Please contact the admin.", ephemeral=True)
            return

        guildExists = False
        for record in records:
            if (guild_id in record.__dict__["guild_id"]):
                record = record.__dict__
                guildExists = True
                break

        if guildExists:
            if name in record["message_id"]:
                await interaction.response.send_message("This name already exists!", ephemeral=True)
                return
            else:
                record["lst"][name] = []
                record["roles"][name] = []
                client.collection("Evo_reactionRoles").update(
                    record["id"], record)
                await interaction.response.send_message("Created a new reaction list!", ephemeral=True)

        else:
            data = {
                "guild_id": guild_id,
                "lst": {name: []},
                "roles": {name: []}
            }
            result = client.collection("Evo_reactionRoles").create(data)
            await interaction.response.send_message("Created a new reaction list!", ephemeral=True)

    @reaction_roles.subcommand(description="add reaction role to list")
    async def add_reaction(self, interaction: Interaction, reaction: str, role: nextcord.Role, reactionList: str = SlashOption(
        name="list",
        description="Choose the list you want to modify",
        choices=getGuildList(Interaction)
    )):

        try:
            guild_id = str(interaction.user.guild.id)
            email = dotenv_values(".env").get("DB_EMAIL")
            password = dotenv_values(".env").get("DB_PASSWORD")
            client = PocketBase(dotenv_values(".env").get("DB_URL"))
            admin_data = client.admins.auth_with_password(email, password)

            records = client.collection("Evo_reactionRoles").get_full_list(
                query_params={"expand": "id"})
        except Exception as e:
            s.throwError(self.__class__.__name__, e)
            await interaction.response.send_message("An error occurred! Please contact the admin.", ephemeral=True)
            return

        for record in records:
            if (guild_id == record.__dict__["guild_id"]):
                record = record.__dict__
                break

        if reactionList not in record["lst"]:
            await interaction.response.send_message("This list does not exist!", ephemeral=True)
            return

        data = {
            "lst": record["lst"]
        }

        data["lst"].append(reaction)

        client.collection("Evo_reactionRoles").update(record["id"], data)

        await interaction.response.send_message("Added a new reaction to the list!", ephemeral=True)


def setup(bot):
    bot.add_cog(reactionRoles(bot))
