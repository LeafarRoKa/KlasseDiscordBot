import discord
from shared_vars import admin_channel_name, forbidden_words, JOKES,text_detection_ai,nudity_classification
from stats_system.server_stats import Server_stats,commands
from user_management.user_management_logic import promote
import difflib
from user_management.user_strikes import add_strike_code
import statistics
from message_events.message_management_logic import del_old_logs, delete_message
import re
from utils.typing_utils import enforce_guild,GuildMessage,Initialized_Bot,GuildContext
from user_management.user_management_logic import get_member
import random
import typing
import asyncio



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
            old_rank = discord.utils.get(guild.roles, name=user_stats.stats[member.id]['rank'])
            new_rank = discord.utils.get(guild.roles, name =next_rank)
            if old_rank is None or new_rank is None:
                return#FIXME TODO set it so they have to redifine a new role if this doesn't work bcs they removed it.
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

async def check_spam(client:Initialized_Bot, guild:discord.Guild,server_stats:Server_stats,message:GuildMessage):
    """Checks spam and applies the corresponding punishment to each user.

    Args:
        client (Initialized_Bot): The discord bot.
        guild (discord.Guild): The guild to check spam for.
        server_stats (Server_stats): The server stats.
    """
    if await check_spam_without_punishment(guild, server_stats):
        await spam_punishment(client,server_stats,message)
    
async def spam_punishment(client:Initialized_Bot,server_stats:Server_stats,message:GuildMessage):
    """Applies punishment for all users spamming.

    Args:
        client (Initialized_Bot): The discord bot.
        server_stats (Server_stats): The server stats.
    """
    for user in is_user_spamming:
        user_id = int(user.split('#')[0])
        guild_id = int(user.split('#')[1])
        guild = client.get_guild(guild_id)
        if guild is None:
            # if guild_id in server_stats.stats.keys():
            #     server_stats.stats.pop(guild_id)  FIXME add a coutdown for removing data on remove and then remove it only on that date instead of instantly removing it.
            continue #if server got removed 

        channel = discord.utils.get(guild.channels,name=admin_channel_name) # admin channel
        if is_user_spamming[user]:
            user_obj = await get_member(guild,user_id)
            if not user_obj:
                user_obj = await guild.fetch_member(user_id)
            if not channel or not isinstance(channel,discord.TextChannel):
                return
            await channel.send(f'User <@{user_id}> is spamming.',allowed_mentions=discord.AllowedMentions(users=False))
            await add_strike_code(user_obj,server_stats, message,1,reason='Spamming')
            is_user_spamming[user] = False
            break

#checks for slurs in the message function
def check_slurs_without_punishment(message: discord.Message|GuildMessage|GuildContext|None =  None, text:str|None = None, has_file:bool = False) -> tuple[bool,str,str]:
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
        if not isinstance(message.channel, discord.abc.GuildChannel):
            raise TypeError('The message has to be sent in a Guild.')
        channel = message.channel.name
    else:
        channel = 'general'
    if text is not None:
        user_message = text
    else:
        if not message:
            return False,'', ''
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

async def check_slurs(message: GuildMessage | GuildContext, server_stats:Server_stats, client:Initialized_Bot, text = None, has_file = False):
    """Checks a message, command context, or an image text for slurs and applies the corresponding punishment.

    Args:
        message (discord.Message | commands.Context): The message or command context to check for slurs.
        server_stats (Server_stats): The server stats.
        client (Initialized_Bot): The discord bot.
        text (str, optional): The image text. Defaults to None.
        has_file (bool, optional): If a image text should be checked. Defaults to False.
    """
    username = message.author.name
    is_slur, reason, word = check_slurs_without_punishment(message,text,has_file)
    if is_slur:
        if isinstance(message,commands.Context):
            message = message.message
        message = enforce_guild(message)  
        guild = message.guild
        strikes = server_stats.strikes(guild)
        admin_channel = discord.utils.get(guild.channels, name=admin_channel_name) #admin channel
        await add_strike_code(message.author,server_stats,message, 1 ,reason)
        try:
            await message.author.send(f'You got one strike for {reason}: {word}. Please be sure to follow the server rules or else you could be timed out or banned.\nYou currently have {str(strikes[message.author.id])} strikes.')
            if isinstance(admin_channel,discord.abc.Messageable):
                await admin_channel.send(f'User {message.author.name} got one strike for {reason}: {word}.\nUser {message.author.name} currently has {str(strikes[message.author.id])} strikes.')
        except discord.Forbidden:
                await message.reply(f'User {username} got one strike for {reason}: {word}.\nThis message was sent in admin because I cannot send DM to {message.author} (DMs disabled or blocked).')
        except Exception as e:
            print(e)
            await message.reply(f'An unexpected error occured while trying to send strike warning to {username}.\nError: {e}',delete_after=5)
        await delete_message(message)

