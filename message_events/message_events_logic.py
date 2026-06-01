import discord
from shared_vars import admin_channel_name, Server_stats, commands, forbidden_words
from user_management.user_management_logic import promote
import difflib
from user_management.user_strikes import add_strike_code
import statistics
from message_events.message_management_logic import del_old_logs, delete_message
import re

async def rank_check(member: discord.Member, server_stats:Server_stats):
    """Promotes a member to the next rank (discord role) if the needed requirements are met. 

    Args:
        member (discord.Member): The member to be promoted.
        server_stats (Server_stats): The server stats.
    """
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
    """Sorts the logs dictionary from newest to oldest.

    Args:
        dictionary (dict): The logs dictionary.

    Returns:
        dict: The sorted dictionary.
    """
    log_dict = dictionary.copy()
    sort_full_logs = {}
    for user,msg_list in log_dict.items():
        for time_obj,msgs in msg_list.items():
            if time_obj == 'guild_id':
                continue
            if isinstance(time_obj,int):
                time_obj, user = user, time_obj
            if time_obj not in sort_full_logs:
                sort_full_logs[time_obj] = {}
            if user not in sort_full_logs[time_obj]:
                sort_full_logs[time_obj][user] = []
            for msg in msgs:
                sort_full_logs[time_obj][user].append(msg)
    return dict(sorted(sort_full_logs.items(), reverse=True))#.items is crucial here to not loose connection to the values

async def check_spam_without_punishment(guild:discord.Guild, server_stats:Server_stats) -> bool:
    """Checks if the messages in the guilds temp logs are spam.

    Args:
        guild (discord.Guild): The guild to check the spam in.
        server_stats (Server_stats): The server stats.

    Returns:
        bool: Returns True if at least one user is spamming else False.
    """
    global is_user_spamming
    TEMP_LOGS = server_stats.stats[guild.id]['temp_logs']
    await del_old_logs(server_stats)
    is_user_spamming = {}
    for user, message_logs in TEMP_LOGS.items():
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
                    is_user_spamming[f'{user}#{guild.id}'] = True
            else:
                is_user_spamming[f'{user}#{guild.id}'] = False
        else:
            is_user_spamming[f'{user}#{guild.id}'] = False

    for user, is_spam in is_user_spamming.items():
        if is_spam:
            return True
    return False

async def check_spam(client:commands.Bot, guild:discord.Guild,server_stats:Server_stats):
    """Checks spam and applies the corresponding punishment to each user.

    Args:
        client (commands.Bot): The discord bot.
        guild (discord.Guild): The guild to check spam for.
        server_stats (Server_stats): The server stats.
    """
    await check_spam_without_punishment(guild, server_stats)
    await spam_punishment(client,server_stats)
    
async def spam_punishment(client:commands.Bot,server_stats:Server_stats):
    """Applies punishment for all users spamming.

    Args:
        client (commands.Bot): The discord bot.
        server_stats (Server_stats): The server stats.
    """
    for user in is_user_spamming:
        user_id = int(user.split('#')[0])
        guild = client.get_guild(int(user.split('#')[1]))
        if guild is None:
            continue #if server got removed
        channel = discord.utils.get(guild.channels,name= admin_channel_name) # admin channel
        if is_user_spamming[user]:
            user_obj = guild.get_member(user_id)
            if not user_obj:
                user_obj = await guild.fetch_member(user_id)
            await channel.send(f'User <@{user_id}> is spamming.',allowed_mentions=discord.AllowedMentions(users=False))
            await add_strike_code(user_obj,server_stats, 1,reason='Spamming')
            is_user_spamming[user] = False
            break

#checks for slurs in the message function
async def check_slurs_without_punishment(message: discord.Message|commands.Context =  None, text:str = None, has_file = False) -> tuple[bool,str,str]:
    """Checks a message or a command context for slurs without applying punishment. If an image text should be checked, the message parameter can be ignored.

    Args:
        message (discord.Message | commands.Context, optional): The message or command context to check for slurs. Defaults to None.
        text (str, optional): The text on an image to be checked. Defaults to None.
        has_file (bool, optional): If the message contained an image. Defaults to False.

    Returns:
        tuple[bool,str,str]: A tuple containing: 
                                - True if the slurs were found, else False.
                                - The source of the slurs.
                                - The slur word.
    """
    if isinstance(message,commands.Context):
        message = message.message
    if message: 
        channel = message.channel.name
    else:
        channel = 'general'
    if text is not None:
        user_message = text
    else:
        user_message = message.content
    if has_file:
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
    """Checks a message, command context, or an image text for slurs and applies the corresponding punishment.

    Args:
        message (discord.Message | commands.Context): The message or command context to check for slurs.
        server_stats (Server_stats): The server stats.
        client (commands.Bot): The discord bot.
        text (str, optional): The image text. Defaults to None.
        has_file (bool, optional): If a image text should be checked. Defaults to False.
    """
    username = message.author.name
    is_slur, reason, word = await check_slurs_without_punishment(message,text,has_file)
    if is_slur:  
        guild = message.guild   
        strikes = server_stats.strikes(guild)
        channel_admin = discord.utils.get(guild.channels, name = admin_channel_name) #admin channel
        ctx = await client.get_context(message) if isinstance(message,discord.Message) else message
        await add_strike_code(message.author,server_stats, '1',ctx ,reason)
        try:
            await message.author.send(f'You got one strike for {reason}: {word}. Please be sure to follow the server rules or else you could be timed out or banned.\nYou currently have {str(strikes[message.author.id])} strikes.')
            await channel_admin.send(f'User {message.author.name} got one strike for {reason}: {word}.\nUser {message.author.name} currently has {str(strikes[message.author.id])} strikes.')
        except discord.Forbidden:
                await message.reply(f'User {username} got one strike for {reason}: {word}.\nThis message was sent in admin because I cannot send DM to {message.author} (DMs disabled or blocked).')
        except Exception as e:
            print(e)
            await message.reply(f'An unexpected error occured while trying to send strike warning to {username}.\nError: {e}',delete_after=5)
        await delete_message(message)
