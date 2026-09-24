from shared_vars import discord, admin_channel_name, bot_channel_name, event_channel_name,goodbye_channel_name,welcome_channel_name,permissions_per_role, ENDING_IMGS,REQUIREMENTS_TEMPLATE
from stats_system.server_stats import Server_stats,commands,Roles_requirement
from message_events.message_management_logic import delete_message,response_waiting,response_waiting_text,send_and_response_waiting_until_response,send_and_response_waiting_until_response_int
from message_events.message_events_logic import check_unsafe_image_content
from server_management.cmds_logic import other_rbg, hex_color_to_rgb
from utils.typing_utils import Initialized_Bot,GuildContext
from utils.utils import dynamic_send,get_admin_channel,get_messageable_channel
from io import BytesIO
from PIL import Image
import os
import asyncio
import typing


class Server_management(commands.Cog):
    def __init__(self, client:Initialized_Bot,server_stats:Server_stats):
        """Initialize the class with the Discord bot and the server stats. During the initialization adds a global check to the Discord bot.

        Args:
            client (Initialized_Bot): The Discord Bot.
            server_stats (Server_stats): The server stats.
        """
        self.client = client
        self.server_stats = server_stats

    @commands.command(help='Lists all server roles.')
    async def list_roles(self,ctx:GuildContext):
        roles = ctx.guild.roles
        roles_list = []
        for role in list(roles):
            if role.name != '@everyone':
                roles_list.append(role.name)
        await ctx.reply(f'Avalible roles:\n'+'\n'.join(f'- {role}' for role in roles_list))

    @commands.command(help='This cmd clears all messages in the given channel(channelID).',brief='Clears the given channel.')
    @commands.has_permissions(manage_messages = True)
    @commands.has_permissions(manage_messages=True)
    async def clear_channel (self, ctx:GuildContext, channel_id: int|None = None):
        if channel_id is None:
            reply = await ctx.reply('Please enter a channel_ID')
            await delete_message([ctx.message,reply], time=5)
            return
        channel = ctx.guild.get_channel(channel_id)
        if not isinstance(channel,discord.abc.Messageable):
            reply = await ctx.reply('Channel does not exist.\nPlease enter a valid channel_ID.')
            await delete_message([ctx.message, reply], time=5)
            return
        await ctx.send(f'Are you sure that you want to delete all messages of the channel {channel.name}. Type y to confirm and n to exit.')
        response = await response_waiting(ctx,self.client)
        if response is None:
            return
        
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

    @commands.hybrid_command(help='This cmd adds the given channel(channelID) from the channels where the bot can directly talk.',brief='Adds channel to the allowed channels.')
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def add_allowed_channels(self, ctx:GuildContext, channel_obj: discord.TextChannel):
        channel_id = channel_obj.id
        allowed_channels = self.server_stats.stats[ctx.guild.id]['allowed_channels']
        for channel in ctx.guild.channels:
            if channel_id == channel.id:
                if channel_id in allowed_channels:
                    await ctx.send(f'Channel is already an allowed channel.')
                    return
                allowed_channels.append(channel_id)
                await self.server_stats.save_stats()
                await ctx.send(f'Successfully added channel {channel.name} to the allowed channels.')
                return
        await dynamic_send(ctx,'Channel was not found. Please make sure that the entered channeld ID is an existing channel.')

    @commands.hybrid_command(help='This cmd removes the given channel(channelID) from the channels where the bot can directly talk.',brief='Removes the channel from the bot channels.')
    @commands.has_permissions(manage_channels=True)
    async def remove_allowed_channels(self, ctx:GuildContext, channel_id: int):
        allowed_channels = self.server_stats.stats[ctx.guild.id]['allowed_channels']
        for id in allowed_channels:
            if channel_id == id:
                allowed_channels.pop(id)
                channel = ctx.guild.get_channel(id)
                if channel is None:
                    return
                await self.server_stats.save_stats()
                await ctx.send(f'Successfully removed channel {channel.name} from the allowed channels.')
                return 
        await dynamic_send(ctx,'Channel id is not yet registred to the allowed channels.')


    @commands.command(help = 'This cmd sets up the bot to be used in a server.',brief='Sets up the bot in the server.')
    @commands.has_permissions(manage_guild=True)
    async def setup(self,ctx:GuildContext):
        guild = ctx.guild
        admin_channel = get_admin_channel(guild)
        bot_channel =get_messageable_channel(bot_channel_name,guild)
        event_channel = get_messageable_channel(event_channel_name,guild)
        welcome_channel = get_messageable_channel( welcome_channel_name,guild)
        goodbye_channel = get_messageable_channel(goodbye_channel_name,guild)
        nescessary_channels = {admin_channel_name : admin_channel ,bot_channel_name : bot_channel,event_channel_name: event_channel,welcome_channel_name: welcome_channel,goodbye_channel_name: goodbye_channel}
        self.server_stats.is_dict_complete()
        if any(channel is None for channel in nescessary_channels.values()):
            await ctx.send('Would you like to proceed with creating channels (y/n)?\n(if a needed channel doesn\'t already exist it will ask you if it is allowed to specificly create that channel.)')
            response = await response_waiting(ctx,self.client,time=300)
            if response is None:
                    return
            if response.content.lower() not in ['y', 'yes']:
                await ctx.send('successfully stopped the setup process.')
                return
        for name, channel in nescessary_channels.items():
            if channel is None:
                await ctx.send(f'A text channel called {name} is needed for the bot to work.\nBut the channel doesn\'t exist in this server. Would you like the bot to create that channel(y/n)?')
                response = await response_waiting(ctx,self.client, time= 300)
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

        async def role_name_defentition() -> dict[str,Roles_requirement]:
            roles_names = {}
            for i in range(1,10):
                preset = REQUIREMENTS_TEMPLATE[i-1]
                response = await send_and_response_waiting_until_response(ctx,self.client, prompt=f'What would you like to name the {i}. xp role (1.lowest-5.highest).(exit to exit)', time=300,break_on=['exit'])
                if response.lower() in ['none']:
                    continue
                xp_requirement = await send_and_response_waiting_until_response_int(ctx,self.client,f'How much xp would you like there to be required for reaching this role. The defualt is {preset['xp']}. (Enter default for the default.)',time=300,break_on=['default'])
                if isinstance(xp_requirement,str):
                    xp_requirement = preset['xp']
                strikes_requirements = await send_and_response_waiting_until_response_int(ctx,self.client,f'How many strikes would you like to be allowed a user to have maximally for being allowed in the next role? The default would be {preset['strikes']} (Enter default for the default)',time=300,break_on=['default'])
                if isinstance(strikes_requirements,str):
                    strikes_requirements = preset['strikes']
                roles_names[response] = {'xp':xp_requirement,'strikes':strikes_requirements,'pos':i}
                if len(set(roles_names.values())) != len(roles_names.values()):
                    await ctx.send('You can\'t have two roles with the same name.\nYou will have to repeat the role naming process\n')
                    return await role_name_defentition()
            return roles_names
        
        roles_name = await role_name_defentition()
        if not roles_name:
            return
        await ctx.send('Please make sure that the bot\'s role is above all of the other user roles that you want the bot to manage.\nThe most optimal position would be right below the owner role.\n\nIf you completed that enter ok to proceed.')
        response = await response_waiting_text(ctx,self.client,time=600)
        if response not in ['ok','y','yes']:
            return
        for name , requirements in roles_name.items():
            i = requirements['pos']
            role = discord.utils.get(guild.roles, name= name)
            if role is None:
                await ctx.send(f'There is no role named {name}.\nWould you like me to create that role?')
                response = await response_waiting(ctx,self.client,300)
                if response is None:
                    return
                if response.content.lower() in ['y','yes']:
                    if not guild.me.guild_permissions.manage_roles:
                        await ctx.send('I do not have permissions to manage roles.\nI am required the permission to manage roles to automaticly setup this server.')
                        return
                    r,g,b = hex_color_to_rgb(permissions_per_role[i+1][1])
                    rgb = other_rbg(r,g,b)
                    await guild.create_role(name=name,permissions= permissions_per_role[i][0],color=discord.Color(rgb))
                    role = typing.cast(discord.Role,discord.utils.get(guild.roles,name=name))#bcs it was just created
                    self.server_stats.stats[guild.id]['roles_imgs'][name] = {9: r'images/owner.png', 8: '','klassebot': r'images/bot.png', 7: r"images/admin.png",6: '',5: r"images/dev.png", 4: r"images/trial_dev.png", 3: r'images/lite_member.png', 2: r"images/member.png", 1: r'images/beginner.png', 'spammer':''}[i]
                    self.server_stats.stats[guild.id]['roles_requirements'].pop(str(i))  #TODO Make the strikes limit on
                    self.server_stats.stats[guild.id]['roles_requirements'][name] = requirements
                    if i == 9:
                        await ctx.send('As this is the owner role it is normally above the bot, so you will have to move it above the bots rank. ')
                        break
                    await guild.edit_role_positions({role:i})
        # self.server_stats.stats[guild.id]['server_roles'] = roles_name#TODO DO NOT CREATE OWNER ROLE JUST SAVE IT, CREATE PERMISSION FOR THE OTHER 3 or so roles. 
        self.server_stats.stats[guild.id]['set_up'] = True
        self.server_stats.stats[guild.id]['suggestions_closed'] = False
        await self.server_stats.save_stats()      
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
    async def setup_error(self, ctx:GuildContext,error:commands.CommandError):
        if isinstance(error, commands.errors.CommandInvokeError):
            await ctx.send('I do not have permission to create new roles that are a higher level than me.\nPlease make sure that the bot\'s role is placed above every role that the bot should be managing.\nThe most optimal position would be the one below the owner role.')
            error.handled = True#type:ignore
            return
        else:
            raise error
    
    @commands.command(help = 'This cmd allows you to change the images used in the stats images for registred roles.',brief='Change role images for stats card.',aliases=['change_role_imgs'])
    @commands.has_permissions(manage_guild=True)
    async def change_role_image(self, ctx:GuildContext, name:str | None = None):
        if not name:
            await ctx.reply(f'You did not provide a name. The registred roles are: {list(self.server_stats.stats[ctx.guild.id]['roles_requirements'])}')
            return
        if not name in self.server_stats.stats[ctx.guild.id]['roles_requirements']:
            await ctx.reply('The given role name is not registred in the bot for this server.\nPlease try again.')
            return
        attachments = ctx.message.attachments
        if len(attachments) != 1:
            await ctx.reply('You did not provide a valid amount of attachements.\nPlease only provide one image attachment.')
            return
        if attachments[0].content_type and attachments[0].content_type.split('/')[1].lower() not in ENDING_IMGS:
            await ctx.reply(f'The provided file type is not accepted by the bot for images.\nPlease try again with a file type that is in the following list {ENDING_IMGS}')
            return
        folder_name  = f'server_data_{ctx.guild.name}#{ctx.guild.id}'
        folder_path = f'{folder_name}/images'
        if not os.path.isdir(folder_path):#isdir means is directory mkdir means make directory a directory is to my knowledge a folder 
            os.mkdir(folder_path)
        image_path = f'{folder_path}/{name.lower()}.{ctx.message.attachments[0].content_type}'
        with Image.open(BytesIO(await attachments[0].read())) as img:
            img.save(image_path)
            risk = await check_unsafe_image_content(image_path)
            if risk[1] > 5:
                await ctx.reply('As the image seems to contain nudity you are not allowed to continuoue. Please try again with a non-explicit image.')

                return
        self.server_stats.stats[ctx.guild.id]['roles_imgs'][name] = image_path
        await ctx.reply(f'Successfully updated the rank image for {name}.')
