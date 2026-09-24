from __future__ import annotations
import pyperclip
from typing import TypeVar,TYPE_CHECKING
import discord
from colorama import Fore
from datetime import datetime,time
from discord.ext import commands
from shared_vars import admin_channel_name
if TYPE_CHECKING:
    from datetime import date
    from types import FunctionType
    
T = TypeVar('T')

def copy_to_clipboard(text:str):
    if not isinstance(text,str):
        try:
            raise TypeError(f'The given argument needed to be of type str but the type given was {type(text).__name__}')
        except AttributeError:
            raise TypeError(f'The given argument needed to be of type str but the another type was given.')
    pyperclip.copy(text)
    return text

def combine(value:T,*funcs:FunctionType) -> T:
    """Uses the given value in all given functions and returns the given value.

    Args:
        value (Any): The value given to the functions.
    """
    for func in funcs:
        if not hasattr(func,'__call__'):
            continue
        try:
            func(value)
        except Exception:
            continue
    return value

def make_datetime(date:date):
    return datetime.combine(date,time())


async def channel_send(channel:discord.abc.GuildChannel,msg:str):
    if not isinstance(channel,discord.abc.Messageable):
        # raise TypeError('Messages can\'t be sent in the given channel.')
        return
    return await channel.send(msg)

def red_print(*args,**kwargs):
    """Runs the print function with all the given positional arguments and keyword arguments but prints the text in red.
    """
    print(Fore.RED)
    print(*args,**kwargs)
    print(Fore.RESET)

def date_level_get(key:datetime,dictionary:dict) -> list:
    """Searches all values that use the same date in their key as the given key.

    Args:
        key (datetime): The key to search values for.
        dictionary (dict): The dict to search all values from.

    Returns:
        list: The list containing the found values 
    """
    vals = []
    for k,v in dictionary.items():
        if not isinstance(k,datetime):
            continue
        if k.date() == key.date():
            vals.append(v)
    return vals

async def dynamic_send(sendable:commands.Context|discord.Interaction,to_send:str|None=None,hide=True,*args,**kwargs):
    if isinstance(sendable,discord.Interaction):
        await sendable.response.send_message(to_send,ephemeral=hide,*args,**kwargs)
    elif sendable.interaction:
        return await dynamic_send(sendable.interaction,to_send,hide=hide,*args,**kwargs)
    else:
        await sendable.reply(to_send,*args,**kwargs)

if __name__ == '__main__':
    text = None
    try:
        copy_to_clipboard(text)#type:ignore
    except TypeError as e:
        print(e)
    text = 'Hello World'
    print(copy_to_clipboard(text))
    combine(text,copy_to_clipboard,print)

def get_messageable_channel(channel_name:str,guild:discord.Guild):
    return discord.utils.get((channel for channel in guild.channels if isinstance(channel, discord.abc.Messageable)),name=channel_name)

def get_admin_channel(guild:discord.Guild):
    return get_messageable_channel(admin_channel_name,guild)
