import os
import sys
import asyncio
import traceback
from datetime import datetime, timedelta

from pyrogram import Client
from pyrogram.errors import FloodWait
from pyrogram.types import BotCommand
from pyrogram.errors.exceptions.bad_request_400 import AccessTokenExpired

from d4rk.Logs import setup_logger

logger = setup_logger(__name__)

class BotManager(Client):
    _bot: Client = None
    _web = True
    _bot_info = None
    _is_connected = False
    _rename = False
    _flood_data = {}
    TOKEN_INDEX = 0
    _loop = None
    _scheduler_thread = None
    font = 0
    sudo_users = []


    def create_client(self,token_index):
        super().__init__(
            name=self.app_name,
            api_id=self.api_id,
            api_hash=self.api_hash,
            bot_token=self.tokens[token_index],
            plugins=self.plugins,
            in_memory=True
            )

    def load_flood_data(self):
        if not os.path.exists('flood.txt'):
            return self._flood_data

        with open('flood.txt', "r") as f:
            for line in f:
                if ":" not in line:
                    continue
                try:
                    token_index, until = map(int, line.strip().split(":"))
                    if token_index not in self._flood_data or until > self._flood_data[token_index]:
                        self._flood_data[token_index] = until
                except:
                    continue

    async def handle_flood_wait(self, wait_time: int):
        logger.info(f"FloodWait: Sleeping for {wait_time} seconds.")

        await asyncio.sleep(wait_time)
        try:await super().start()
        except AccessTokenExpired:pass
        
    def _safe_async(self, coro_func):
        if self._loop:asyncio.run_coroutine_threadsafe(coro_func(), self._loop)
        else:logger.error("Event loop is not set for _safe_async")

    def get_token_index_from_flood_file(self):
        if not os.path.exists("flood.txt"):
            return 0
        now = int(datetime.now(self.TZ).timestamp())
        available = []
        non_flooded = []
        for i in range(len(self.tokens)):
            until = self._flood_data.get(i, 0)
            if until <= now:
                logger.info(f"Token 0{i + 1} is not in flood.")
                self._flood_data.pop(i, None)
                self.save_flood_data()
                non_flooded.append((i))
            else:
                available.append((i, until))
            if non_flooded != []:
                return non_flooded[0]
        logger.warning("All tokens are in flood. Picking the one with the soonest expiry.")
        available.sort(key=lambda x: x[1])
        return available[0][0]
    def save_flood_data(self):
        with open('flood.txt', "w") as f:
            for token_index, until in self._flood_data.items():
                f.write(f"{token_index}:{until}\n")

    async def change_token(self, token_index,wait_time):
        flood_until = datetime.now(self.TZ) + timedelta(seconds=wait_time)
        self._flood_data[token_index] = int(flood_until.timestamp())
        self.save_flood_data()
        try:
            self.TOKEN_INDEX = token_index + 1
            self.create_client(self.TOKEN_INDEX)
            await asyncio.sleep(2)
        except:
            self.TOKEN_INDEX = 0
            self.create_client(self.TOKEN_INDEX)
            await self.handle_flood_wait(wait_time)

    async def setup_webserver(self):
        self._web_runner = await self.web_server.setup_web_server(8443)

    async def powerup(self):
        if hasattr(self, "db"):
            self.font = self.db.Settings.get(key="font",datatype=str)
            self.sudo_users = self.db.Settings.get(key="sudo_users",datatype=list,default=[])

            if not self.font:
                logger.info("Font not set, defaulting to font 1")
                self.db.Settings.set("font", "1")
                self.font = 1

        self.load_flood_data()
        self.TOKEN_INDEX= self.get_token_index_from_flood_file()
        self.create_client(self.TOKEN_INDEX)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self._loop = asyncio.get_running_loop()
                logger.info(f'Starting bot client... (attempt {attempt + 1}/{max_retries})')
                if not self._is_connected:
                    await asyncio.wait_for(super().start(), timeout=60.0)
                    self._bot_info = await super().get_me()
                    logger.info(f"Bot Client > {self._bot_info.first_name} - @{self._bot_info.username} Started")
                    await self.setup_commands()
                    self._is_connected = True
                    await self.start_scheduler()
                    await self.handle_restart()
                    break 

            except asyncio.TimeoutError:
                logger.error(f"Bot start timed out (attempt {attempt + 1})")
                if attempt < max_retries - 1:
                    logger.info("Retrying in 10 seconds...")
                    await asyncio.sleep(10)
                
            except FloodWait as e:
                logger.error(f"FloodWait: {e.value} seconds")
                await self.change_token(self.TOKEN_INDEX,e.value)
                
            except AccessTokenExpired:
                logger.error(f"Access token expired (attempt {attempt + 1})")
                await self.change_token(self.TOKEN_INDEX, 60)
            except Exception as e:
                logger.error(f"Error starting Client (attempt {attempt + 1}): {e}")
                logger.error(traceback.format_exc())
                if attempt < max_retries - 1:
                    logger.info("Retrying in 10 seconds...")
                    await asyncio.sleep(10)
        else:
            logger.error("Failed to start bot after all retry attempts")

        await self.setup_webserver()

    async def powerdown(self, *args):
        logger.info("Initiating APP to stop...")
        if self._rename:await super().set_bot_info(lang_code='en',name=self.app_name + " (Offline)")
        self.stop_scheduler()
        today = self.TZ_now.strftime("%Y-%m-%d")
        if hasattr(self, '_web_runner') and self._web_runner:
            await self.web_server.cleanup()
        if self._is_connected:
            logger.info("Stopping bot client...")
            try:
                if self.LOGS:
                    await self.send_message(chat_id=self.LOGS, text=f"{self._bot_info.mention} stopping...")
                    await self.send_document(chat_id=self.LOGS, document=f"logs/log-{today}.txt")
                    await self.send_message(chat_id=self.LOGS, text=f"{self._bot_info.mention} stopped successfully!")
            except Exception as e:
                logger.error(f"Error sending stop notification: {e}")
            logger.info(f"{self._bot_info.first_name} - @{self._bot_info.username} Stoped")
            await super().stop()
            sys.exit(0)

    async def reboot(self):
        try:
            if self._rename:await super().set_bot_info(lang_code='en',name=self.app_name + " (restarting..)")
            logger.info("Initiating APP to reboot...")
            self.stop_scheduler()
            today = self.TZ_now.strftime("%Y-%m-%d")
            if hasattr(self, '_web_runner') and self._web_runner:
                await self.web_server.cleanup()
            if self._is_connected:
                try:
                    if self.LOGS:
                        await self.send_message(chat_id=self.LOGS, text=f"{self._bot_info.mention} rebooting...")
                        await self.send_document(chat_id=self.LOGS, document=f"logs/log-{today}.txt")
                    logger.info(f"{self._bot_info.first_name} - @{self._bot_info.username} is rebooting")
                except Exception as e:
                    logger.error(f"Error sending reboot notification: {e}")
                await super().stop()
                self._is_connected = False
            await asyncio.sleep(2)
            
            logger.info("Restarting process...")
            os.execl(sys.executable, sys.executable, *sys.argv)
        except Exception as e:
            logger.error(f"Error during reboot: {e}")
            os.execl(sys.executable, sys.executable, *sys.argv)

    async def handle_restart(self):
        if os.path.exists('restart.txt'):
            with open('restart.txt', 'r') as file:
                data = file.read().split()
                chat_id = int(data[0])
                Message_id = int(data[1])
            try:await self.send_message(chat_id=self.LOGS, text=f"{self._bot_info.mention} restarted successfully!")
            except Exception as e:logger.error(f"Failed to send restart notification: {e}")
            try:await self.edit_message_text(chat_id=chat_id,message_id=Message_id, text="Bot restarted successfully!")          
            except:
                await self.send_message(chat_id=chat_id, text="Bot restarted successfully!",reply_to_message_id=Message_id-1,)
                await self.delete_messages(chat_id=chat_id,message_ids=Message_id)
            os.remove('restart.txt')
        else:
            try:await self.send_message(chat_id=self.LOGS, text=f"{self._bot_info.mention} started successfully!")
            except Exception as e:logger.error(f"Failed to send start notification: {e}")


    async def setup_commands(self,set_commands=False):
        if self._rename:
            if self._bot_info.first_name != self.app_name:
                await super().set_bot_info(lang_code='en',name=self.app_name)
        if set_commands:
            commands = await super().get_bot_commands()
            if commands == []:
                b_index = self.TOKEN_INDEX + 1
                bot_commands = [
                    BotCommand("start", f"{b_index} Start the bot"),
                    BotCommand("help", f"{b_index} Get help"),
                    BotCommand("logs", f"{b_index} Get logs (Admin only)"),
                    BotCommand("reboot", f"{b_index} Reboot the bot (Admin only)")
                ]
                await super().set_bot_commands(bot_commands)

    async def send_logs(self):
        logger.info("Sending yesterday logs...")
        if not self._is_connected:
            logger.warning("Bot is not connected")
        if self._is_connected:
    
            yesterday = (self.TZ_now - timedelta(days=1)).strftime("%Y-%m-%d")
            try:
                m = await self.send_document(chat_id=self.LOGS, document=f"logs/log-{yesterday}.txt")
                logger.info(f"Logs sent to {m.chat.first_name} - @{m.chat.username}")
            except Exception as e:
                logger.error(f"Error sending logs: {e}")