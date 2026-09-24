from shared_vars import discord, event_title, next_sunday
from stats_system.server_stats import Server_stats,commands
import random
from datetime import datetime,timezone,timedelta
import asyncio
import re
from utils.typing_utils import Initialized_Bot
from user_management.user_management_logic import get_member
from utils.utils import combine,channel_send

async def event_prep(guild:discord.Guild,server_stats:Server_stats):
    """Run event preparation, including:
        - choose the winning suggestion
        - close suggestions
        - update the winner data with the data of the winning suggestion
        - send a message with a ping for the role events that announces the event and the winner data.

Args:
        guild (discord.Guild): The guild where the event should happen.
        server_stats (Server_stats): The server stats.

Returns:
    None: Returns early if required data is missing or no suggestions are available.
    """
    to_watch = server_stats.stats[guild.id]['to_watch']
    if not to_watch:
        return #an event should never be created then so we dont have to try and delete it.
    winner =  random.choice(list(to_watch.keys()))
    winner_data = to_watch[winner]
    all_events = await guild.fetch_scheduled_events()
    if all(event.name.lower() != event_title.lower() for event in all_events):
        return
    server_stats.stats[guild.id]['suggestions_closed'] = True
    server_stats.stats[guild.id]['to_watch'][winner] = winner_data
    event_role = discord.utils.get(guild.roles, name= 'events')
    channel = discord.utils.get(guild.channels, name= 'events')
    member = await get_member(guild,winner_data.get('id'))
    if member is None: 
        return
    if not event_role:
        print('Channel general chat was not found.')
        return
    if not channel:
        return
    await channel_send(channel,f'{event_role.mention} The randomly selected suggestion was **{winner}** hosted by <@{member.id}>.\nThe bot doesn\'t take any more invites or suggestion removals until the end of the event.' if event_role else f'The randomly selected suggestion was **{winner}** hosted by <@{member.id}>.\nThe bot doesn\'t take any more invites or suggestion removals until the end of the event.')


async def wait_until_event(server_stats:Server_stats,client:Initialized_Bot):
    """Counts down until event start.

    Args:
        server_stats (Server_stats): The server stats.
        client (Initialized_Bot): The discord bot.
    """
    time_until_next_event = (next_sunday - datetime.now(timezone.utc)- timedelta(hours=1)).total_seconds() # 1 hour before event
    if time_until_next_event <= 0:
        print('Event already in the past. Error happened.')
        return
    await asyncio.sleep(time_until_next_event)
    for guild_id in server_stats.stats.keys():
        if not server_stats.stats[guild_id]['to_watch']:
            continue
        guild = client.get_guild(guild_id)
        if guild is None:
            continue
        await event_prep(guild,server_stats)
    await wait_until_event(server_stats=server_stats,client=client)

def create_msg(member:discord.Member, messasge:str):
    guild = member.guild
    msg_types = {     'welcome' :'{} {} to the {} server.',
                        'goodbye':'{} {} we are sorry to see you go.'    
                }
    results, second_results = fuzzy_get(messasge,msg_types)
    if not results and not second_results:
        return combine('There were ', print)

def fuzzy_get(key:str,dictionary:dict,default = None):#TODO Rename this function
    if not isinstance(key,str) or not isinstance(dictionary,dict):
        return default, default
    words = re.split(r'\b',key)
    results = []
    second_results = []
    for word in words:
        for version in (word, word.lower(),word.upper()):
            result = dictionary.get(version)
            if result:
                results.append(result)
                break
            for key in dictionary.keys():
                if key in word:
                    second_results.append(dictionary.get(key))
                    break
    return results, second_results
        


    