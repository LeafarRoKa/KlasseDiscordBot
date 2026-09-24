from shared_vars import discord,waiting_list
from stats_system.server_stats import Server_stats,commands
from discord.ext import tasks
from datetime import datetime, timezone
from user_management.user_management_logic import promote
from utils.typing_utils import Initialized_Bot
from user_management.user_management_logic import get_member
class Basic_tasks(commands.Cog):
    async def __init__(self, client:Initialized_Bot,server_stats:Server_stats):
        """Initialize the class with the discord bot and the server stats. Additionally starts tasks when the bot is ready.

        Args:
            client (Initialized_Bot): The discord Bot.
            server_stats (Server_stats): The server stats.
        """
        self.client = client
        self.server_stats = server_stats
        await self.client.wait_until_ready()
        self.is_waiting_expired.start()
        self.is_dict_overflow.start()

    @tasks.loop(seconds=10)
    async def is_dict_overflow(self):
        for guild_id in self.server_stats.stats:
            FULL_LOGS = self.server_stats.stats[guild_id]['full_logs']
            while len(FULL_LOGS) > 500:
                FULL_LOGS.pop(next(iter(FULL_LOGS)))#removes the first entered key value pair
            save_full_logs = {}
            for time_obj, user_msgs_at_time in FULL_LOGS.items():
                time_obj = str(time_obj)
                if time_obj not in save_full_logs.keys():
                    save_full_logs[time_obj] = {}
                for user, msgs in user_msgs_at_time.items():
                    user = str(user)
                    save_full_logs[time_obj][user] = msgs
            self.server_stats.stats[guild_id]['full_logs'] = FULL_LOGS
        
    @tasks.loop(seconds= 10)
    async def is_waiting_expired(self):
        global waiting_list
        members_to_remove = []  
        for member in waiting_list:
            guild = self.client.get_guild(waiting_list[member]['guild'])
            if guild is None:
                members_to_remove.append(member)
                continue
            member_obj = await get_member(guild,member)
            if waiting_list[member]['time'] <= datetime.now(timezone.utc):
                spammer = discord.utils.get(guild.roles, name='spammer')
                new_role = discord.utils.get(guild.roles, name=self.server_stats.user_stats(guild).stats[member].get('role_before_spam',''))
                self.server_stats.user_stats(guild).stats[member].pop('role_before_spam')
                if new_role is None or spammer is None:
                    self.server_stats.stats[guild.id]['set_up'] = False
                    return
                if member_obj is None:
                    raise ValueError('A Member has to be Valid if in the Server stats else its not deleted on leave.')
                await self.server_stats.save_stats()
                await promote(spammer,new_role, member_obj,self.server_stats)
                members_to_remove.append(member)

        for member in members_to_remove:
            waiting_list.pop(member)