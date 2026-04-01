from shared_vars import commands, Server_stats, discord,full_logs,save_data
from discord.ext import tasks
from datetime import datetime, timezone
from user_management.user_management_logic import promote
class Basic_tasks(commands.Cog):
    async def __init__(self, client:commands.Bot,server_stats:Server_stats):
        self.client = client
        self.server_stats = server_stats
        await self.client.wait_until_ready
        self.is_waiting_expired.start()
        self.is_dict_overflow.start()

    @tasks.loop(seconds=10)
    async def is_dict_overflow():
        global full_logs
        while len(full_logs) > 500:
            full_logs.pop(next(iter(full_logs)))#removes the first entered key value pair
        save_full_logs = {}
        for time_obj, user_msgs_at_time in full_logs.items():
            time_obj = str(time_obj)
            if time_obj not in save_full_logs.keys():
                save_full_logs[time_obj] = {}
            for user, msgs in user_msgs_at_time.items():
                user = str(user)

                save_full_logs[time_obj][user] = msgs
        save_data('logs',full_logs)
    @tasks.loop(seconds= 10)
    async def is_waiting_expired(self):
        global waiting_list
        members_to_remove = []  
        for member in waiting_list:
            guild = self.client.get_guild(waiting_list[member]['guild'])
            member_obj = guild.get_member(member)
            if waiting_list[member]['time'] <= datetime.now(timezone.utc):
                spammer = discord.utils.get(guild.roles, name = 'spammer')
                new_role = discord.utils.get(guild.roles, name=  self.server_stats.user_stats(guild).stats[member]['role_before_spam'])
                self.server_stats.user_stats(guild).stats[member].pop('role_before_spam')
                self.server_stats.save_stats()
                await promote(spammer,new_role, member_obj,self.server_stats)
                members_to_remove.append(member)

        for member in members_to_remove:
            waiting_list.pop(member)