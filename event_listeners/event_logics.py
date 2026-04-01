from shared_vars import discord, event_title,Server_stats, next_sunday,commands
import random
from datetime import datetime,timezone,timedelta
import asyncio
async def event_prep(guild:discord.Guild,server_stats:Server_stats):
    to_watch = server_stats.stats[guild.id]['to_watch']
    if not to_watch:
        return #an event should never be created then so we dont have to try and delete it.
    winner =  random.choice(list(to_watch.keys()))
    server_stats.stats[guild.id]['winner_watch'] = winner
    winner_data = to_watch.get(winner)
    all_events = await guild.fetch_scheduled_events()
    if all(event.name.lower() != event_title.lower() for event in all_events):
        return
    server_stats.stats[guild.id]['suggestions_closed'] = True
    server_stats.stats[guild.id]['winner_data'][winner] = winner_data
    event_role = discord.utils.get(guild.roles, name= 'events')
    channel = discord.utils.get(guild.channels, name= 'events')
    member = guild.get_member(winner_data.get('id'))
    if member is None:
        return
    if not event_role:
        print('Channel general chat was not found.')
        return
    await channel.send(f'{event_role.mention} The randomly selected suggestion was **{winner}** hosted by <@{member.id}>.\nThe bot doesn\'t take any more invites or suggestion removals until the end of the event.' if event_role else f'The randomly selected suggestion was **{winner}** hosted by <@{member.id}>.\nThe bot doesn\'t take any more invites or suggestion removals until the end of the event.')

async def wait_until_event(server_stats:Server_stats,client:commands.Bot):
    time_until_next_event = (next_sunday - datetime.now(timezone.utc)- timedelta(hours=1)).total_seconds() # 1 hour before event
    if time_until_next_event <= 0:
        print('Event already in the past. Error happened.')
        return
    await asyncio.sleep(time_until_next_event)
    for guild_id in server_stats.stats.keys():
        if not server_stats.stats[guild_id]['to_watch']:
            continue
        if client.get_guild(guild_id) is None:
            continue
        await event_prep(client.get_guild(guild_id),server_stats)
    await wait_until_event(server_stats=server_stats,client=client)