import os
import asyncio
import functools

from typing import Union
from pyrogram import Client 
from d4rk.Logs import setup_logger
from pyrogram.types import Message , CallbackQuery , ChatPrivileges

from ._delete import delete
from ._ractions import Reacts
from dotenv import load_dotenv
load_dotenv()

logger = setup_logger(__name__)

OWNER = int(os.getenv("OWNER", 7859877609))

def authorize(sudo=True,admin=False,delete_command=True, react=True,react_emoji:Reacts=Reacts.fire,alert=True,permission=None):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(client: Client, message: Union[Message,CallbackQuery]):
            try:
                user = message.from_user
                if not user:
                    logger.warning(f"Unauthorized access attempt from non-user message: {message}")
                me = await client.get_me()
                is_admin = False
                if admin:
                    if message.chat.type.name.lower() in ["group","supergroup"]:
                        role = await client.get_chat_member(message.chat.id, user.id)
                        myrole = await client.get_chat_member(message.chat.id, me.id)
                        if (user_admin:= role.status.name.lower() in ["creator", "administrator","owner"]) and (i_am_admin:=myrole.status.name.lower() in ["creator", "administrator","owner"]):
                            if permission:
                                privileges = getattr(role, "privileges", None)
                                myprivileges = getattr(myrole, "privileges", None)
                                if privileges and myprivileges:
                                    has_permission = getattr(privileges, permission, False)
                                    has_my_permission = getattr(myprivileges, permission, False)
                                    if has_permission and has_my_permission:
                                        is_admin = True
                                    else:
                                        msg = ""
                                        if not has_permission and not has_my_permission:msg = f"❌ Neither you nor I "
                                        elif not has_permission:msg = f"❌ You don't"
                                        elif not has_my_permission:msg = f"❌ I don't"
                                        msg += f" have the required permission: `{permission}`."
                                        return await client.send_alert(message=message,text=msg)
                            else:is_admin = True
                    else:
                        if alert:
                            return await client.send_alert(message=message,text="❌ This command can only be used in groups.")
                        
                authorized = user.id == OWNER or (sudo and user.id in client.sudo_users) or is_admin
                if react and isinstance(message, Message):
                    try:await message.react(react_emoji)
                    except:pass
                
                if not authorized:
                    logger.warning(f"Unauthorized {func.__name__} request from user {user.id} @{user.username}")
                    if alert:
                        m = await client.send_alert(message=message,text="❌ Unauthorized access.")
                        if react and isinstance(message, Message):
                            await message.react(Reacts.shit)
                            if m:await delete(client, message.chat.id, m.id, timeout=5)
                
                else:
                    logger.info(f"Authorized user {user.id} executing {func.__name__}")
                    await func(client, message)
                if delete_command:
                    try:await delete(client, message.chat.id, message.id, timeout=5)
                    except:pass
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
            return
        return wrapper
    return decorator

