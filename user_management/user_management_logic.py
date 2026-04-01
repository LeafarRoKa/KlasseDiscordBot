from shared_vars import discord, User_stats, Server_stats,admin_channel_name, commands
from datetime import timedelta
from message_events.message_management import delete_message
async def promote(old_role: discord.Role, new_role: discord.Role, member: discord.Member, server_stats:Server_stats):
        guild = member.guild
        user_stats = server_stats.user_stats(guild)
        user_stats: User_stats
        await remove_role_logic(member, old_role)
        await give_role_logic(member, new_role)
        if new_role.name in server_stats.stats[guild.id]['server_roles'].values():
            user_stats.set_xp(member, 0)
        server_stats.save_stats()
        user_stats.update_rank(member,server_stats.stats[guild.id]['server_roles'])
        channel = discord.utils.get(guild.channels,name= admin_channel_name)
        try:
            await member.send(f'You successfully got promoted from {old_role.name} to {new_role.name}.')
        except discord.Forbidden:
            await channel.send(f'Successfully promoted {member.name} from {old_role.name} to {new_role.name}.')
        except Exception as e:
            print(e)
            await channel.send(f'An error occoured while trying to promote {member.name} from {old_role.name} to {new_role.name}.\nPlease contact the bot dev if this behaviour is unexpected.')

async def give_role_logic(member: discord.Member, role: discord.Role, ctx = None):
    guild = member.guild
    if ctx == None:
        channel = discord.utils.get(guild.channels,name= admin_channel_name)#admin channel
    else:
        channel = ctx.channel
    try:
        await member.add_roles(role)
        await channel.send(f'Successfully gave {role.name} to {member.display_name}')
    except discord.Forbidden:
        await channel.send('I do not have permission to assign this role.')
    
    except Exception as e:
        print(e)
        await channel.send('An unexpected Error has occoured please contact the Bot owner.')

async def remove_role_logic(member: discord.Member, role: discord.Role):
    guild = member.guild
    try:
        await member.remove_roles(role)
        channel = discord.utils.get(guild.channels,name= admin_channel_name)
        await channel.send(f'Successfully removed {role.name} from {member.display_name}.')
        return f'Successfully removed {role.name} from {member.display_name}.'
    except discord.Forbidden:
        return f'I do not have permission to remove role: {role.name} from {member.name}.'
    except Exception as e:
        print(e)
        return 'An unexpected Error has occoured please contact the Bot owner.'
    
async def timeout_logic(ctx:commands.Context, member: discord.Member, duration: str, *,reason: str = 'No valid reason provided'):
    guild = member.guild
    
    try:
        time_unit = duration[-1]
        time_value = int(duration[:-1])
        if time_unit == 's':
            timeout_time = timedelta(seconds = time_value)
        elif time_unit == 'm':
            timeout_time = timedelta(minutes= time_value)
        elif time_unit == 'h':
            timeout_time = timedelta(hours=time_value)
        elif time_unit == 'd':
            timeout_time = timedelta(days= time_value)
        else:
            timeout_time = timedelta(seconds=int(duration))
        await member.timeout(timeout_time, reason=reason)
        channel = discord.utils.get(guild.channels,name= admin_channel_name)
        await channel.send(f'Member {member.name} has been timed out for {duration}. Reason: {reason}.')
    except ValueError:
        channel = discord.utils.get(guild.channels,name= admin_channel_name)
        await channel.send(f'Member {member.name} has not been timed out for {duration}. Reason {reason}.\nIt failed because of a ValueError.')
    except discord.Forbidden:
        if not ctx:
            admin_channel = discord.utils.get(guild.channels,name=admin_channel_name)
            if not admin_channel:
                return
            await admin_channel.send(f'I tried to timeout member <@{member.id}> for reason {reason} but i couldn\'t because the member is either on the same or on a higher rank than me.')
            return
        await ctx.reply('I am not capable of performing actions for members above or at my same rank.',delete_after=5)
        await delete_message(ctx.message,time=5)
    except OverflowError:
        pass