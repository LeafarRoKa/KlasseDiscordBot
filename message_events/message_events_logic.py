import discord
from shared_vars import admin_channel_name, Server_stats, commands, forbidden_words, logs_temp
from user_management.user_management_logic import promote
import difflib
from user_management.user_strikes import add_strike_code
import statistics
from message_events.message_management import del_old_logs, delete_message
import re

async def rank_check(member: discord.Member, server_stats:Server_stats):
    guild = member.guild
    user_stats = server_stats.user_stats(guild)
    next_rank = user_stats.stats[member.id]['next_rank']
    user_xp = user_stats.stats[member.id]['xp']
    strikes = server_stats.strikes(guild)
    user_strikes = strikes[member.id]
    roles_requirements = server_stats.stats[guild.id]['roles_requirements']
    if next_rank in roles_requirements.keys():
        if roles_requirements[next_rank]['xp'] <= user_xp and roles_requirements[next_rank]['strikes'] >= user_strikes:
            old_rank = discord.utils.get(guild.roles, name= user_stats.stats[member.id]['rank'])
            new_rank = discord.utils.get(guild.roles, name = next_rank)
            await promote(old_rank, new_rank, member,server_stats)

def sort_by_newest(dictionary:dict):
    log_dict = dictionary.copy()
    sort_full_logs = {}
    for user,msg_list in log_dict.items():
        for time_obj,msgs in msg_list.items():
            if isinstance(time_obj,int):
                time_obj, user = user, time_obj
            if time_obj not in sort_full_logs:
                sort_full_logs[time_obj] = {}
            if user not in sort_full_logs[time_obj]:
                sort_full_logs[time_obj][user] = []
            for msg in msgs:
                sort_full_logs[time_obj][user].append(msg)
    return dict(sorted(sort_full_logs.items()))#.items is crucial here to not loose connection to the values

async def check_spam_without_punishment():
    global is_user_spamming
    global logs_temp
    del_old_logs()
    is_user_spamming = {}
    for user, message_logs in logs_temp.items():
        all_msg_per_user = []
        for message_list in message_logs.values():
            if isinstance(message_list,int):
                continue
            for message in message_list:
                all_msg_per_user.append(message)
        all_percentages = []
        start = 0
        not_compared_msgs = all_msg_per_user.copy()
        for msg in all_msg_per_user:
            if len(all_msg_per_user) == 1:
                all_percentages = [0]
                break 
            try:
                start = not_compared_msgs.index(msg, start)
            except ValueError:
                continue
            index = start
            not_compared_msgs = not_compared_msgs[index+1:]
            avg_percentage = []
            msg_to_remove = []
            for next_msg in not_compared_msgs:
                match_perc = difflib.SequenceMatcher(a= next_msg, b= msg).ratio()
                msg_to_remove.append(next_msg)
                avg_percentage.append(match_perc)
            if len(avg_percentage) > 0:
                print(statistics.median(avg_percentage))
                all_percentages.append(statistics.median(avg_percentage))
            else:
                avg_percentage = 0

        if len(all_percentages) > 0:
            user_match_percentage = statistics.median(all_percentages)
            print(user_match_percentage)
            if user_match_percentage > 0.92:
                if len(all_msg_per_user) > 5:
                    is_user_spamming[user] = True
            else:
                is_user_spamming[user] = False
        else:
            is_user_spamming[user] = False

    for user, is_spam in is_user_spamming.items():
        if is_spam:
            return True
    return False

async def check_spam(client,server_stats):
    await check_spam_without_punishment()
    await spam_punishment(client,server_stats)
    
async def spam_punishment(client,server_stats):
    global logs_temp
    for user in is_user_spamming:
        guild = client.get_guild(logs_temp[user].get('guild_id'))
        if guild is None:
            return #if server got removed
        channel = discord.utils.get(guild.channels,name= admin_channel_name) # admin channel
        if is_user_spamming[user]:
            user_name = client.get_user(user)
            await channel.send(f'User {user_name} is spamming.')
            user_obj = guild.get_member(user)
            if user_obj == None:
                user_obj = client.fetch_user(user)
            await add_strike_code(user_obj,server_stats, 1)
            logs_temp[user] = {}
            is_user_spamming[user] = False
            break

#checks for slurs in the message function
async def check_slurs_without_punishment(message: discord.Message|commands.Context =  None, text = None, has_file = False):
    if message != None: 
        channel = message.channel.name
    else:
        channel = 'general'
    if text != None:
        user_message = text
    else:
        user_message = message.content
    if has_file != False:
        reason = 'sending an image containing'
    else:
        reason = 'sending'
    if channel != 'spam':
        user_message = user_message.lower().strip('?’=,.\'.').replace('@', 'a').replace('1', 'i').replace('!', 'i').replace('ĝ','g').replace('é', 'e').replace('ř', 'r').replace('4','a').replace('1','i').replace('3', 'e').replace('5','s').replace('8', 'o')
        for word in forbidden_words:
            if re.findall(r'(?<![a-z])('+word+r'){1,}(?![a-z])',user_message):
                return True, reason, word
    return False, reason, ""
    


async def check_slurs(message: discord.Message | commands.Context, server_stats:Server_stats, client:commands.Bot, text = None, has_file = False):
    username = message.author.name
    is_slur, reason, word = await check_slurs_without_punishment(message,text,has_file)
    if is_slur:  
        guild = message.guild   
        strikes = server_stats.strikes(guild)
        channel_admin = discord.utils.get(guild.channels, name = admin_channel_name) #admin channel
        await add_strike_code(message.author,server_stats, '1', await client.get_context(message))
        try:
            await message.author.send(f'You got one strike for {reason}: {word}. Please be sure to follow the server rules or else you could be timed out or banned.\nYou currently have {str(strikes[message.author.id])} strikes.')
            await channel_admin.send(f'User {message.author.name} got one strike for {reason}: {word}.\nUser {message.author.name} currently has {str(strikes[message.author.id])} strikes.')
        except discord.Forbidden:
                await message.reply(f'User {username} got one strike for {reason}: {word}.\nThis message was sent in admin because I cannot send DM to {message.author} (DMs disabled or blocked).')
        except Exception as e:
            print(e)
            await message.reply(f'An unexpected error occured while trying to send strike warning to {username}.\nError: {e}',delete_after=5)
        await delete_message(message)
