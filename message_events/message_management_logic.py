from __future__ import annotations
import typing
from shared_vars import discord,change_confirmations,waiting_confirmations,command_prefix
from datetime import datetime, timezone,timedelta
import asyncio
import typing
from utils.typing_utils import TEMP_LOGS_PATTERN,FULLS_LOGS_PATTERN,GuildMessage,GuildContext,Initialized_Bot
if typing.TYPE_CHECKING:
    from stats_system.server_stats import Server_stats,commands
async def delete_message(message:discord.Message | GuildMessage | list[discord.Message|GuildMessage], time = 0) -> bool:
    """Deletes the given message or all the messages in the given message list.

    Args:
        message (discord.Message | list[discord.Message]): The message or list of messages to be deleted.
        time (int, optional): The amount of seconds to wait until the deletion. Defaults to 0.

    Returns:
        discord.Message | list[discord.Message] | bool: Returns either the deleted messages or False if a single message was given and failed to delete.
    """
    await asyncio.sleep(time)
    if isinstance(message, discord.Message):
        message = [message,]
    if isinstance(message, list):
        deleted_msgs = []
        for msg in message:
            if isinstance(msg, discord.Message):
                try:
                    deleted_msgs.append(await msg.delete())
                except discord.errors.NotFound:
                    continue
        return len(deleted_msgs) == message
    else:
        raise TypeError('The given argument for message was not a valid type')
@typing.overload
def log(logs:TEMP_LOGS_PATTERN,message:discord.Message,with_guild:bool=False) -> TEMP_LOGS_PATTERN: ...
@typing.overload
def log(logs:FULLS_LOGS_PATTERN,message:discord.Message,with_guild:typing.Literal[False]=False) -> FULLS_LOGS_PATTERN: ...

def log(logs:TEMP_LOGS_PATTERN|FULLS_LOGS_PATTERN,message:discord.Message,with_guild:bool = False):
    """Logs the given message in the given dictionary.

    Args:
        logs (dict): The logs dictionary to log the message in.
        message (discord.Message): The message to log.
        with_guild (bool, optional): If the guild the message was from should also be saved if not present. Defaults to False.

    Returns:
        dict: The updated logs.
    """
    if message.guild is None:
        raise ValueError('The message object does not contain a valid guild.')
    if message.author.id not in logs.keys():      
        # if with_guild:              
        #     logs[message.author.id] = typing.cast(dict[typing.Literal['guild_id'],int],{'guild_id':message.guild.id}) commented this out bcs
        #its not needed and bcs it was annoying with the type linter
        logs[message.author.id] = {}  
    if message.created_at not in logs[message.author.id].keys():
        logs[message.author.id][message.created_at]  = []
    typing.cast(list[str],logs[message.author.id][message.created_at]).append(message.content)
    return logs

async def del_old_logs(server_stats: Server_stats):
    """Deletes all the messages in the temp logs if they are older than 5 minutes.

    Args:
        server_stats (Server_stats): The server stats.
    """
    for guild_id in server_stats.stats:
        keys_to_pop = {}
        logs_temp = server_stats.stats[guild_id]['temp_logs']
        for user, messages in logs_temp.items():
            for timestamp in messages.keys():
                if timestamp == 'guild_id':
                    continue
                if not timestamp.tzinfo:
                    timestamp = timestamp.replace(tzinfo=timezone.utc)
                five_min_before = datetime.now(timezone.utc) - timedelta(minutes=3)
                if timestamp < five_min_before:
                    if user not in keys_to_pop.keys():
                        keys_to_pop[user] = [timestamp]
                    else:
                        keys_to_pop[user].append(timestamp)
        for user, time_obj in keys_to_pop.items():
            for timestamp in time_obj:
                logs_temp[user].pop(timestamp)
        server_stats.stats[guild_id]['temp_logs'] = logs_temp
    await server_stats.save_stats()

