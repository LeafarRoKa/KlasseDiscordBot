from shared_vars import discord, commands, Server_stats
from user_management.user_management_logic import give_role_logic, remove_role_logic, timeout_logic
from message_events.message_management import delete_message
class User_management(commands.Cog):
    def __init__(self, client:commands.Bot,server_stats:Server_stats):
        self.client = client
        self.server_stats = server_stats

    @commands.command(help='This cmd gives the given role to the given user.',brief='Gives the user the given role.')
    @commands.has_permissions(manage_roles= True)
    @commands.bot_has_permissions(manage_roles = True)
    async def give_role(self, ctx, member: discord.Member, role: discord.Role):
        await give_role_logic(member, role, ctx)
    
    @commands.command(help='This cmd removes the given role to the given user.',brief='Removes the role from the given user.')
    @commands.has_permissions(manage_roles= True)
    @commands.bot_has_permissions(manage_roles = True)
    async def remove_role(self,ctx, member: discord.Member, role: discord.Role):
        message = await remove_role_logic(member, role)
        await ctx.reply(message)

    @commands.command(help='This cmd adds the given role to all users in the server if they don\'t have it already.',brief='Gives everyone the given role.')
    @commands.has_permissions(manage_roles= True)
    @commands.bot_has_permissions(manage_roles = True)
    async def give_all_roles(self,ctx, role: discord.Role):
        for member in ctx.guild.members:
            try:
                await member.add_roles(role)
                await ctx.send(f'Successfully gave {role.name} to {member.display_name}')
            except discord.Forbidden:
                await ctx.send(f'I do not have permission to add {role.name} to {member.display_name}.')
            except Exception as e:
                print(e)
                await ctx.send('An unexpected Error has occoured please contact the Bot owner.')

    
    @commands.command(help='This cmd times out the given member for the given time. You can also provide a optional reason.',brief='Times out the given user.')
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, duration: str, reason: str = 'No valid reason provided'):
        await timeout_logic(ctx, member, duration ,reason = reason) 
    
    @commands.command(help='This cmd timeouts you for the given amount of seconds.',brief='Times out yourself.')
    async def self_timeout(self, ctx:commands.Context,time:str='60'):
        if not time.isdigit():
            return
        if int(time) > 10000:
            await ctx.reply('You can maximally timout out yourself for 10000 seconds.',delete_after=5)
            await delete_message(ctx.message,time=5)
            return   
        await timeout_logic(ctx,ctx.author,f'{time}s',reason='self_timout')
        await delete_message(ctx.message)  
    
    @commands.command(help='This cmd sets the xp of the given user to the amount given.',brief='Sets a users_xp to a given amount.')
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(manage_messages= True)
    async def set_xp(self, ctx, member: discord.Member, amount:int):
        global server_stats
        guild = ctx.guild
        self.server_stats.stats[guild.id]['user_stats'].stats[member.id]['xp'] = amount
        self.server_stats.save_stats()
        await ctx.reply(f'successfully set <@{member.id}>\'s xp to {amount}.')
    

    @commands.command(help='This cmd adds xp to the given user.',brief='Adds the given xp the given user.')
    @commands.has_permissions(moderate_members=True)
    async def add_xp(self,ctx,member:discord.Member,amount:int = 5):
        self.server_stats.user_stats(member.guild).add_xp(member,amount)
        await ctx.reply(f'Successfully added {amount}xp to <@{member.id}>.',allowed_mentions=discord.AllowedMentions(users=False))
    
    @commands.command(help='This cmd sets the xp of the given user to the given amount.', brief='Sets xp of the given user.')
    @commands.has_permissions(moderate_members=True)
    async def remove_xp(self, ctx:commands.Context, member:discord.Member, amount:int=5):
        self.server_stats.user_stats(ctx.guild).add_xp(member,amount*-1)
        await ctx.reply(f'Successfully removed {amount}xp to <@{member.id}>.',allowed_mentions=discord.AllowedMentions(users=False))


    @commands.command(help='This cmd adds the badge coresponding to the given badge name to the given user.',brief='Adds a badge to the given user.')
    @commands.has_permissions(manage_messages=True)
    async def add_badge(self,ctx, member: discord.Member,badge_name:str):
        guild = ctx.guild
        if badge_name in self.server_stats[guild.id]['badges_imgs'].keys():
            self.server_stats.user_stats(guild).stats[member.id]['badges'].append(self.server_stats[guild.id]['badges_imgs'].get(badge_name))
            ... #TODO complete function
    @commands.command(help='This cmd removes the given role from all the users in the server if they have it.',brief='Removes the given role from everyone.')
    @commands.has_permissions(manage_roles= True)
    @commands.bot_has_permissions(manage_roles = True)
    async def remove_all_roles(self,ctx, role: discord.Role):
        for member in ctx.guild.members:
            try:
                await member.remove_roles(role)
                await ctx.send(f'Successfully removed {role.name} from {member.display_name}.')
            except discord.Forbidden:
                await ctx.send(f'I do not have permission to remove {role.name} from {member.display_name}.')
            except Exception as e:
                print(e)
                await ctx.send('An unexpected Error has occoured please contact the Bot owner.')