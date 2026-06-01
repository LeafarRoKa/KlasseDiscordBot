from shared_vars import commands, Server_stats, discord
from message_events.message_events_logic import sort_by_newest
from io import StringIO
from datetime import date
import re
from message_events.message_management_logic import date_level_get
class Message_management(commands.Cog):
    def __init__(self, client:commands.Bot,server_stats:Server_stats):
        """Initialize the class with the Discord bot and the server stats. 

        Args:
            client (commands.Bot): The Discord Bot.
            server_stats (Server_stats): The server stats.
        """
        self.client = client
        self.server_stats = server_stats

    @commands.command(help='This cmd gives the logs for the given user. You can also give a certain amount of msgs that it will show.',brief='Returns the logs.',)
    @commands.has_permissions(manage_messages=True)
    async def logs(self, ctx : commands.Context , filter:discord.Member | str , amount:int = 100, sorting: bool = True): # completed Make it so that it works and only gives the logs of a certain person or of a certain amount not the full logs
        """Get the logs of the guild the command was sent in. Can be filtered by date or member.

        Args:
            ctx (commands.Context): The context the command was called with.
            filter (discord.Member | str): What to filter with either a date string or a discord member.
            amount (int, optional): The amount of sent messages. Defaults to 100.
            sorting (bool, optional): If the messages should be sorted by member. Defaults to True.
        """
        date_str = None
        mbr = None
        if isinstance(filter,discord.Member):
            mbr  = filter
        else:
            date_str = filter.strip('\'')
        FULL_LOGS = self.server_stats.stats[ctx.guild.id]['full_logs']
        counter = 0
        readable_logs = ''
        date_obj = ''
        if date_str:
            if len(date_str) <= 4 or not date_str[-4:].isdigit() or not bool(not re.sub(r'[0-3]\d-[0-1]\d-\d{4}','', date_str) and date.today().year >= int(date_str[-4:])):
                await ctx.send('The date sent is not a valid date. Please follow the following format: dd-mm-yyyy')
                return
            parts =  date_str.split('-')
            parts.reverse()
            date_str = '-'.join(part for part in parts)
            try:
                date_obj = date.fromisoformat(date_str)
            except ValueError:
                await ctx.reply('The sent date is an invalid date. Please send a valid date. The format is: dd-mm-yyyy')
                return
            if not date_level_get(date_obj,sort_by_newest(FULL_LOGS)):
                await ctx.reply('There are no saved logged messages at the given date.\nPlease try again with a different date.')
                return
        if not mbr and not date_obj:
            await ctx.reply('You have to either provide a date to filter with or a user.')
            return 
        sorted_logs = sort_by_newest(FULL_LOGS)
        user_msgs = {}
        while counter <= amount:
            for time_obj, user_msgs_at_time in sorted_logs.items():
                if counter >= amount:
                    break
                if date_obj and date_obj != time_obj.date():
                    continue
                for user, msg_list in user_msgs_at_time.items():
                    if len(msg_list) == 0:
                        continue
                user_n =  ctx.guild.get_member(user)
                if user_n == None:
                    user_n =  await self.client.fetch_user(user)
                if mbr and user_n.id != mbr.id:
                    continue    
                if sorting:
                    for msg in msg_list:
                        if user not in user_msgs.keys():
                            user_msgs[user] = f'\nUser {user_n.name} sent:'
                        user_msgs[user] += f'\nmessage: {msg} at    {time_obj.strftime("%D %H:%M")}'
                else:
                    for msg in msg_list:
                        append_msg = f'User {user_n.name} sent: '
                        append_msg += f'\nmessage: \n    {msg}\nat {time_obj.strftime("%H:%M")}'
                    readable_logs += f'{append_msg}\n'
                counter +=1
            break
        if sorting:
            for user, log in user_msgs.items():
                readable_logs += f'\n{log}'
        await ctx.send(file =discord.File(StringIO(readable_logs), filename = 'logs.txt'))