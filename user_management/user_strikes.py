
from shared_vars import discord, Server_stats,admin_channel_name,waiting_list
from datetime import timedelta, datetime, timezone
from user_management.user_management_logic import promote, timeout_logic

async def add_strike_code(member: discord.Member,server_stats:Server_stats, amount:int = '1', ctx = None):
    if type(amount) != int:
        amount = int(amount)
    server_stats.stats[member.guild.id]['strikes'][member.id] += amount
    server_stats.save_stats()
    await strikes_punishments(member,server_stats, ctx)

async def set_strikes_code(ctx, member: discord.Member,server_stats:Server_stats, amount ='1'):
    if type(amount) != int:
        amount = int(amount)
    server_stats.stats[member.guild.id]['strikes'][member.id] = amount
    await strikes_punishments(member,server_stats)
    await ctx.send(f'The strikes of {member.display_name} were successfully set to {amount}')


async def strikes_punishments(member: discord.Member, server_stats:Server_stats, ctx  = None):
    global waiting_list
    guild = member.guild
    user_stats = server_stats.user_stats(guild)
    channel =  discord.utils.get(guild.channels,name= admin_channel_name) #admin channel
    if user_stats.stats[member.id]['rank'] == 'owner':
        name = 'Owner'
    else:
        name= user_stats.stats[member.id]['rank'] 
    old_role = discord.utils.get(guild.roles, name =name )#it is called that way to save it as an old role if the user recieves spammer
    spammer = discord.utils.get(guild.roles, name= 'spammer')
    strikes = server_stats.strikes(guild)
    if old_role.name in list(server_stats.stats[guild.id]['server_roles'].values())[6:]:
        if strikes[member.id] < server_stats.stats[guild.id]['roles_requirements'].get(old_role.name, {}).get('strikes', 0) + 10:
            return
    if channel is None:
        print('Could not find channel with the set channel ID.')
        return
    if strikes[member.id] == 1:
        time_obj = '1m'
        await timeout_logic(ctx, member, time_obj, reason= 'The user has one strike')
        await channel.send(f'{member.name} was timedout for {time_obj} for having {strikes[member.id]} strikes.')
    elif strikes[member.id] == 2:
        time_obj = '5m'
        msg = await timeout_logic(ctx, member, time_obj, reason= 'The user has two strikes')
        print(msg)
        await channel.send(f'{member.name} was timedout for {time_obj} for having {strikes[member.id]} strikes.')
    elif strikes[member.id] >= 3 and strikes[member.id] <= 19:
        user_stats.stats[member.id]['role_before_spam'] = old_role.name
        await promote(old_role, spammer, member,server_stats)
        server_stats.save_stats()
        ban_time = timedelta(seconds = 100)
        if strikes[member.id] == 4:
            ban_time = timedelta(minutes= 5)
        elif strikes[member.id] == 5:
            ban_time = timedelta(minutes= 10)
        elif strikes[member.id] == 6:
            ban_time = timedelta(minutes= 15)
        elif strikes[member.id] == 7:
            ban_time = timedelta(minutes= 20)
        elif strikes[member.id] == 8:
            ban_time = timedelta(minutes= 30)
        elif strikes[member.id] == 9:
            ban_time = timedelta(hours= 1)
        elif strikes[member.id] == 10:
            ban_time = timedelta(hours= 2)
        elif strikes[member.id] == 11:
            ban_time = timedelta(hours= 3)
        elif strikes[member.id] == 12:
            ban_time = timedelta(hours= 4)
        elif strikes[member.id] == 13:
            ban_time = timedelta(hours= 5)
        elif strikes[member.id] == 14:
            ban_time = timedelta(hours= 6)
        elif strikes[member.id] == 15:
            ban_time = timedelta(hours= 7)
        elif strikes[member.id] == 16:
            ban_time = timedelta(hours= 8)
        elif strikes[member.id] == 17:
            ban_time = timedelta(hours= 9)
        elif strikes[member.id] == 19:
            ban_time = timedelta(hours= 10)
        if member.id not in waiting_list.keys():
            waiting_list[member.id] = {'time':datetime.now(timezone.utc) + ban_time,'guild':guild.id}
        else:
            waiting_list[member.id]['time'] +=ban_time

        if ctx == None:
            await channel.send(f'User {member.name} got flagged for spamming.')
        else:
            await ctx.reply('You got flagged for spamming or saying slurs.', delete_after = 5)

    elif strikes[member.id] >= 20 and strikes[member.id] <= 40:
        user_stats.stats[member.id]['role_before_spam'] = old_role.name
        await promote(old_role, spammer, member,server_stats)
        server_stats.save_stats
        await timeout_logic(member, '1d', reason=f'The user has {strikes[member.id]} strikes.')

    elif strikes[member.id] > 40:
        await member.kick(reason='You were kicked because you currently had 40 strikes on the server.\nPlease contact the server admins if you think this treatment is unfair.')
    
    server_stats.save_stats()