async def response_waiting(ctx:commands.Context, client: Initialized_Bot, time = 30) -> discord.Message | None:
    """Waits for a message from the same author and channel as the commands context author and channel.

    Args:
        ctx (commands.Context): The command context to compare with.
        client (Initialized_Bot): The Discord bot
        time (int, optional): The time until timeout. Defaults to 30.

    Returns:
        discord.Message | None: The sent message or None if the sent message starts with the command prefix or no message was sent in time. 
    """
    global waiting_confirmations, change_confirmations
    waiting_confirmations.append(ctx.author.id)
    def check(msg: discord.Message):
        return msg.author != client.user and msg.author == ctx.author and msg.channel == ctx.channel
    try:
        response = await client.wait_for('message', timeout=time, check=check)
        if response.content.startswith(command_prefix):
            return None
    except TimeoutError:
        await ctx.reply('You took too long to respond', delete_after = 8)
        return None
    change_confirmations.append(ctx.author.id)
    return response


async def response_waiting_text(ctx:commands.Context, client:Initialized_Bot, time=30):
    """Uses response_waiting function and returns only the content of the received message.

    Args:
        ctx (commands.Context): The command context.
        client (Initialized_Bot): The Discord bot.
        time (int, optional): The time until timeout. Defaults to 30.

    Returns:
        str | None: The message content or None if no message was returned.
    """
    response = await response_waiting(ctx,client,time=time)
    if response is None:
        return ''
    return response.content.lower()

async def response_waiting_bool(ctx:commands.Context, client:Initialized_Bot, time=30):
    """Uses response_waiting_text and returns True if the returned text either is y or yes, else False.

    Args:
        ctx (commands.Context): The command context.
        client (Initialized_Bot): The Discord bot.
        time (int, optional): The time until timeout. Defaults to 30.

    Returns:
        bool | None: The bool or None if no content was returned.
    """
    response = await response_waiting_text(ctx,client,time=time)
    if response is None:
        return False
    return response in ['y','yes']

async def send_and_response_waiting(ctx:commands.Context, client:Initialized_Bot, prompt:str, time=30):
    """Sends the given prompt and then uses the response_waiting function.

    Args:
        ctx (commands.Context): The command context.
        client (Initialized_Bot): The Discord bot.
        prompt (str): The prompt to send.
        time (int, optional): The time until timeout. Defaults to 30.

    Returns:
        discord.Message | None: The recieved message or None if no message was returned.
    """
    await ctx.send(prompt)
    response = await response_waiting(ctx,client,time)
    return response

async def send_and_response_waiting_text(ctx:commands.Context, client:Initialized_Bot, prompt:str, time=30):
    """Sends the given prompt and then uses the response_waiting function and returns only the content of the received message.

    Args:
        ctx (commands.Context): The command context.
        client (Initialized_Bot): The Discord bot.
        prompt (str): The prompt to send.
        time (int, optional): The time until timeout. Defaults to 30.

    Returns:
        str | None: The message content or None if no message was returned.
    """
    await ctx.send(prompt)
    response = await response_waiting_text(ctx,client,time)
    return response

async def send_and_response_waiting_bool(ctx:commands.Context, client:Initialized_Bot, prompt:str, time=30):
    """Sends the given prompt and uses response_waiting_text and returns True if the returned text either is y or yes, else False.

    Args:
        ctx (commands.Context): The command context.
        client (Initialized_Bot): The Discord bot.
        prompt (str): The prompt to send.
        time (int, optional): The time until timeout. Defaults to 30.

    Returns:
        bool | None: The bool or None if no content was returned.
    """
    await ctx.send(prompt)
    return await response_waiting_bool(ctx,client,time)

async def send_and_response_waiting_until_response(ctx:commands.Context, client:Initialized_Bot, prompt:str,time=30,break_on = []) -> str:
    """Sends the given prompt and uses response_waiting_text. If the message doesn't gets sent in the given time the process gets repeated.

    Args:
        ctx (commands.Context): The command context.
        client (Initialized_Bot): The discord bot.
        prompt (str): The prompt to send.
        time (int, optional): The time to wait. Defaults to 30.
        break_on (list, optional): When to return None instead of the response. Defaults to [].

    Returns:
        str | None: Returns the recieved message content if the content is not in break on.
    """
    await ctx.send(prompt)
    response = await response_waiting_text(ctx,client,time)
    if response.lower() in break_on:
        return response
    if not response:
        return await send_and_response_waiting_until_response(ctx,client,prompt,time,break_on)
    return response

