from shared_vars import discord, commands,change_confirmations,waiting_confirmations,logs_temp
from datetime import datetime, timezone,timedelta
import asyncio

async def delete_message(message:discord.Message | list[discord.Message], time = 0):
    """
    Docstring for delete_message
    
    :param message: discord.Message or list containing discord.Message
    :param time: Amount of seconds waiting before deletion.
    """
    if time != 0:
        await asyncio.sleep(time)
    if isinstance(message, discord.Message):
        await message.delete()
        return
    if isinstance(message, list):
        for msg in message:
            if isinstance(msg, discord.Message):
                deleted_message = await msg.delete()
                return deleted_message
    else:
        print('The given argument for message was not a valid type')
        return None

def del_old_logs():
    global logs_temp
    keys_to_pop = {}
    for user, messages in logs_temp.items():
        for timestamp in messages.keys():
            if timestamp == 'guild_id':
                continue
            five_min_before = datetime.now(timezone.utc) - timedelta(minutes=3)
            if timestamp < five_min_before:
                if user not in keys_to_pop.keys():
                    keys_to_pop[user] = [timestamp]
                else:
                    keys_to_pop[user].append(timestamp)
    for user, time_obj in keys_to_pop.items():
        for timestamp in time_obj:
            logs_temp[user].pop(timestamp)

async def response_waiting(ctx:commands.Context, client: commands.Bot, time = 30):
    global waiting_confirmations, change_confirmations
    waiting_confirmations.append(ctx.author.id)
    def check(msg: discord.Message):
        return  msg.author != client.user and msg.author == ctx.author and msg.channel == ctx.channel
    try:
        response = await client.wait_for('message', timeout=time, check=check)
    except TimeoutError:
        await ctx.reply('You took too long to respond', delete_after = 8)
        return None
    change_confirmations.append(ctx.author.id)
    return response


async def response_waiting_text(ctx:commands.Context, client:commands.Bot, time=30):
    response = await response_waiting(ctx,client,time=time)
    if response is None:
        return ''
    return response.content.lower()

async def confirmation(ctx:commands.Context, client:commands.Bot, time=30):
    response = await response_waiting_text(ctx,client,time=time)
    if response is None:
        return False
    return response in ['y','yes']