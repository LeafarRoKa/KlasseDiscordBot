from stats_system.server_stats import Server_stats,commands
from datetime import datetime, timezone
import random
from message_events.message_management_logic import delete_message
from user_cmds.cmds_logic import can_do_daily
from utils.typing_utils import GuildContext,Initialized_Bot
class Fun_cmds(commands.Cog):
    def __init__(self, client:Initialized_Bot,server_stats:Server_stats):
        """Initialize the class with the discord bot and the server stats. Additionally saves all Cogs under attributes.

        Args:
            client (Initialized_Bot): The discord Bot.
            server_stats (Server_stats): The server stats.
        """
        self.client = client
        self.server_stats = server_stats
    
    @commands.command(help='The bot responds with Pong to this cmd.',brief='')
    async def ping(self,ctx:GuildContext):#if you don't put self python tries to pass it automaticly and discord tries to pass ctx and that wont work cause there is only one argument like one place, so the first argument will ALWAYS be self and so if there is no self there is no place for ctx
        await ctx.reply('Pong!')

    @commands.command(help='This cmd gives you a bit of xp every 24 hours.',brief='Gives xp every 24 hours.')
    async def daily_xp(self,ctx:GuildContext):
        user_stats = self.server_stats.user_stats(ctx.guild)
        can_use, hours,minutes = can_do_daily(user_stats.stats[ctx.author.id].get('time_redeemed'))
        if not can_use:
            better_diff = f'{int(hours)} hours {minutes} minutes'
            reply = await ctx.reply(f'You cannot redeem your daily xp multiple times in 24 hours.\nYou still have to wait {better_diff}.')
            await delete_message([ctx.message,reply],time=5)
            return
            
        amount_of_xp = 25
        user_stats.add_xp(ctx.author, amount_of_xp)
        user_stats.stats[ctx.author.id]['time_redeemed']  = datetime.now(timezone.utc)
        await self.server_stats.save_stats()
        await ctx.reply(f'You got {amount_of_xp}xp added as your daily xp.')
        
    @commands.command(aliases=['8ball'], help = 'This command responds to your questions with yes, no or maybe',brief='Responds to a question.')
    async def question_responder(self, ctx,question:str):
        await ctx.reply(random.choice(['yes','no','maybe']))

