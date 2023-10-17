import nextcord
from nextcord.ext import commands
from aiohttp import web
import asyncio
from pocketbase import PocketBase
from dotenv import dotenv_values
import json
from nextcord import Interaction, SlashOption
from functions import shortcuts as s

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

    def check_auth(apiKey=apiKey, userID=userID):

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
                break

        if not authenicated:
            if (hasApiKey):
                return {"status": "error", "message": "This API key is not meant for this user"}
            else:
                return {"status": "error", "message": "Invalid API key"}

        return {"status": "success"}, record

    auth, record = check_auth(apiKey, userID)
    if auth["status"] == "error":
        return web.json_response(auth, status=400)

    kv = record.__dict__["kv"]

    try:
        user = request.app['bot'].get_user(int(userID))
        guildID = user.mutual_guilds[0].id

        mutualGuild = request.app['bot'].get_guild(guildID)

    except Exception as e:
        s.throwError("userAPI", e, "Getting user and guild object")
        return web.json_response({"status": "error", "message": "User does not share any mutual guilds with the bot"}, status=400)
    member = mutualGuild.get_member(
        int(userID))
    print(member)
    accentColor = member.accent_color
    avatar = member.avatar.url
    # banner = member.banner.url
    bot = member.bot
    color = member.color.value
    created_at = member.created_at.isoformat()
    default_avatar = member.default_avatar.url
    discriminator = member.discriminator
    name = member.name
    nickname = member.display_name
    user_id = member.id

    mobileStatus = member.mobile_status
    desktopStatus = member.desktop_status
    webStatus = member.web_status
    status = member.status
    rawStatus = member.raw_status

    def safe_getattr(obj, attr_name, default=None):
        """Safely retrieve an attribute from an object."""
        return getattr(obj, attr_name, default)

    def handle_generic_activity(activity):
        attributes = [
            'name', 'type', 'url', 'created_at', 'timestamps',
            'application_id', 'details', 'state', 'emoji',
            'party', 'assets', 'buttons', 'secrets', 'instance',
            'flags', 'large_image_url', 'large_image_text',
            'small_image_url', 'small_image_text', 'start', 'end'
        ]
        return {attr: str(safe_getattr(activity, attr)) for attr in attributes}

    def handle_spotify_activity(activity):
        attributes = ['track_id', 'artist', 'album', 'track', 'duration']
        return {attr: str(safe_getattr(activity, attr)) for attr in attributes}

    def handle_game_activity(activity):
        attributes = ['name', 'type', 'url', 'details', 'state', 'large_image_url',  'large_image_text',
                      'small_image_url', 'small_image_text']
        return {attr: str(safe_getattr(activity, attr)) for attr in attributes}

    def handle_streaming_activity(activity):
        attributes = ['name', 'type', 'url', 'details', 'state', "large_image_url", 'large_image_text',
                      'small_image_url', 'small_image_text']
        return {attr: str(safe_getattr(activity, attr)) for attr in attributes}

    def handle_custom_activity(activity):
        attributes = ['name', 'type', 'created_at', 'emoji', 'state']
        return {attr: str(safe_getattr(activity, attr)) for attr in attributes}

    activity_handlers = {
        nextcord.activity.Activity: handle_generic_activity,
        nextcord.activity.Spotify: handle_spotify_activity,
        nextcord.activity.Game: handle_game_activity,
        nextcord.activity.Streaming: handle_streaming_activity,
        nextcord.activity.CustomActivity: handle_custom_activity
    }

    activity_type = type(member.activity)
    if activity_type in activity_handlers:
        userActivity = activity_handlers[activity_type](member.activity)
    else:
        userActivity = {}

    responseJson = {
        "status": "success",
        "accentColor": accentColor,
        "avatar": avatar,
        # "banner": banner,
        "bot": bot,
        "color": color,
        "created_at": created_at,
        "default_avatar": default_avatar,
        "discriminator": discriminator,
        "name": name,
        "nickname": nickname,
        "user_id": user_id,
        "kv": kv,
        "mobileStatus": mobileStatus,
        "desktopStatus": desktopStatus,
        "webStatus": webStatus,
        "status": status,
        "rawStatus": rawStatus,
        "primaryActivity": userActivity,
        # "listActivities": lst

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
