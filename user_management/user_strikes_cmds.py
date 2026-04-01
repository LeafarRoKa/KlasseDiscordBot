from shared_vars import commands, Server_stats,discord
from user_management.user_strikes import add_strike_code,set_strikes_code
class User_strikes(commands.Cog):
    def __init__(self, client:commands.Bot,server_stats:Server_stats):
        self.client = client
        self.server_stats = server_stats
    
    @commands.command(help='This cmd adds the amount of strikes given to the given user.',brief='Adds a strike to the given user.')
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members= True)

    async def add_strikes(self,ctx, member: discord.Member, amount = '1' ):
        try:
            if amount == 1:
                await ctx.send(f'Added {amount} strike to {member.name}.')
            else:
                await ctx.send(f'Added {amount} strikes to {member.name}.')
            await add_strike_code(member,self.server_stats, amount)
        except discord.Forbidden:
            await ctx.send(f'I do not have permission to do that.')
        except Exception as e:
            print(e)
            await ctx.send('An unexpected Error has occoured please contact the Bot owner.')
    
    @commands.command(help='This cmd sets the amount of strikes a user has to the given amount.',brief='Sets the users_strikes to the given amount.')
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members= True)
    async def set_strikes(self,ctx, member: discord.Member, amount= '1'):
        await set_strikes_code(ctx, member,self.server_stats, amount)

    @commands.command(help='This cmd lists all the strikes of every user in the server if no user is given. If a user is given it will just show the strikes of that user.',brief='Lists the strikes of everyone.')
    @commands.has_permissions(manage_roles= True)
    @commands.bot_has_permissions(manage_roles= True)
    async def strikes_list(self, ctx, member:discord.Member=None):
        answer = ''
        strikes = self.server_stats.strikes(ctx.guild)
        for key, value in strikes.items():
            if member and key != member.id:
                continue
            key = self.client.get_user(key)
            key = key.display_name
            if key is None:
                continue
            if value == 1:
                answer += (f'User: {key} has {value} strike.\n')
            else:
                answer += (f'User: {key} has {value} strikes.\n')
        await ctx.send(answer)
    @commands.command(help='This cmd shows you how many strikes you currently have.',brief='Shows how many strikes you have.')
    async def my_strikes(self,ctx):
        member = ctx.author
        strikes = self.server_stats.strikes(ctx.guild)
        if strikes[member.id] == 1:
            await ctx.send(f'You have {strikes[member.id]} strike.')
        else:
            await ctx.send(f'You have {strikes[member.id]} strikes.')
