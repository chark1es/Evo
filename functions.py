
import json
from pocketbase import PocketBase  # Client also works the same
from pocketbase.client import FileUpload
from dotenv import dotenv_values
import traceback


class shortcuts():

    def __init__(self, client):
        self.client = client

    def throwError(cog, e, specific="Nothing Specific"):
        print(
            f"ERROR in {cog} \n\n{type(e).__name__}  \n\nException: {e} \n\nTraceback: {traceback.format_exc()}")

    def getChannels(guild_id, vctype="voice_channel"):
        guild_id = str(guild_id)
        email = dotenv_values(".env").get("DB_EMAIL")
        password = dotenv_values(".env").get("DB_PASSWORD")
        client = PocketBase(dotenv_values(".env").get("DB_URL"))
        admin_data = client.admins.auth_with_password(email, password)

        records = client.collection("Evo_tempVC").get_full_list(
            query_params={"expand": "id"})

        for record in records:
            if (guild_id in record.__dict__["guild_id"]):
                lst = record.__dict__[vctype][guild_id]
                for index, value in enumerate(lst):
                    lst[index] = int(value)
                return lst

        # Creates a new database if one doesn't exist
        data = {
            "guild_id": guild_id,
            "voice_channel": {guild_id: []},
            "monitor_voice_channel": {guild_id: []}
        }
        result = client.collection("Evo_tempVC").create(data)
        return result.__dict__[vctype][guild_id]

    def addChannels(guild_id, channel_id, vctype="voice_channel"):
        channel_id = str(channel_id)
        guild_id = str(guild_id)
        email = dotenv_values(".env").get("DB_EMAIL")
        password = dotenv_values(".env").get("DB_PASSWORD")
        client = PocketBase(dotenv_values(".env").get("DB_URL"))
        admin_data = client.admins.auth_with_password(email, password)

        records = client.collection("Evo_tempVC").get_full_list(
            query_params={"expand": "id"})

        recordExists = False

        for record in records:
            if (guild_id in record.__dict__["guild_id"]):
                listData = record.__dict__[vctype][guild_id]
                recordExists = True
                break
        if recordExists:

            listData.append(channel_id)

            listData = {
                guild_id: listData
            }

            data = {
                vctype: listData
            }

            result = client.collection("Evo_tempVC").update(
                record.__dict__["id"], data)

            iD = record.__dict__["id"]

        else:
            data = {
                "guild_id": guild_id,
                "voice_channel": {guild_id: []},
                "monitor_voice_channel": {guild_id: []}
            }
            result = client.collection("Evo_tempVC").create(data)

            # Push updated data
            data = {
                vctype: {guild_id: [channel_id]}
            }
            result = client.collection("Evo_tempVC").update(
                result.__dict__["id"], data)

    def removeChannels(guild_id, channel_id, vctype="voice_channel"):
        channel_id = str(channel_id)
        guild_id = str(guild_id)
        email = dotenv_values(".env").get("DB_EMAIL")
        password = dotenv_values(".env").get("DB_PASSWORD")
        client = PocketBase(dotenv_values(".env").get("DB_URL"))
        admin_data = client.admins.auth_with_password(email, password)

        records = client.collection("Evo_tempVC").get_full_list(
            query_params={"expand": "id"})

        recordExists = False
        for record in records:
            if (guild_id in record.__dict__["guild_id"]):
                listData = record.__dict__[vctype][guild_id]
                recordExists = True
                break

        if recordExists:

            listData.remove(channel_id)

            listData = {
                guild_id: listData
            }

            data = {
                vctype: listData
            }

            result = client.collection("Evo_tempVC").update(
                record.__dict__["id"], data)

            iD = record.__dict__["id"]