def generalize_message(message_content:str) -> str:
    return message_content.lower().replace('@', 'a').replace('1', 'i').replace('!', 'i').replace('ĝ','g').replace('é', 'e').replace('ř', 'r').strip('?=’,.\'.').replace('4','a').replace('1','i').replace('3', 'e')

def get_matching_return_message(message:GuildMessage) -> str:
    message_content = message.content.lower().strip('?’,.\'.')
    match message_content:
        case 'hello' | 'hi':
            return f'Hello {message.author.name}'
        case 'bye':
            return f'Bye {message.author.name}'
        case 'tell me a joke':
            return random.choice(JOKES)
        case 'what can you do':
            return f'I can respond to basic questions and for commands you can find them all using !help'
        case 'whats new':
            return 'I have a new !gen function that can "generate" python code. I also now have an entire suggestion system.'
        case 'what are some upcoming features':
            return 'Probably some commands that allow you to search things in the internet trough the bot, a !stats command and a new command that lists all the questions that you can ask me (the bot).\nI recieve so many features rn because my creator is really locked in during vacation.'
            pass
        case 'who created you':
            #return f'I was created by the clases greatest Python programmer (even better than Telmo) called Rafael.')
            return f'I was created by only one Python programmer.'
        case 'why didnt my command work':
            return f'If your command wasn\'t answered by me it probably was because you either wrote it in another channel that is not the bot channel, \nyou wrote the false command or you just dont have enough permsions to use that command.'

        case 'can you please ping everyone':
            return f'@everyone <@{message.author.id}> wanted me to ping you all.'
        case _:
            return random.choice(['Unnötige Frage.', 'Give it up twin🥀✌️', "Give it up bro.","Be serious bro.","That’s not it.","Bro please.","Come on bro.","That’s wild.","Bro thought this was smart.","That’s crazy. In a bad way.","Not happening.","Message rejected.","Try again.","Try harder.","Recalculate.","Re-evaluate your choices.","You are lost.","Completely lost.","Orientation missing.","Confidence was there. Logic wasn’t.","That ain’t it.","That’s tough bro.","Bro thought hes tough.","Delete that.","Let’s pretend that didn’t happen.","I’m ignoring this.","No comment.","I refuse.",'Bold move.',"Incorrect move.","Critical thinking left.", "Brain patch missing.","That changed nothing.","Energy wasted.","Time wasted.","Bro typed that confidently but confidence ≠ correctness.","Let’s not.","Just no.","You need a brain reset.","Minimal brain usage.","I’m distancing myself.","Bro why.","Explain yourself.","Just don’t.","Well that’s embarrassing.","This is not it.","I’m logging off mentally.","That’s below expectations. Way below.","Try again tomorrow.","That hurt to read.","Completely unnecessary.","Respectfully no. Disrespectfully also no.","Absolutely not.","At least you tried.", "No shot.","You can’t mean that.","That’s delusional (lightly).","You said that confidently too.","You lost me instantly.","That’s illegal logic.","You typed that willingly.","That’s not defendable.","You overcooked.","You committed too hard.","I’m disappointed in that one.","Even your mom would’ve double-checked that.","Even your mom expected better.","Your mom saw that and logged off.","Your mom would’ve taken five more seconds to write that correctly.","Even your mom knew that wasn’t it.","Even your mom wouldn’t defend that.","Even your mom would’ve googled it first.","Even your mom would’ve edited that.","Even your mom paused before that one.","Even your mom would’ve worded that better.","Even your mom would’ve structured that better."])


async def check_unsafe_text(filepath:str,risk:int=0) -> tuple[bool,int]:
    text_read = typing.cast(list[tuple[list[list[int]],str,float]],await asyncio.to_thread(text_detection_ai.readtext,filepath))
    text_on_img = f' '.join(text[1] for text in text_read if text[2] > 0.5)
    print(f'text_on_img: {text_on_img}')
    is_slur, _, _ = check_slurs_without_punishment(text=text_on_img, has_file=True)
    return is_slur, risk + 5

async def check_unsafe_image_content(filepath,risk:int=0):
    before_check = risk
    security_rating = await asyncio.to_thread(nudity_classification.detect,filepath)
    if security_rating:
        security_rating = max(detection['score'] for detection in security_rating)
    else:
        security_rating = 0
    print(f'Security: {security_rating}')
    if security_rating > 0.7:
        risk += 4
    elif security_rating > 0.75:
        risk += 5 
    elif security_rating > 0.8:
        risk += 6
    return before_check!=risk, risk