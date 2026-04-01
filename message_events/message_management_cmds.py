from shared_vars import commands, Server_stats, discord, full_logs
from message_events.message_events_logic import sort_by_newest
from io import StringIO
class Message_management(commands.Cog):
    def __init__(self, client:commands.Bot,server_stats:Server_stats):
        self.client = client
        self.server_stats = server_stats
    @commands.command(help='This cmd gives the logs for the given user. You can also give a certain amount of msgs that it will show.',brief='Returns the logs.')
    @commands.has_permissions(manage_messages=True)
    async def logs(self, ctx,mbr:discord.Member, amount:int = 100, sorting:bool = True): # TODO Make it so that it works and only gives the logs of a certain person or of a certain amount not the full logs
        global full_logs
        counter = 0
        readable_logs = ''
        sorted_logs = sort_by_newest(full_logs)
        user_msgs = {}
        while counter <= amount:
            for time_obj, user_msgs_at_time in sorted_logs.items():
                if counter >= amount:
                    break
                for user, msg_list in user_msgs_at_time.items():
                    if len(msg_list) == 0:
                        continue
                user_n =  ctx.guild.get_member(user)
                if user_n == None:
                    user_n =  await self.client.fetch_user(user)
                if user_n.id != mbr.id:
                    continue    
                if sorting:
                    for msg in msg_list:
                        if user not in user_msgs.keys():
                            user_msgs[user] = f'\nUser {user_n.name} sent:'
                        user_msgs[user] += f'\nmessage: {msg} at {time_obj.strftime("%D %H:%M")}'
                else:
                    for msg in msg_list:
                        append_msg = (f'User {user_n.name} sent: ')
                        append_msg += f'\nmessage: {msg} at {time_obj.strftime("%H:%M")}'
                    readable_logs += f'{append_msg}\n'
                counter +=1
            break
        if sorting:
            for user, log in user_msgs.items():
                readable_logs += f'\n{log}'
        await ctx.send(file =discord.File(StringIO(readable_logs), filename = 'logs.txt'))

