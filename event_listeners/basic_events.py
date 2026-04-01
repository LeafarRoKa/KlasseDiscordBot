from shared_vars import commands, Server_stats,discord, event_title
from user_management.user_management_logic import give_role_logic
from suggestion_system.suggestion_logic import is_member_hosting, remove_suggestion_logic
from event_listeners.event_logics import event_prep
class Basic_events(commands.Cog):
    def __init__(self, client:commands.Bot,server_stats:Server_stats):
        self.client = client
        self.server_stats = server_stats
        
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if self.client.user.id == member.id:
            return
        guild = member.guild
        if self.server_stats.stats[guild.id].get('set_up') is not None and self.server_stats.stats[guild.id].get('set_up') is False:
            return
        channel =  discord.utils.get(guild.channels, name= 'welcome')#welcome channel
        await channel.send(f'Welcome <@{member.id}> to the {guild.name} server!')
        role = discord.utils.get(guild.roles, name = self.server_stats.stats[guild.id].get('server_roles').get(1)) 
        if not role:
            print(f'An error occoured while trying to give a role to a new member called {member.display_name} in the server {member.guild.name}.')
            return
        await give_role_logic(member, role)
        self.server_stats.is_dict_complete()

    @commands.Cog.listener()
    async def on_member_remove(self, member:discord.Member):
        if member.id == self.client.user.id:
            return
        guild = member.guild
        if self.server_stats.stats[guild.id].get('set_up') is not None and self.server_stats.stats[guild.id].get('set_up') is False:
            return
        channel = discord.utils.get(guild.channels, name = 'goodbye')
        await channel.send(f'Bye <@{member.id}> we are sorry to see you go.')
        is_hosting, suggestion = is_member_hosting(member,self.server_stats)
        if is_hosting:
            is_removed = await remove_suggestion_logic(suggestion,member.guild, self.server_stats)
            if is_removed is False:
                print('An error occoured when trying to remove a member that left from the suggestion list. Function: on_member_remove.')

    
    @commands.Cog.listener()
    async def on_member_update(self,before: discord.Member, after: discord.Member):
        guild = before.guild
        if not any(after.id == member.id for member in guild.members):
            return
        if self.server_stats.stats[guild.id].get('set_up') is not None and self.server_stats.stats[guild.id].get('set_up') is False:
            return
        if before.roles != after.roles:
            self.server_stats.stats[guild.id]['user_stats'].update_rank(after,self.server_stats.stats[guild.id]['server_roles'])

    @commands.Cog.listener()
    async def on_scheduled_event_update(self,event_before:discord.ScheduledEvent, event_after:discord.ScheduledEvent):
        guild = event_after.guild
        if self.server_stats.stats[guild.id].get('set_up') is not None and self.server_stats.stats[guild.id].get('set_up') is False:
            return
        if event_before.name.lower() != event_title.lower():
            return
        if event_after.status.name == 'completed':
            self.server_stats.stats[event_after.guild.id]['to_watch'] = {}
            self.server_stats.stats[event_after.guild.id]['winner_data'] = {}
            self.server_stats.stats[event_after.guild.id]['suggestions_closed'] = False
            self.server_stats.stats[event_after.guild.id]['winner_user'] = None
            self.server_stats.stats[event_after.guild.id]['winner_watch'] = None
            self.server_stats.save_stats()
        elif event_after.status.name == 'active':
            if not self.server_stats.stats[event_after.guild.id]['winner_data']:
                await event_prep(event_after.guild,self.server_stats)
            self.server_stats.stats[event_after.guild.id]['winner_user'] = 1
            self.server_stats.stats[event_after.guild.id]['winner_watch'] = 1

    @commands.Cog.listener()
    async def on_guild_join(self,guild):
        self.server_stats.is_dict_complete()
        self.server_stats.stats[guild.id]['set_up'] = False

    @commands.Cog.listener()
    async def on_guild_remove(self,guild):
        self.server_stats.stats[guild.id]['set_up'] = False
        #TODO Add expiration date for the data