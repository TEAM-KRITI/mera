# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 🚀
#
# This source code is under MIT License 📜
# ===========================================================

from pyrogram import Client
import config

from ..logging import LOGGER


assistants = []
assistantids = []


class Userbot(Client):

    def __init__(self):
        self.one = Client(
            name="ShiviAss1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
            no_updates=True,
        )

        self.two = Client(
            name="ShiviAss2",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING2),
            no_updates=True,
        )

        self.three = Client(
            name="ShiviAss3",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING3),
            no_updates=True,
        )

        self.four = Client(
            name="ShiviAss4",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING4),
            no_updates=True,
        )

        self.five = Client(
            name="ShiviAss5",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING5),
            no_updates=True,
        )

    async def _start_assistant(self, client, number, chats):
        """
        Safely start one assistant.
        """

        if not getattr(config, f"STRING{number}", None):
            return False

        try:
            await client.start()

            # Join required chats.
            for chat in chats:
                try:
                    await client.join_chat(chat)
                except Exception:
                    pass

            # Get Telegram user information.
            me = await client.get_me()

            client.id = me.id
            client.name = me.mention
            client.username = me.username

            # Add only after successful startup.
            if number not in assistants:
                assistants.append(number)

            if me.id not in assistantids:
                assistantids.append(me.id)

            try:
                await client.send_message(
                    config.LOGGER_ID,
                    "» ᴀssɪsᴛᴀɴᴛ sᴛᴀʀᴛᴇᴅ",
                )
            except Exception:
                LOGGER(__name__).warning(
                    f"» ᴀssɪsᴛᴀɴᴛ {number} ᴄᴏᴜʟᴅ ɴᴏᴛ sᴇɴᴅ ᴛʜᴇ ʟᴏɢ ᴍᴇssᴀɢᴇ."
                )

            LOGGER(__name__).info(
                f"✦ ᴀssɪsᴛᴀɴᴛ {number} sᴛᴀʀᴛᴇᴅ ᴀs {client.name}"
            )

            return True

        except Exception as e:

            LOGGER(__name__).error(
                f"❌ ᴀssɪsᴛᴀɴᴛ {number} ғᴀɪʟᴇᴅ ᴛᴏ sᴛᴀʀᴛ: {e}"
            )

            # Make sure failed assistant is not selected.
            if number in assistants:
                assistants.remove(number)

            try:
                if client.is_connected:
                    await client.stop()
            except Exception:
                pass

            return False

    async def start(self):
        LOGGER(__name__).info(
            "» sᴛᴀʀᴛɪɴɢ ᴀssɪsᴛᴀɴᴛs..."
        )

        # Clear old values after restart/reload.
        assistants.clear()
        assistantids.clear()

        # ---------------------------------------------------
        # ASSISTANT 1
        # ---------------------------------------------------

        await self._start_assistant(
            self.one,
            1,
            [
                "Kirti_update",
                "kirti_chat_support",
            ],
        )

        # ---------------------------------------------------
        # ASSISTANT 2
        # ---------------------------------------------------

        await self._start_assistant(
            self.two,
            2,
            [
                "Kirti_update",
                "kirti_chat_support",
            ],
        )

        # ---------------------------------------------------
        # ASSISTANT 3
        # ---------------------------------------------------

        await self._start_assistant(
            self.three,
            3,
            [
                "Kirti_update",
                "kirti_chat_support",
            ],
        )

        # ---------------------------------------------------
        # ASSISTANT 4
        # ---------------------------------------------------

        await self._start_assistant(
            self.four,
            4,
            [
                "Kirti_update",
                "kirti_chat_support",
            ],
        )

        # ---------------------------------------------------
        # ASSISTANT 5
        # ---------------------------------------------------

        await self._start_assistant(
            self.five,
            5,
            [
                "Kirti_update",
                "kirti_chat_support",
            ],
        )

        # ---------------------------------------------------
        # FINAL STATUS
        # ---------------------------------------------------

        if assistants:
            LOGGER(__name__).info(
                f"✅ ᴀᴄᴛɪᴠᴇ ᴀssɪsᴛᴀɴᴛs: {assistants}"
            )

        else:
            LOGGER(__name__).error(
                "❌ ɴᴏ ᴀssɪsᴛᴀɴᴛ ᴡᴀs sᴛᴀʀᴛᴇᴅ. "
                "ᴄʜᴇᴄᴋ STRING1-STRING5 ɪɴ ᴄᴏɴғɪɢ."
            )

    async def stop(self):
        LOGGER(__name__).info(
            "» sᴛᴏᴘᴘɪɴɢ ᴀssɪsᴛᴀɴᴛs..."
        )

        clients = [
            self.one,
            self.two,
            self.three,
            self.four,
            self.five,
        ]

        for client in clients:
            try:
                if client.is_connected:
                    await client.stop()
            except Exception:
                pass

        assistants.clear()
        assistantids.clear()

        LOGGER(__name__).info(
            "» ᴀʟʟ ᴀssɪsᴛᴀɴᴛs sᴛᴏᴘᴘᴇᴅ."
        )


# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 😎
#
# 🧑‍💻 Developer : t.me/TheSigmaCoder
# 🔗 Source link : GitHub.com/Im-Notcoder/Shivi-V2
# 📢 Telegram channel : t.me/Purvi_Bots
# ===========================================================
