from shared_vars import discord, commands,change_confirmations,waiting_confirmations,command_prefix, Server_stats
from datetime import datetime, timezone,timedelta
import asyncio
from colorama import Fore
async def delete_message(message:discord.Message | list[discord.Message], time = 0) -> discord.Message | list[discord.Message] | bool:
    """Deletes the given message or all the messages in the given message list.

    Args:
        message (discord.Message | list[discord.Message]): The message or list of messages to be deleted.
        time (int, optional): The amount of seconds to wait until the deletion. Defaults to 0.

    Returns:
        discord.Message | list[discord.Message] | bool: Returns either the deleted messages or False if a single message was given and failed to delete.
    """
    await asyncio.sleep(time)
    if isinstance(message, discord.Message):
        try:
            return await message.delete()
        except discord.errors.NotFound:
            return False
    if isinstance(message, list):
        deleted_msgs = []
        for msg in message:
            if isinstance(msg, discord.Message):
                try:
                    deleted_msgs.append(await msg.delete())
                except discord.errors.NotFound:
                    continue
        return deleted_msgs
                
    else:
        print('The given argument for message was not a valid type')
        return None
    
def log(logs:dict,message:discord.Message,with_guild = False):
    """Logs the given message in the given dictionary.

    Args:
        logs (dict): The logs dictionary to log the message in.
        message (discord.Message): The message to log.
        with_guild (bool, optional): If the guild the message was from should also be saved if not present. Defaults to False.

    Returns:
        dict: The updated logs.
    """
    if message.author.id not in logs.keys():                    
        logs[message.author.id] = {'guild_id':message.guild.id} if with_guild else {}  
    if message.created_at not in logs[message.author.id].keys():
        logs[message.author.id][message.created_at]  = []
    logs[message.author.id][message.created_at].append(message.content)
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
                timestamp : datetime
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

async def response_waiting(ctx:commands.Context, client: commands.Bot, time = 30):
    """Waits for a message from the same author and channel as the commands context author and channel.

    Args:
        ctx (commands.Context): The command context to compare with.
        client (commands.Bot): The Discord bot
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


async def response_waiting_text(ctx:commands.Context, client:commands.Bot, time=30):
    """Uses response_waiting function and returns only the content of the received message.

    Args:
        ctx (commands.Context): The command context.
        client (commands.Bot): The Discord bot.
        time (int, optional): The time until timeout. Defaults to 30.

    Returns:
        str | None: The message content or None if no message was returned.
    """
    response = await response_waiting(ctx,client,time=time)
    if response is None:
        return ''
    return response.content.lower()

async def response_waiting_bool(ctx:commands.Context, client:commands.Bot, time=30):
    """Uses response_waiting_text and returns True if the returned text either is y or yes, else False.

    Args:
        ctx (commands.Context): The command context.
        client (commands.Bot): The Discord bot.
        time (int, optional): The time until timeout. Defaults to 30.

    Returns:
        bool | None: The bool or None if no content was returned.
    """
    response = await response_waiting_text(ctx,client,time=time)
    if response is None:
        return False
    return response in ['y','yes']

async def send_and_response__waiting(ctx:commands.Context, client:commands.Bot, prompt:str, time=30):
    """Sends the given prompt and then uses the response_waiting function.

    Args:
        ctx (commands.Context): The command context.
        client (commands.Bot): The Discord bot.
        prompt (str): The prompt to send.
        time (int, optional): The time until timeout. Defaults to 30.

    Returns:
        discord.Message | None: The recieved message or None if no message was returned.
    """
    await ctx.send(prompt)
    response = await response_waiting(ctx,client,time)
    return response

async def send_and_response_waiting_text(ctx:commands.Context, client:commands.Bot, prompt:str, time=30):
    """Sends the given prompt and then uses the response_waiting function and returns only the content of the received message.

    Args:
        ctx (commands.Context): The command context.
        client (commands.Bot): The Discord bot.
        prompt (str): The prompt to send.
        time (int, optional): The time until timeout. Defaults to 30.

    Returns:
        str | None: The message content or None if no message was returned.
    """
    await ctx.send(prompt)
    response = await response_waiting_text(ctx,client,time)
    return response

async def send_and_response_waiting_bool(ctx:commands.Context, client:commands.Bot, prompt:str, time=30):
    """Sends the given prompt and uses response_waiting_text and returns True if the returned text either is y or yes, else False.

    Args:
        ctx (commands.Context): The command context.
        client (commands.Bot): The Discord bot.
        prompt (str): The prompt to send.
        time (int, optional): The time until timeout. Defaults to 30.

    Returns:
        bool | None: The bool or None if no content was returned.
    """
    await ctx.send(prompt)
    response = await response_waiting_bool(ctx,client,time)
    return response

async def send_and_response_waiting_until_response(ctx:commands.Context, client:commands.Bot, prompt:str,time=30,break_on = []):
    """Sends the given prompt and uses response_waiting_text. If the message doesn't gets sent in the given time the process gets repeated.

    Args:
        ctx (commands.Context): The command context.
        client (commands.Bot): The discord bot.
        prompt (str): The prompt to send.
        time (int, optional): The time to wait. Defaults to 30.
        break_on (list, optional): When to return None instead of the response. Defaults to [].

    Returns:
        str | None: Returns the recieved message content if the content is not in break on.
    """
    await ctx.send(prompt)
    response = await response_waiting_text(ctx,client,time)
    if response.lower() in break_on:
        return
    if not response:
        return await send_and_response_waiting_until_response(ctx,client,prompt,time,break_on)
    return response
class Response_waiting():
    def __init__(self,ctx:commands.Context,client:commands.Bot,time:int=30):
        """Initialize the class with the Discord bot and the server stats. Additionaly also sets the given time and context for all messages incoming.

        Args:
            client (commands.Bot): The Discord Bot.
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
        if isinstance(key,datetime):
            key = key.date()
        if k.date() == key:
            vals.append(v)
    return vals