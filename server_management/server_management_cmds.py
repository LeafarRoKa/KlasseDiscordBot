from shared_vars import commands, Server_stats, discord, admin_channel_name, bot_channel_name, event_channel_name,goodbye_channel_name,welcome_channel_name,permissions_per_role
from message_events.message_management import delete_message,response_waiting,response_waiting_text
import asyncio
from server_management.cmds_logic import other_rbg, hex_color_to_rgb
class sever_management(commands.Cog):
    def __init__(self, client:commands.Bot,server_stats:Server_stats):
        self.client = client
        self.server_stats = server_stats
    @commands.command(help='Lists all server roles.')
    async def list_roles(ctx):
        roles = ctx.guild.roles
        roles_list = []
        for role in list(roles):
            if role.name != '@everyone':
                roles_list.append(role.name)
        await ctx.send(f'Avalible roles:\n'+'\n'.join(f'- {role}' for role in roles_list))

    @commands.command(help='This cmd clears all messages in the given channel(channelID).',brief='Clears the given channel.')
    @commands.has_permissions(manage_messages = True)
    @commands.bot_has_permissions(manage_messages=True)
    async def clear_channel (self, ctx:commands.Context, channel_id: int = None):
        guild = ctx.guild
        channel = discord.utils.get(guild.channels,name= admin_channel_name) # admin channel
        if channel_id == None:
            reply = await ctx.reply('Please enter a channel_ID')
            await delete_message([ctx,reply], time=5)
            return
        try:
            channel = ctx.guild.get_channel(channel_id)
        except discord.NotFound:
            reply = 'Channel does not exist.\nPlease enter a valid channel_ID.'
            reply = await ctx.reply(reply)
            await delete_message([ctx, reply], time=5)
        await ctx.send(f'Are you sure that you want to delete all messages of the channel {channel.name}. Type y to confirm and n to exit.')
        response = response_waiting(ctx,self.client)
        if response.content == 'y':
            try:
                await channel.purge(limit = None, bulk = True)
                async for message in channel.history(limit = None, oldest_first = True):
                    try:
                        await message.delete()
                        await asyncio.sleep(0.3)
                    except discord.Forbidden:
                        await ctx.send(f'Missing permission to delete some messages.')
                    except discord.HTTPException:
                        continue
                await ctx.send(f'Succecfully cleared all messages of channel {channel.name}.')
            except discord.Forbidden:
                await ctx.send('I do not have permission to manage messages.')
            except Exception as e:
                print(e)
                await ctx.send('An error has occoured while trying to excecute this command.')
        elif response.content == 'n':
            return
        else:    
            await ctx.send('Invalid response.')
    @commands.command(help='This cmd adds the given channel(channelID) from the channels where the bot can directly talk.',brief='Adds channel to the allowed channels.')
    @commands.has_permissions(manage_channels=True)
    async def add_allowed_channels(self, ctx, channel_id: int):
        allowed_channels = self.server_stats.stats[ctx.guild.id]['allowed_channels']
        for channel in ctx.guild.channels:
            if channel_id == channel.id:
                if channel_id in allowed_channels.values():
                    await ctx.send(f'Channel is already an allowed channel.')
                    return
                allowed_channels[channel.name] = channel_id
                self.server_stats.save_stats()
                await ctx.send(f'Successfully added channel {channel.name} to the allowed channels.')
                return
        await ctx.send('Channel was not found. Please make sure that the entered channeld ID is an existing channel.')

    @commands.command(help='This cmd removes the given channel(channelID) from the channels where the bot can directly talk.',brief='Removes the channel from the bot channels.')
    @commands.has_permissions(manage_channels=True)
    async def remove_allowed_channels(self, ctx, channel_id: int):
        allowed_channels = self.server_stats.stats[ctx.guild.id]['allowed_channels']
        for name, id in allowed_channels.items():
            if channel_id == id:
                allowed_channels.pop(name)
                self.server_stats.save_stats()
                await ctx.send(f'Successfully removed channel {name} from the allowed channels.')
                return 
        await ctx.send('Channel id is not yet registred to the allowed channels.')


    @commands.command(help = 'This cmd sets up the bot to be used in a server.',brief='Sets up the bot in the server.')
    @commands.has_permissions(manage_guild=True)
    async def setup(self,ctx:commands.Context):
        guild = ctx.guild
        admin_channel = discord.utils.get(guild.channels,name=admin_channel_name)
        bot_channel = discord.utils.get(guild.channels,name=bot_channel_name)
        event_channel = discord.utils.get(guild.channels,name=event_channel_name)
        welcome_channel = discord.utils.get(guild.channels, name = welcome_channel_name)
        goodbye_channel = discord.utils.get(guild.channels, name = goodbye_channel_name)
        nescessary_channels = {admin_channel:admin_channel_name,bot_channel:bot_channel_name,event_channel:event_channel_name,welcome_channel:welcome_channel_name,goodbye_channel:goodbye_channel_name}
        self.server_stats.is_dict_complete()
        if any(channel is None for channel in nescessary_channels.keys()):
            await ctx.send('Would you like to proceed with creating channels (y/n)?\n(if a needed channel doesn\'t already exist it will ask you if it is allowed to specificly create that channel.)')
            response = await response_waiting(ctx,self.client,time=120)
            if response is None:
                    return
            if response.content.lower() not in ['y', 'yes']:
                await ctx.send('successfully stopped the setup process.')
                return
        for channel, name in nescessary_channels.items():
            if channel is None:
                await ctx.send(f'A text channel called {name} is needed for the bot to work.\nBut the channel doesn\'t exist in this server. Would you like the bot to create that channel(y/n)?')
                response = await response_waiting(ctx,self.client, time= 120)
                if response is None:
                    return
                if response.content.lower() not in ['y', 'yes']:
                    await ctx.send(f'Successfully cancled the creation of channel {name}')
                    return
                if not guild.me.guild_permissions.manage_channels:
                    await ctx.send('I do not have permissions to create channels.\nI am required the permission to create channels to automaticly setup this server.')
                    return
                await ctx.guild.create_text_channel(name)
        await ctx.send('In the following you will need to create 5 roles. The roles beyond 5. are optional and would be mini-mod, mod, admin, owner(if you would like to not create any of these roles respond None as the role name.)')
        async def role_name_defentition():
            roles_name = {}
            for i in range(1,10):
                await ctx.send(f'What would you like to name the {i}. xp role (1.lowest-5.highest).')
                response = await response_waiting(ctx,self.client)
                if response is None:
                    return
                if response.content.lower() in ['none']:
                    continue
                roles_name[i] = response.content
                if len(set(roles_name.values())) != len(roles_name.values()):
                    await ctx.send('You can\'t have two roles with the same name.\nYou will have to repeat the role naming process\n')
                    return await role_name_defentition()
            return roles_name
        roles_name = await role_name_defentition()
        await ctx.send('Please make sure that the bot\'s role is above all of the other user roles that you want the bot to manage.\nThe most optimal position would be right below the owner role.\n\nIf you completed that enter ok to proceed.')
        response = await response_waiting_text(ctx,self.client,time=600)
        if response not in ['ok','y','yes']:
            return
        
        for num, role_name in roles_name.items():
            role = discord.utils.get(guild.roles, name= role_name)
            if role is None:
                await ctx.send(f'There is no role named {role_name}.\nWould you like me to create that role?')
                response = await response_waiting(ctx,self.client,120)
                if response is None:
                    return
                if response.content.lower() in ['y','yes']:
                    if not guild.me.guild_permissions.manage_roles:
                        await ctx.send('I do not have permissions to manage roles.\nI am required the permission to manage roles to automaticly setup this server.')
                        return
                    r,g,b = hex_color_to_rgb(permissions_per_role[num][1])
                    rgb = other_rbg(r,g,b)
                    await guild.create_role(name=role_name,permissions= permissions_per_role[num][0],color=discord.Color(rgb))
                    role = discord.utils.get(guild.roles,name=role_name)
                    self.server_stats.stats[guild.id]['roles_imgs'][num] = {9: r'images/owner.png', 8: '','klassebot': r'images/bot.png', 7: r"images/admin.png",6: '',5: r"images/dev.png", 4: r"images/trial_dev.png", 3: r'images/lite_member.png', 2: r"images/member.png", 1: r'images/beginner.png', 'spammer':''}.get(num)
                    self.server_stats.stats[guild.id]['roles_requirements'][num] = {1: {"xp": 0, "strikes": 99}, 2: {"xp": 500, "strikes": 99}, 3: {"xp": 2500, "strikes": 20}, 4: {"xp": 5000, "strikes": 10}, 5: {"xp": 12500, "strikes": 5},6:{'strikes':60},7:{'strikes':80},8:{'strikes':10000},9:{'strikes':9999999999999999999999999}}.get(num)#TODO Make the strikes limit on 
                    if num == 9:
                        await ctx.send('As this is the owner role it is normally above the bot, so you will have to move it above the bots rank. ')
                        break
                    await guild.edit_role_positions({role:num})
        self.server_stats.stats[guild.id]['server_roles'] = roles_name#TODO DO NOT CREATE OWNER ROLE JUST SAVE IT, CREATE PERMISSION FOR THE OTHER 3 or so roles. 
        self.server_stats.stats[guild.id]['set_up'] = True
        self.server_stats.stats[guild.id]['suggestions_closed'] = False
        self.server_stats.save_stats         
        self.server_stats.user_stats(guild).complete(guild)
        #TODO come up with ideas on how to personalize this bot the most possible
        #completed the following
        #completed if admin channel doesnt exist ask if the bot should create one
        #completed if bot channel doesnt exist  not ask for permission to create one
        #completed ask whats the first role in the server 
        #completed check if role exists else ask to create it
        #...
        #completed ask whats the 5th role that should be earned with xp if it doesnt exist ask to create one
        #completed check if a welcome channel, a event channel, a goodbye channel exist if not ask to create one

    @setup.error
    async def setup_error(ctx:commands.Context,error:commands.CommandError):
        if isinstance(error, discord.ext.commands.errors.CommandInvokeError):
            await ctx.send('I do not have permission to create new roles that are a higher level than me.\nPlease make sure that the bot\'s role is placed above every role that the bot should be managing.\nThe most optimal position would be the one below the owner role.')
            error.handled = True
            return
        else:
            raise error