@typing.overload
async def send_and_response_waiting_until_response_int(ctx:GuildContext,client:Initialized_Bot,prompt:str,time:int=30,break_on:tuple[()]=(),lower_bound:int|None=None,upper_bound:int|None=None) -> int: ...

@typing.overload
async def send_and_response_waiting_until_response_int(ctx:GuildContext,client:Initialized_Bot,prompt:str,time:int=30,break_on:list[str]=...,lower_bound:int|None=None,upper_bound:int|None=None) -> str|int: ...


async def send_and_response_waiting_until_response_int(ctx:GuildContext, client:Initialized_Bot, prompt:str,time=30,break_on:list[str]|tuple[()] = (),lower_bound:int|None=None,upper_bound:int|None=None):
    """Sends the given prompt and uses response_waiting_text. If the message doesn't gets sent in the given time the process gets repeated.

    Args:
        ctx (commands.Context): The command context.
        client (Initialized_Bot): The discord bot.
        prompt (str): The prompt to send.
        time (int, optional): The time to wait. Defaults to 30.
        break_on (list, optional): When to return None instead of the response. Defaults to [].

    Returns:
        str | None: Returns the recieved message content if the content is not in break on.
    """
    # await ctx.send(prompt)
    response = await send_and_response_waiting_int(ctx,client,prompt,time,break_on,lower_bound,upper_bound)
    if not response:
        return await send_and_response_waiting_until_response(ctx,client,prompt,time,break_on)
    return response


@typing.overload
async def send_and_response_waiting_int(ctx:GuildContext,client:Initialized_Bot,prompt:str,time:int=30,break_on:tuple[()]=(),lower_bound:int|None=None,upper_bound:int|None=None) -> int: ...

@typing.overload
async def send_and_response_waiting_int(ctx:GuildContext,client:Initialized_Bot,prompt:str,time:int=30,break_on:list[str]=...,lower_bound:int|None=None,upper_bound:int|None=None) -> str|int: ...


async def send_and_response_waiting_int(ctx:GuildContext, client:Initialized_Bot, prompt:str,time=30,break_on:list[str]|tuple[()]=(),lower_bound:int|None=None,upper_bound:int|None=None):
    """A loop that asks a number until exists 

    Args:
        prompt (str): _description_

    Returns:
        _type_: _description_
    """
    question_count = await send_and_response_waiting_text(ctx, client, prompt, time)
    question_count = question_count.rstrip('.')  
    if any(question_count.lower() == breakword for breakword in break_on):
        return question_count
    if not question_count.isdigit() or lower_bound and int(question_count) < lower_bound or upper_bound and int(question_count) > upper_bound:
        await ctx.send(f'{question_count} is not a valid input.')
        return typing.cast(int|str,await send_and_response_waiting_int(ctx,client,prompt,time,lower_bound,upper_bound,break_on=break_on))
    return int(question_count)

class Response_waiting():
    def __init__(self,ctx: GuildContext,client:Initialized_Bot,time:int=30):
        """Initialize the class with the Discord bot and the server stats. Additionaly also sets the given time and context for all messages incoming.

        Args:
            client (Initialized_Bot): The Discord Bot.
            server_stats (Server_stats): The server stats.
        """
        self.ctx = ctx
        self.client = client
        self.time = time
    
    async def send_and_response_waiting_text(self,prompt:str):
        """Does the same as send_and_response_waiting_text just uses the parameters given on class creation.

        Args:
            prompt (str): The prompt to be sent.

        Returns:
            str | None: Either the received message content or None if no message content was received.
        """
        await self.ctx.send(prompt)
        response = await response_waiting_text(self.ctx,self.client,self.time)
        return response
    
    async def send_and_response_waiting_bool(self, prompt:str):
        """Sends the given prompt and uses response_waiting_bool with the parameters given on class creation.

        Args:
            prompt (str): The prompt to be sent.

        Returns:
            str | None : The bool or None if no content was returned.
        """
        await self.ctx.send(prompt)
        response = await response_waiting_bool(self.ctx,self.client,self.time)
        return response
        
