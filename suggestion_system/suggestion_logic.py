from shared_vars import discord, Server_stats, event_title
def is_member_hosting(member:discord.Member,server_stats:Server_stats)->tuple[bool,str|None]:
    for watch_name, watch_data in server_stats.stats[member.guild.id]['to_watch'].items():
        if watch_data.get('id') == member.id:
            return True, watch_name
    return False, None

async def remove_suggestion_logic(suggestion:str,guild:discord.Guild,server_stats:Server_stats):
    server_stats.stats[guild.id]['to_watch'].pop(suggestion)
    to_watch = server_stats.stats[guild.id]['to_watch']
    server_stats.save_stats()
    if not to_watch.get(suggestion):
        if not to_watch:
            all_events = await guild.fetch_scheduled_events()
            for event in all_events:
                if event.name.lower() == event_title.lower():
                    await event.delete()
                    return True
        return True
    return False

