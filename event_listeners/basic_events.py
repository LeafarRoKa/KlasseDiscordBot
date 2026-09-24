from shared_vars import discord, event_title
from stats_system.server_stats import Server_stats,commands
from user_management.user_management_logic import give_role_logic
from suggestion_system.suggestion_logic import is_member_hosting, remove_suggestion_logic
from event_listeners.event_logics import event_prep
from utils.typing_utils import Initialized_Bot
import typing
class Basic_events(commands.Cog):
    
    def __init__(self, client:Initialized_Bot,server_stats:Server_stats):
        """Initialize the class with the discord bot and the server stats.

        Args:
            client (Initialized_Bot): The discord Bot.
            server_stats (Server_stats): The server stats.
        """
        self.client = client
        self.server_stats = server_stats
        
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Gets called when a member joines a guild. Sends a welcome message and adds the member to the stats. Adds the lowest role to the member.

        Args:
            member (discord.Member): The member that joined.
        """
        if typing.cast(discord.ClientUser,self.client.user).id == member.id:
            return
        guild = member.guild
        if self.server_stats.stats[guild.id].get('set_up') is not None and self.server_stats.stats[guild.id].get('set_up') is False:
            return
        channel =  discord.utils.get(guild.channels, name= 'welcome')#welcome channel
        if isinstance(channel,discord.TextChannel):
            await channel.send(f'Welcome <@{member.id}> to the {guild.name} server!')
        role = discord.utils.get(guild.roles, name=next(name for name,value in self.server_stats.stats[guild.id]['roles_requirements'].items() if value['pos'] == 0)) 
        if not role:
            print(f'An error occoured while trying to give a role to a new member called {member.display_name} in the server {member.guild.name}.')
            return
        await give_role_logic(member, role)
        self.server_stats.is_dict_complete()
        

    @commands.Cog.listener()
    async def on_member_remove(self, member:discord.Member):
        """Called when a member leaves a guild. Sends a goodbye message and removes suggestion if the member has one.

        Args:
            member (discord.Member): The member that left.
        """
        if not self.client.user:#if not set up
            return
        if member.id == self.client.user.id:
            return
        guild = member.guild
        if self.server_stats.stats[guild.id].get('set_up') is not None and self.server_stats.stats[guild.id].get('set_up') is False:
            return
        channel = discord.utils.get(guild.channels, name = 'goodbye')
        if channel and isinstance(channel,discord.TextChannel):
            await channel.send(f'Bye <@{member.id}> we are sorry to see you go.')
        is_hosting, suggestion = is_member_hosting(member,self.server_stats)
        if is_hosting:
            is_removed = await remove_suggestion_logic(typing.cast(str,suggestion),member.guild, self.server_stats)
            if is_removed is False:
                print('An error occoured when trying to remove a member that left from the suggestion list. Function: on_member_remove.')

    
    @commands.Cog.listener()
    async def on_member_update(self,before: discord.Member, after: discord.Member):
        """Called when a member's profile changes. Updates user stats role if roles were changed.

        Args:
            before (discord.Member): The member before changes.
            after (discord.Member): The member after changes.
        """
        guild = before.guild
        if not any(after.id == member.id for member in guild.members):
            return
        if self.server_stats.stats[guild.id].get('set_up') is not None and self.server_stats.stats[guild.id].get('set_up') is False:
            return
        if before.roles != after.roles:
            self.server_stats.stats[guild.id]['user_stats'].update_rank(after)

    @commands.Cog.listener()
    async def on_scheduled_event_update(self,event_before:discord.ScheduledEvent, event_after:discord.ScheduledEvent):
        """Called when a guild scheduled event is updated. Makes the following changes if the bot event is affected:
            - if the event is completed:
                - resets:
                    - The suggestions
                    - Winner data
                    - winning user 
                    - winner suggestion 

                - opens the suggestions
                
            - if the event is active:
                - runs event preparation
                - sets the winner user and data to 1

Args:
    event_before (discord.ScheduledEvent): The event before changes.
    event_after (discord.ScheduledEvent): The event after changes.
        """
        guild = event_after.guild
        if not guild:
            return
        if self.server_stats.stats[guild.id].get('set_up') is not None and self.server_stats.stats[guild.id].get('set_up') is False:
            return
        if event_before.name.lower() != event_title.lower():
            return
        if event_after.status.name == 'completed':
            self.server_stats.stats[event_after.guild_id]['to_watch'] = {}
            self.server_stats.stats[event_after.guild_id]['suggestions_closed'] = False
            await self.server_stats.save_stats()
        elif event_after.status.name == 'active':
            if not self.server_stats.stats[event_after.guild_id]['to_watch']:
                await event_prep(guild,self.server_stats)

    @commands.Cog.listener()
    async def on_guild_join(self,guild:discord.Guild):
        """Called when the bot gets added to a guild. Adds the guild to the server stats. 

        Args:
            guild (discord.Guild): Guild where the bot was added.
        """
        if guild.id not in self.server_stats.stats:# .keys() is actually slower bcs dicts have already an implemented function 
            #for checking if smth is in the dict
            self.server_stats.is_dict_complete()
            self.server_stats.stats[guild.id]['set_up'] = False
        else:
            self.server_stats.add_guild(guild.id)

    @commands.Cog.listener()
    async def on_guild_remove(self,guild:discord.Guild):
        """Called when the bot gets removed from a guild. Sets the value set_up to False for that guild.

        Args:
            guild (discord.Guild): Guild the bot was removed from.
        """
        # self.server_stats.stats[guild.id]['set_up'] = False
        self.server_stats.remove_guild(guild.id)
        