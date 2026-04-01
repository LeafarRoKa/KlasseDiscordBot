from shared_vars import commands, Server_stats, discord, event_title, event_description,next_sunday
from suggestion_system.suggestion_logic import is_member_hosting, remove_suggestion_logic
from message_events.message_management import response_waiting,delete_message
from message_events.message_events import check_slurs_without_punishment
from datetime import timezone, timedelta
class Suggestion_cmds(commands.Cog):
    def __init__(self, client:commands.Bot,server_stats:Server_stats):
        self.client = client
        self.server_stats = server_stats
    @commands.command(help='This events removes your suggestion from the event suggestions.',brief='Removes your suggestion.')
    async def remove_suggestion(self,ctx:commands.Context):
        if self.server_stats.stats[ctx.guild.id]['suggestions_closed']:
            await ctx.send('Suggestions removals are closed until the upcoming event is over.')
            return
        guild = ctx.guild
        is_hosting, watch_name = is_member_hosting(ctx.author, self.server_stats)
        if not is_hosting:
            await ctx.reply('You are currently not hosting anything')
            return
        await ctx.send('Are you sure that you want to remove your suggestion?(y/n)')
        response = await response_waiting(ctx, self.client)
        if response == None:
            return
        if response.content.lower() in ['y','yes']:
            is_removed = await remove_suggestion_logic(watch_name,guild, self.server_stats)
            if is_removed:
                await ctx.reply('You were successfully removed from the watch suggestions.')
            
    @commands.command(help='This cmd adds your suggestion to the events suggestions.',brief='Adds your suggestion.')
    async def suggest(self,ctx: commands.Context, watch_name:str, takes_time:int = 2):
        guild = ctx.guild
        if guild.id not in self.server_stats.stats.keys():
            return
        if self.server_stats.stats[guild.id]['suggestions_closed']:
            await ctx.send('Suggestion are closed until the upcoming event is over.')
            return
        global next_sunday
        to_watch = self.server_stats.stats[guild.id]['to_watch']
        watch_name = watch_name.lower()
        is_slur,_,_ = await check_slurs_without_punishment(ctx,watch_name)
        if is_slur:
            return
        is_hosting,_ = is_member_hosting(ctx.author, self.server_stats)
        if is_hosting:
            await ctx.send('You are already hosting an event.\nYou can\'t host multiple events at the same time.')
            return
        if watch_name in to_watch.keys():
            member = ctx.guild.get_member(to_watch.get(watch_name).get('id'))
            if member is None:
                display_name = await self.client.fetch_user(to_watch.get(watch_name).get('id'))
            display_name = member.display_name
            watch_time = to_watch.get(watch_name).get('watch_date')
            await ctx.send(f'{watch_name} is already being hosted by {display_name} at {watch_time.strftime('%d.%m.%Y')}.\nYou can\'t suggest to host the same thing.')
            return
        await ctx.send('Do you want to host it this weekend (You will have to set up what you proposed next sunday) (y/n)?')
        response = await response_waiting(ctx, self.client)
        if response is None:
                    return
        if response.content.lower() in ['y','yes']:
            next_sunday = next_sunday.replace(tzinfo=timezone.utc)#next sunday replace timezone information with utc timezone
            channel = discord.utils.get(guild.voice_channels, name= 'General')
            self.server_stats.stats[guild.id]['to_watch'][watch_name] = {'watch_date': next_sunday,
                                    'id': ctx.author.id}
            await ctx.reply(f'You are now applied to host **{watch_name}** next sunday.')
            self.server_stats.save_stats()
            all_events = await guild.fetch_scheduled_events()
            for event in all_events:
                if event.name.lower() == event_title.lower():
                    return
            await guild.create_scheduled_event(name=event_title,start_time = next_sunday, 
                                            end_time = next_sunday+timedelta(takes_time),
                                            entity_type=discord.EntityType.voice,description = event_description,
                                            privacy_level=discord.PrivacyLevel.guild_only,
                                            channel = channel)#guild only makes it so that only server members can participate in this event. Else you could see the server in discovery and before accepting rules etc just participate in the event.
        elif response.content.lower() in ['n', 'no']:
            await ctx.reply('Sorry but you can\'t propose something and then not host it. If you want you can try to convince someone else to do it for you.')

    @commands.command()
    async def my_suggestion(self,ctx:commands.Context):
        _,suggestion = is_member_hosting(ctx.author,server_stats=self.server_stats)
        if not suggestion:
            await ctx.reply(f'You do not have any current suggestion.',delete_after=5)
            await delete_message(ctx.message,time=5)
            return
        await ctx.reply(f'You current suggestion is: **{suggestion}**')