import nextcord
from nextcord.ext import commands
from aiohttp import web
import asyncio
from pocketbase import PocketBase
from dotenv import dotenv_values
import json
from nextcord import Interaction, SlashOption

import string
import random

app = web.Application()


async def index(request):

    try:
        data = await request.json()
    except json.JSONDecodeError:
        return web.json_response({'status': 'error', 'message': 'Invalid JSON received'}, status=400)

    apiKey = data.get('api_key')
    if apiKey == None:
        return web.json_response({'status': 'error', 'message': 'Missing API Key'}, status=400)

    userID = data.get('user_id')
    if userID == None:
        return web.json_response({'status': 'error', 'message': 'Missing User ID'}, status=400)

    trueRecord = None

    def check_auth(apiKey=apiKey, userID=userID):
        global trueRecord
        email = dotenv_values(".env").get("DB_EMAIL")
        password = dotenv_values(".env").get("DB_PASSWORD")
        client = PocketBase(dotenv_values(".env").get("DB_URL"))
        admin_data = client.admins.auth_with_password(email, password)
        records = client.collection("Evo_UserAPI").get_full_list(
            query_params={"expand": "id"})

        authenicated = False
        hasApiKey = False

        for record in records:

            print(f"\n\n{record.__dict__}\n\n")

            if (apiKey in record.__dict__["api_key"]):
                hasApiKey = True
            if (apiKey in record.__dict__["api_key"] and userID in record.__dict__["user_id"]):
                authenicated = True
                trueRecord = record

        if not authenicated:
            if (hasApiKey):
                return {"status": "error", "message": "This API key is not meant for this user"}
            else:
                return {"status": "error", "message": "Invalid API key"}

        return {"status": "success"}

    auth = check_auth(apiKey, userID)
    if auth["status"] == "error":
        return web.json_response(auth, status=400)

    kv = trueRecord.__dict__["kv"]

    user = await request.app['bot'].fetch_user(userID)
    accentColor = user.accent_color
    avatar = user.avatar.url
    banner = user.banner.url
    bot = user.bot
    color = user.color.value
    created_at = user.created_at.isoformat()
    default_avatar = user.default_avatar.url
    discriminator = user.discriminator
    name = user.name
    nickname = user.display_name
    user_id = user.id

    responseJson = {
        "status": "success",
        "accentColor": accentColor,
        "avatar": avatar,
        "banner": banner,
        "bot": bot,
        "color": color,
        "created_at": created_at,
        "default_avatar": default_avatar,
        "discriminator": discriminator,
        "name": name,
        "nickname": nickname,
        "user_id": user_id,
        "kv": kv
    }
    return web.json_response(responseJson)


app.router.add_get('/', index)


class userAPI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.runner = None
        self.site = None
        self.bot.loop.create_task(self.run_server())

    async def run_server(self):
        self.runner = web.AppRunner(app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, '0.0.0.0', 1192)
        await self.site.start()

    with open('config.json', 'r') as f:
        data = json.load(f)

    def cog_unload(self):
        # Schedule the coroutine to shut down the server
        asyncio.create_task(self.shutdown_server())

    async def shutdown_server(self):
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()

    @nextcord.slash_command(guild_ids=data["guilds"], description="main command")
    async def userapi(self, interaction: Interaction):
        pass

    # Invites the user to a voice channel
    @userapi.subcommand(description="get key value")
    async def get(self, interaction: Interaction, key: str):

        email = dotenv_values(".env").get("DB_EMAIL")
        password = dotenv_values(".env").get("DB_PASSWORD")
        client = PocketBase(dotenv_values(".env").get("DB_URL"))
        admin_data = client.admins.auth_with_password(email, password)
        records = client.collection("Evo_UserAPI").get_full_list(
            query_params={"expand": "id"})

        for record in records:
            if str(interaction.user.id) == record.__dict__["user_id"]:
                if key in record.__dict__["kv"]:
                    await interaction.response.send_message(record.__dict__["kv"][key], ephemeral=True)
                    return
                else:
                    await interaction.response.send_message("Key not found", ephemeral=True)
                    return

    @userapi.subcommand(description="set key value")
    async def set(self, interaction: Interaction, key: str, value: str):

        email = dotenv_values(".env").get("DB_EMAIL")
        password = dotenv_values(".env").get("DB_PASSWORD")
        client = PocketBase(dotenv_values(".env").get("DB_URL"))
        admin_data = client.admins.auth_with_password(email, password)
        records = client.collection("Evo_UserAPI").get_full_list(
            query_params={"expand": "id"})

        for record in records:
            if str(interaction.user.id) == record.__dict__["user_id"]:
                tempData = {
                    key: value
                }
                data = {
                    "kv": tempData
                }
                result = client.collection("Evo_UserAPI").update(
                    record.__dict__["id"], data)

                await interaction.response.send_message("Key set", ephemeral=True)

    @userapi.subcommand(description="list all kv pairs")
    async def list(self, interaction: Interaction):

        email = dotenv_values(".env").get("DB_EMAIL")
        password = dotenv_values(".env").get("DB_PASSWORD")
        client = PocketBase(dotenv_values(".env").get("DB_URL"))
        admin_data = client.admins.auth_with_password(email, password)
        records = client.collection("Evo_UserAPI").get_full_list(
            query_params={"expand": "id"})

        for record in records:
            if str(interaction.user.id) == record.__dict__["user_id"]:
                await interaction.response.send_message(record.__dict__["kv"], ephemeral=True)

    @userapi.subcommand(description="create api key")
    async def create(self, interaction: Interaction):

        email = dotenv_values(".env").get("DB_EMAIL")
        password = dotenv_values(".env").get("DB_PASSWORD")
        client = PocketBase(dotenv_values(".env").get("DB_URL"))
        admin_data = client.admins.auth_with_password(email, password)
        records = client.collection("Evo_UserAPI").get_full_list(
            query_params={"expand": "id"})

        for record in records:
            if str(interaction.user.id) == record.__dict__["user_id"]:
                await interaction.response.send_message("You already have an API key", ephemeral=True)
                return

        randomAPI = ''.join(random.choices(string.ascii_letters, k=32))
        data = {
            "api_key": randomAPI,
            "user_id": str(interaction.user.id),
            "kv": {}
        }

        result = client.collection("Evo_UserAPI").create(
            data)

        await interaction.response.send_message("Your API key is `{}`. If you forget your API key, do /userapi reset".format(randomAPI), ephemeral=True)

    @userapi.subcommand(description="reset api key")
    async def reset(self, interaction: Interaction):
        email = dotenv_values(".env").get("DB_EMAIL")
        password = dotenv_values(".env").get("DB_PASSWORD")
        client = PocketBase(dotenv_values(".env").get("DB_URL"))
        admin_data = client.admins.auth_with_password(email, password)
        records = client.collection("Evo_UserAPI").get_full_list(
            query_params={"expand": "id"})

        for record in records:
            if str(interaction.user.id) == record.__dict__["user_id"]:
                randomAPI = ''.join(random.choices(string.ascii_letters, k=32))
                data = {
                    "api_key": randomAPI
                }
                result = client.collection("Evo_UserAPI").update(
                    record.__dict__["id"], data)


def setup(bot):
    app['bot'] = bot  # Store bot instance in the app for reference
    bot.add_cog(userAPI(bot))
