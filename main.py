import discord
import os
import random
from dotenv import load_dotenv
from discord.ext import commands, tasks
from datetime import timedelta, datetime, timezone, date, time
import json
import difflib
import math
import statistics
import asyncio
import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
import aiohttp
from io import StringIO
import pytesseract
import platform
import nudenet
import re
import urllib
import easyocr
from pathlib import Path
from stats_system.server_stats import Server_stats, User_stats
load_dotenv('data/.env') 

if platform.system().lower() == 'windows':
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
elif platform.system().lower() == 'linux':
    pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"

text_detection_ai = easyocr.Reader(['en']) # loads AI into that obj
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
command_prefix = '!'
client = commands.Bot(command_prefix= command_prefix, intents = intents)
commands_list = []
logs_temp = {}
is_user_spamming = {}
forbidden_words = []
waiting_confirmations = []
change_confirmations = []
token = os.getenv('TOKEN')
waiting_list  = {}
d_face_reacts = ['skillissue', 'brofailed', 'rip', 'imagine']
allowed_file_endings = ['txt']
allowed_types_in_bytes= [b'\x89PNG',          # PNG
                         b'\xff\xd8\xff',     # JPEG
                         b'GIF87a',           # GIF
                         b'GIF89a',           # GIF
                         b'BM']               # BMP
user_stats = User_stats
headers = {
    "User-Agent": "Mozilla/5.0"
}
permissions_per_role = {1:[discord.Permissions(view_channel=True,create_instant_invite=True,change_nickname=True, send_messages=True, create_polls=True,add_reactions=True,read_message_history=True,connect=True,use_application_commands=True,send_messages_in_threads=True,speak=True),"#2FE489F2"], 2: [discord.Permissions(view_channel=True,create_expressions=True,create_instant_invite=True, change_nickname=True,send_messages=True,send_messages_in_threads=True,create_public_threads=True,embed_links=True,attach_files=True,add_reactions=True,use_external_emojis=True,use_external_stickers=True,read_message_history=True,send_tts_messages=True,send_voice_messages=True,use_soundboard=True,use_external_sounds=True,use_voice_activation=True,use_application_commands=True,use_embedded_activities=True),"#9b59b6"],3:[discord.Permissions(view_channel=True,create_expressions=True,create_instant_invite=True,change_nickname=True,send_messages=True,send_messages_in_threads=True,create_public_threads=True,create_private_threads=True,embed_links=True,attach_files=True,add_reactions=True,use_external_emojis=True,use_external_stickers=True,read_message_history=True,send_tts_messages=True,send_voice_messages=True,connect=True,speak=True,stream=True,use_soundboard=True,use_external_sounds=True,use_voice_activation=True,use_application_commands=True,use_embedded_activities=True,use_external_apps=True), '#d261ff'],
                        4:[discord.Permissions(view_channel=True,create_expressions=True,create_instant_invite=True,change_nickname=True,send_messages_in_threads=True,send_messages=True, create_public_threads=True,create_private_threads=True,embed_links=True,attach_files=True,add_reactions=True,use_external_emojis=True,use_external_stickers=True,read_message_history=True,send_tts_messages=True,send_voice_messages=True,create_polls=True,connect=True,speak=True,stream=True,use_soundboard=True,use_external_sounds=True,use_voice_activation=True,use_application_commands=True,use_embedded_activities=True,use_external_apps=True),'#206694'],
                        5: [discord.Permissions(view_channel=True,create_expressions=True,manage_expressions=True,create_instant_invite=True,change_nickname=True,send_messages=True,send_messages_in_threads=True,create_private_threads=True,create_public_threads=True,embed_links=True,attach_files=True,add_reactions=True,use_external_emojis=True,use_external_stickers=True,read_message_history=True,send_tts_messages=True,send_voice_messages=True,create_polls=True,connect=True,speak=True,stream=True,use_soundboard=True,use_voice_activation=True,priority_speaker=True,use_application_commands=True,use_embedded_activities=True,use_external_apps=True,create_events=True),'#3498db'],
                        6: [discord.Permissions(view_channel=True,manage_roles=True,create_expressions=True,manage_expressions=True,view_audit_log=True,create_instant_invite=True,change_nickname=True,manage_nicknames=True,kick_members=True, moderate_members=True,send_messages=True,send_messages_in_threads=True,create_public_threads=True,create_private_threads=True,embed_links=True,attach_files=True,add_reactions=True,use_external_emojis=True,use_external_stickers=True,mention_everyone=True,manage_messages=True,manage_channels=True,manage_threads=True,read_message_history=True,send_tts_messages=True,send_voice_messages=True,create_polls=True,connect=True,speak=True,stream=True,use_soundboard=True,use_external_sounds=True,use_voice_activation=True,priority_speaker=True,mute_members=True,use_application_commands=True,use_embedded_activities=True,use_external_apps=True,create_events=True,manage_events=True),'#b65bda'],
                        7:[discord.Permissions(view_channel=True,manage_channels=True,manage_roles=True,create_expressions=True,manage_expressions=True,view_audit_log=True,create_instant_invite=True,change_nickname=True,manage_nicknames=True,kick_members=True,moderate_members=True,send_messages=True,send_messages_in_threads=True,create_private_threads=True,create_public_threads=True,embed_links=True,attach_files=True,add_reactions=True,use_external_emojis=True,use_external_stickers=True,mention_everyone=True,manage_messages=True,manage_threads=True,read_message_history=True,send_tts_messages=True,send_voice_messages=True,create_polls=True,connect=True,speak=True,stream=True,use_soundboard=True,use_external_sounds=True,use_voice_activation=True,priority_speaker=True,mute_members=True,deafen_members=True,move_members=True,use_application_commands=True,use_embedded_activities=True,use_external_apps=True,create_events=True,manage_events=True),'#a65cc3'],
                        8:[discord.Permissions(administrator=True),'#e90367'],                        
                        9:[discord.Permissions(administrator=True),'#b300ff']}
full_logs = {}
badges_imgs  = {}
nudity_classification = nudenet.NudeDetector()
event_title = 'Watch party'
event_description = 'watching one randomly selected suggestion.'
days_until_sunday = (6 - date.today().weekday()) % 7
if days_until_sunday == 0:  # If today is Saturday, move to next week
    days_until_sunday = 7
next_sunday = datetime.combine(date.today()+ timedelta(days=days_until_sunday), time(16)) #16 is the time of the day that we watch
months = {'01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'May', '06': 'Jun', '07': 'Jul', '08':  'Aug', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'}
roles_imgs = {'owner': r'images/owner.png', 'mini mod': '','klassebot': r'images/bot.png', 'admin': r"images/admin.png", 'dev': r"images/dev.png", 'trial dev': r"images/trial_dev.png", 'elite member': r'images/lite_member.png', 'member': r"images/member.png", 'beginner': r'images/beginner.png', 'spammer':''}
ending_imgs = ['png','jpeg']
admin_channel_name = 'admin'
bot_channel_name = 'bot'
welcome_channel_name = 'welcome'
event_channel_name = 'events'
goodbye_channel_name = 'goodbye'

with open(r'data/de.txt', 'r') as f:
    for word in set(f):
        forbidden_words.append(word.strip('\n'))

with open(r'data/en.txt', 'r') as f:
    for word in set(f):
        forbidden_words.append(word.strip('\n'))

def open_save_files():
    global code_dict
    try:
        porpouse = 'code'
        with open(r'data/code.json', 'r') as f:
            code_dict = json.load(f)  
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        migrate_or_create(porpouse)

def migrate_or_create(file_type_name:str):
    """
    This function either changes the file path into the data folder or if the file doesn't even exist outside the data folder 
    it creates a blank file with the file_type_name  and the ending .json containing a empty dict.

    Args:
        file_type_name (str): This argument should contain the purpouse of the file. Ex. The porpouse of the file strikes.json is strikes.
    """
    try:
        old_path = f'{file_type_name}.json'
        new_path = f'data/{file_type_name}.json'
        os.rename(old_path, new_path)
    except FileNotFoundError:
        with open(new_path, 'w') as f:
            json.dump({},f)

open_save_files()

with open(r'data/logs.json', 'r') as f:
    save_full_logs = json.load(f)
    full_logs = {}
    for time_str, user_msgs_at_time in save_full_logs.items():
        time_obj = datetime.fromisoformat(time_str)
        if time_obj not in full_logs.keys():
            full_logs[time_obj] = {}
        for user, msgs in user_msgs_at_time.items():
            user = int(user)
            full_logs[time_obj][user] = msgs

def mismatch_message(user_command):
    best_match_percentage = -1
    for command in commands_list:
        match_perecentage = difflib.SequenceMatcher(a = user_command,b = command).ratio()
        if match_perecentage > best_match_percentage:
            best_match_percentage = match_perecentage
            best_matching_command = command
    if best_match_percentage < 0.4:
        return f'Unknown command.\nType !help to see all commands.'
    else:
        return f'Invalid command.\nDid you mean: {best_matching_command}?\nType !help to see all commands.'


@client.event
async def on_command_error(ctx:commands.Context, error:discord.message.Message):
    print(type(error))
    print(error)
    if getattr(error, 'handled', False):#if it doesn't have the attribute it means it wasn't handled and will return the here defined default false so it won't return if it doesn't have the attribute and if it does it only is correct if set to True
        return
    if isinstance(error, commands.RoleNotFound):
        await ctx.reply('The role does not exist.',delete_after=5)
    elif isinstance(error, commands.MissingPermissions):
        await ctx.reply('You lack the permissions to execute this command.',delete_after=5)
    elif isinstance(error, commands.MemberNotFound):
        await ctx.reply('Member not found. Please ensure you mentioned a valid Member.',delete_after=5)
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.reply('I lack the permissions to execute this command. Please contact the bot owner if this behaviour is unexpected.',delete_after=5)
    elif isinstance(error, commands.BadArgument):
        await ctx.reply('Member not found. Please ensure you mentioned a valid Member.',delete_after=5)
    elif isinstance(error, discord.Forbidden):
        await ctx.reply('I am not capable of performing actions for members above or at my same rank.',delete_after=5)
    elif isinstance(error, commands.CommandNotFound):
        await ctx.reply(mismatch_message(str(ctx.invoked_with)),delete_after=5)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply('You are missing an argument.',delete_after=5)
    else:
        await ctx.send('An error has occured while trying to execute this command.',delete_after=5)




@client.event
async def on_ready():
    global server_stats
    server_stats = Server_stats(client)
    server_stats.open_stats()
    server_stats.is_dict_complete()
    is_waiting_expired.start()
    is_dict_overflow.start()
    print(f'Logged in as bot {client}')


async def response_waiting(ctx:commands.Context, time = 30):
    waiting_confirmations.append(ctx.author.id)
    def check(msg: discord.Message):
        return  msg.author != client.user and msg.author == ctx.author and msg.channel == ctx.channel
    try:
        response = await client.wait_for('message', timeout=time, check=check)
    except TimeoutError:
        await ctx.reply('You took too long to respond', delete_after = 8)
        return None
    change_confirmations.append(ctx.author.id)
    return response


async def response_waiting_text(ctx:commands.Context, time=30):
    response = await response_waiting(ctx,time=time)
    if response is None:
        return ''
    return response.content.lower()

async def confirmation(ctx:commands.Context, time=30):
    response = await response_waiting_text(ctx,time=time)
    if response is None:
        return False
    return response in ['y','yes']


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
    


async def check_slurs(message: discord.Message | commands.Context, text = None, has_file = False):
    username = message.author.name
    is_slur, reason, word = await check_slurs_without_punishment(message,text,has_file)
    if is_slur:  
        guild = message.guild   
        strikes = server_stats.strikes(guild)
        channel_admin = discord.utils.get(guild.channels, name = admin_channel_name) #admin channel
        await add_strike_code(message.author, '1', await client.get_context(message))
        try:
            await message.author.send(f'You got one strike for {reason}: {word}. Please be sure to follow the server rules or else you could be timed out or banned.\nYou currently have {str(strikes[message.author.id])} strikes.')
            await channel_admin.send(f'User {message.author.name} got one strike for {reason}: {word}.\nUser {message.author.name} currently has {str(strikes[message.author.id])} strikes.')
        except discord.Forbidden:
                await message.reply(f'User {username} got one strike for {reason}: {word}.\nThis message was sent in admin because I cannot send DM to {message.author} (DMs disabled or blocked).')
        except Exception as e:
            print(e)
            await message.reply(f'An unexpected error occured while trying to send strike warning to {username}.\nError: {e}',delete_after=5)
        await delete_message(message)

@client.event
async def on_message(message:discord.Message):
    if 'server_stats' not in globals():
        return        
    guild = message.guild
    global full_logs
    sideeye_reactions = ['trust me', 'trust me bro', '100%']
    skillissue_reactions = ['why doesnt','why doesn\'t','it doesn\'t work', 'it doesnt work','how do i', 'error','broken', 'i lost', 'i messed up']
    iq_reactions = ['actually', 'you can just','instead do']
    sus_reactions = ['hypothetically','dont ask why','for a friend','i have a girlfriend', 'i have a gf', 'i have a bf', 'i have a boyfriend',"i dont lose","i don’t lose","i never lose","i never miss","too easy","light work","i calculated it","i calculated that","we’ll see","well see","im built different","i knew that","obviously","trust me","trust me bro","it’s proven","its proven","they don’t want you to know","they dont want you to know",]
    fight_starting_reactions = ['actually', 'technically','well', 'no, because']
    one_word_akward = ['ok', 'cool','hello','hi guys']
    npc_reactions = ['good morning','im bored','how are you', 'whats up', 'what\'s up','anyone here']
    overdramatic_reactions = ['“my code has one error','it’s over', 'its over', 'i’m done', 'im done','this is the end', 'i quit', 'i can’t anymore', 'i cant anymore', 'worst day ever', 'i’m finished', 'in finished', 'i am finished','why does this always happen to me','of course', 'just my luck','i’m cursed', 'im cursed', 'i am cursed',"that’s it","thats it","i’m done",'i’m leaving',"im leaving","goodbye forever","i’m done with this server","im done with this server","you won’t see me again","you wont see me again","this server fell off"]
    absolute_cinema_reactions = ["you will regret this","remember this","this is your last warning","im done","watch what happens","you have no idea","mark my words","it begins","this changes everything","just wait","this isn’t over","this isnt over", "say that again","i’m built different","listen carefully",]
    not_to_use = [ "die", "dead", "death", "suicide", "funeral", "grave","mother", "father", "mom", "dad", "grandmother", "grandfather","sister", "brother", "uncle", "aunt", "cousin", "pet","depression", "anxiety", "panic", "therapy", "suicidal","selfharm", "relapse","divorce", "abuse", "harassment", "assault","war", "accident", "hospital", "cancer"]
    
    gif_reactions =  {

    'skillissue' : ['https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExbmEwZWQycXFxY2Z2d200ZjQzYWhuZjdlcXdvY2c0NnRnb3ZqdWhvYyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/5pGd4XRmJY1Zt1Lv00/giphy.gif',
                  'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExODF6cmtzbDgyaDIweGxwOHR6Nm9wanpvMGc4em93bDR4eWN1bmJicSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/8J1QwMjshEm2s/giphy.gif',
                  'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExc3N1OXE3bWRhODFlZDZ4ODNodDgxcTd6MmJ2Z3Jxdmx1YWdqOGVvcyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/kKEeiM9TshxZ1FfZ8U/giphy.gif'],
    'iq': ['https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMjUxOTYxano2YTVidDRpeWNvcnlwZXp0ZGhnZWg2cHZnZHl1Y2d6YSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/TYmReKrevWMHXSIfWb/giphy.gif',
          'https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExeHhxYmczaGFseWRmNXNxaHBuZjA4d2t5bzZkcnpkcnVmaTI3bzhodSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/26ufdipQqU2lhNA4g/giphy.gif'],
          'absolute_cinema' : 'https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExdWV1bXQzZXlwdDZtc2NhcXh4azRpdXl2emN4bmQzYW41ZHZkNHU0cyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/9EvnXdZaUZbCqScn67/giphy.gif',
    'sus':['https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcWpoc29vc281Ymg5dHJtNmUwdDk2ZzU5M2JxZmIzZXAyN3podmEyaSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/yxy69FCE06Ql0Fjk4Z/giphy.gif',
           'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOHV0bHVmMjd2eWp4YjhndHB1cXBhdGE1aXBjZnYyaWlzdTNmczBrciZlcD12MV9naWZzX3NlYXJjaCZjdD1n/H5C8CevNMbpBqNqFjl/giphy.gif',
           'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExamxibnV5MmMyNTZ3ZmtjeTZnaHhnNzVleTE0cWJ5eWR3c2JhZnpwdyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/QxcSqRe0nllClKLMDn/giphy.gif'],
    'fight_starting': ['https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExOWwyOWIza3M0ZXY2d2NheXZqZHJlamY1dTVxdmZzcHV2YWI4Zm1iMCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Ih1pUh3PrRfOSM5TsI/giphy.gif',
                      'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMjlpdmIwN3pscnM3amVtbm1ocmt2bnpvbzd2eWhhbWIweDR0NXkzdyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/NTur7XlVDUdqM/giphy.gif'],
    'overdramatic': ['https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYnJlbmp3cDNsazh2cnY1dHRqYmUycmlrc3V3Mmg3eWk3ajZkajIwZyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/7lO3u8uZwvPiiUh67z/giphy.gif',
                    'https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExaXkwaDIybDBmbDN0djRlbGVrcWZxajI3dnczd2dxajhqYWIza256YyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/JER2en0ZRiGUE/giphy.gif'],
    'akward_silence': ['https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExd3N5cWFqOGduZ3lwZzZ1MWw0NzFneTdxbG96bjlnMjA4aGZmMHVjcyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/iznHg9hhwfXN5zTQp3/giphy.gif'],
    'npc_moments' : ['https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExc2h6czFhZHFieml5ZWc0YXVlNGdodm9hZ2lpNHN0b3dtOGh2MWJ0dSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/hEAfUHAx1ycVKhySnA/giphy.gif'],
    'chaos': ['https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExam92aTdqYnU1c2w1YXV1ZHFldzd2Njh0cWYwZ2UyMGY3YXY1OHB2NyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/XbnSI4OJqKevcUAamj/giphy.gif',
            'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdGZmY2NkaTkwa3Q1Z3pxanJzdGQ3aG01NnZibTgybnVoeHduNHdwaiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/NTur7XlVDUdqM/giphy.gif',
            'https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExMmJra3FnNGpqcnJ3enYya2U4cXRia3RrN2VrNThucHU1MnlzYXdsNiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/MZocLC5dJprPTcrm65/giphy.gif']
    }
    
    
    dont_send= False
    for word in not_to_use:
        if word in message.content.lower().replace('@', 'a').replace('1', 'i').replace('!', 'i').replace('ĝ','g').replace('é', 'e').replace('ř', 'r').strip('?=’,.\'.').replace('4','a').replace('1','i').replace('3', 'e').replace('5','s').replace('8', 'o'):
            dont_send= True
            break
    
    if dont_send == False:
        #reacting to messages
        if message.content.lower().strip() in d_face_reacts:
            if random.randint(1, 10) == 1:
                await message.add_reaction('\\<:DFace:1470918226446782763>')
                return
    
        for text in sideeye_reactions:
            if text in message.content.lower():
                if random.randint(1,5) == 1:
                    if random.randint(1,3) == 2:
                        await message.reply(random.choice(['https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExem16OG5jZTVpMzg4eHJyZWM5NmI5ZHd0YXJoZGZidTd2cXAwNWllcyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/9G1pzYSsO90rBapiEv/giphy.gif',
                                        'https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExdXNwN2dvbHV5em9jdndqYnZ6NjdxZDR5MnoxaTcwdW5nbzUyZWZ3bCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/cFgb5p5e1My3K/giphy.gif']))
                        break
                    else:
                        await message.add_reaction('🤨')
                        break
        for text in skillissue_reactions:
            if text in message.content.lower():
                if random.randint(1,5) == 1:
                    if random.randint(1,3) == 2:
                        await message.reply(random.choice(gif_reactions['skillissue']))
                        break
                    await message.add_reaction(random.choice(['💀', '\\<:embarassing:1471526438057410763>','🤡']))
                    break   

        for text in iq_reactions:
            if text in message.content.lower():
                if random.randint(1,8) == 1:
                    if random.randint(1,5) == 4:
                        await message.reply(random.choice(gif_reactions['iq']))
                        break
                    await message.add_reaction(random.choice(['🧠', '🤯', '🔥']))
                    break
        
        for text in sus_reactions:
            if text in message.content.lower():
                if random.randint(1,5) == 1:
                    if random.randint(1,3) == 2:
                        await message.reply(random.choice(gif_reactions['sus']))
                        break
                    await message.add_reaction(random.choice(['🤨', '😳', '👀','\\<:pause:1471529450712731860>' ]))
                    break

        for text in one_word_akward:
            if text == message.content.lower():
                if random.randint(1,5) == 1:
                    if random.randint(1,3) == 2:
                        await message.reply(random.choice(gif_reactions['akward_silence']))
                        break
                    await message.add_reaction(random.choice(['😐', '😶', '🦗','\\<:embarassing:1471526438057410763>']))
                    break

        for text in npc_reactions:
            if text in message.content.lower():
                if random.randint(1,5) == 1:
                    if random.randint(1,3) == 2:
                        await message.reply( random.choice(gif_reactions['npc_moments']))
                        break
                    await message.add_reaction(random.choice(['🤖','\\<:NPC:1471531032447684834>','\\<:bot:1471531101381066886>']))
                    break

        

        for text in fight_starting_reactions:
            if text in message.content.lower():
                if random.randint(1,5) == 1:
                    await message.channel.send(random.choice(gif_reactions['fight_starting']))
                    break

        if message.content.upper() == message.content and '!' in message.content:
            if random.randint(1,8) == 1:
                await message.channel.send(random.choice(gif_reactions['chaos']))
        
        for text in overdramatic_reactions:
            if text in message.content.lower():
                if random.randint(1,5) == 1:
                    await message.channel.send(random.choice(gif_reactions['overdramatic']))
        
        for text in absolute_cinema_reactions:
            if text in message.content.lower():
                if random.randint(1,4) == 1:
                    await message.channel.send(random.choice(gif_reactions['absolute_cinema']))
            
    if message.guild and message.guild.id != guild.id:#print('Mesage was sent in the wrong server.')
        return
    elif not message.guild:#print('Message was sent in a dm.')
        return
    user_stats = server_stats.user_stats(guild)

    #prevents the bot from responding to himself
    if message.author.id == client.user.id:
        if server_stats.stats[guild.id]['set_up'] is True:
            user_stats.add_msg(message.author)
        return
    
    if server_stats.stats[guild.id].get('set_up') is not None and server_stats.stats[guild.id].get('set_up') is False:
        if message.content.lower() != '!setup':
            #checks if the user was doing a confirmation
            if message.author.id in waiting_confirmations:
                if message.author.id in change_confirmations:
                    waiting_confirmations.remove(message.author.id)
                    change_confirmations.remove(message.author.id)
                return
            await message.channel.send('You have to set up the bot with !setup to be able to use the bot.')
        else:
            await client.process_commands(message)
        return
    
    
    #logs the sent message
    log(logs_temp,message,with_guild=True)
    log(full_logs, message)
    full_logs = sort_by_newest(full_logs)
    save_full_logs = {}
    for time_obj, user_msgs_at_time in full_logs.items():
        time_obj = str(time_obj)
        if time_obj not in save_full_logs.keys():
            save_full_logs[time_obj] = {}
        for user, msgs in user_msgs_at_time.items():
            user = str(user)
            save_full_logs[time_obj][user] = msgs
    server_stats.save_stats()
    if message.channel != 'spam':
        await check_spam() #checks if the messages are spam

    username = str(message.author).split('#')[0]
    try:
        channel = message.channel.name
    except AttributeError:
        channel = 'DM channel'

    channel_id = message.channel.id
    user_message = str(message.content)
    guild_name = guild.name
    print(f'Message {user_message} was sent by {username} in the following channel: {channel} in the server {guild_name}')
    strikes  = server_stats.strikes(guild)
    #returns a score between 0 and 1 about how save a img object is
    async def check_image_safety(attachment_in_bytes:bytes):
        risk = 0
        with Image.open(BytesIO(attachment_in_bytes)) as img:
            img = img.convert('L')
            text_on_img = ''
            filepath = r'images/sent_img.png'
            img.save(filepath,format='PNG')
            text_read = await asyncio.to_thread(text_detection_ai.readtext,filepath)
            for text in text_read:
                text_on_img += f' {text[1]} '
                print(text[1])
            print(f'text_on_img: {text_on_img}')
            is_slur, _, _ = await check_slurs_without_punishment(text=text_on_img, has_file=True)
            if is_slur:
                risk += 5
                print('Unsafe image content')
            security_rating = await asyncio.to_thread(nudity_classification.detect ,filepath)
            os.remove(filepath)
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
            if risk == 5 or risk == 4:
                channel = discord.utils.get(guild.channels,name= admin_channel_name)
                await channel.send(f'Flagged image from user <@{message.author.id}>.\nIts risk was rated {risk}/9.\nLink to message {message.jump_url}.',allowed_mentions=discord.AllowedMentions(users=True))
            elif risk > 5:
                channel_admin = discord.utils.get(guild.channels,name= admin_channel_name)
                await add_strike_code(message.author, '1', await client.get_context(message))
                reason = 'sending an explicit image'
                try:
                    await message.author.send(f'You got one strike for {reason}. Please be sure to follow the server rules or else you could be timed out or banned.\nYou currently have {str(strikes[message.author.name])} strikes.',allowed_mentions=discord.AllowedMentions(users=False))
                    await channel_admin.send(f'User <@{message.author.id}> got one strike for {reason}.\nUser <@{message.author.id}> currently has {str(strikes[message.author.name])} strikes.',allowed_mentions=discord.AllowedMentions(users=False))
                except discord.Forbidden:
                    await message.send(f'User <@{message.author.id}> got one strike for {reason}.\nThis message was sent in admin because I cannot send DM to <@{message.author.id}> (DMs disabled or blocked).',allowed_mentions=discord.AllowedMentions(users=False))
                except Exception as e:
                    print(e)
                    await channel_admin.send(f'An unexpected error occured while trying to send strike warning to <@{message.author.id}>.\nError: {e}',allowed_mentions=discord.AllowedMentions(users=False))
                await delete_message(message)
    
    #calls function to check for slurs and other not safe content 
    urls = re.findall(r'https?://\S+', message.content)
    async with aiohttp.ClientSession() as session:
        for url in urls:
            print('Found url')
            try:
                print('Opened Session')
                async with session.head(url,headers=headers) as page:
                    print('opened page')
                    try:
                        size_in_bytes = page.headers.get('Content-Length')#gets the data from the page label for type of the content like a label on a package about the package content
                        if size_in_bytes != None:
                            size_in_bytes = int(size_in_bytes)
                            if size_in_bytes <= 20_000_000:
                                async with session.get(url, timeout=10) as page:
                                    url_image = await page.read()
                                    try:
                                        print(type(url_image))
                                        if not any(url_image.startswith(bytes_starting) for bytes_starting in allowed_types_in_bytes):
                                            raise(TypeError)
                                        image_to_check = Image.open(BytesIO(url_image))
                                        image_to_check.verify()
                                    except UnidentifiedImageError:
                                        continue
                                    except TypeError:
                                        await delete_message(message)
                                        print('Why did it not delete')
                                        print(type(message))
                                        await message.channel.send('Please only use not expired image links.')
                                        continue
                                    except Exception as e:
                                        print(e)
                                        continue
                                    #print('Will check image safety')
                                    await check_image_safety(url_image)#TODO for every ten to twenti frames in a gif check its image safety
                    except urllib.error.HTTPError:
                        print('entered exception')
                        async with session.get(url) as page:
                            bytes_downloaded = 0
                            file_parts = []
                            for file_part in page.content.iter_chunked(1024):
                                bytes_downloaded += len(file_part)#gets how many bites long the file part is and adds it to the total
                                if bytes_downloaded > 20_000_000:
                                    raise(KeyError)
                                file_parts.append(file_part)
                            url_image = b''.join(file_parts)
                            await check_image_safety(url_image)
            except asyncio.TimeoutError:
                print('timed out')
                await message.channel.send('Please only use not expired image links.')
                await delete_message(message)
            except KeyError:
                channel = discord.utils.get(guild.channels,name= admin_channel_name)
                await channel.send(f'Flagged image from user {message.author.name}.\nIts image size was greater than 20MB/9.')
                await channel.send(f'Message link {message.jump_url}')

        if message.attachments:
            for attachment in message.attachments:
                if any(attachment.filename.lower().endswith(ending) for ending in ending_imgs):
                    attachment_in_bytes = await attachment.read()
                    await check_image_safety(attachment_in_bytes)
                            
        print(type(message))
        await check_slurs(message)

        #levels up the stats
        server_stats.stats[guild.id]['user_stats'].add_msg(message.author)
        server_stats.save_stats
        await rank_check(message.author)

        allowed_channels = server_stats.stats[guild.id]['allowed_channels']        
        #checks if the message was sent in another channel and if thats true it checks if the bot was mentioned.
        if allowed_channels:
            if channel_id not in allowed_channels.values(): #checks if the channel wich the message was sent in is allowed.
                if message.channel.name.lower() != 'admin':
                    if client.user not in message.mentions and message.mentions != f'<{client.user.id}>':
                        return
                    if user_message.replace(f'<@{str(client.user.id)}>', '').strip().startswith(command_prefix):
                            reply = await message.reply(f'Please use the bot commands channel for bot commands.', delete_after = 5) # later adapt it so it "pings" the bot commands channel.
                            await asyncio.sleep(5)
                            await delete_message([message,reply])
                            return
                
    #checks if the user was doing a confirmation
    if message.author.id in waiting_confirmations:
        if message.author.id in change_confirmations:
            waiting_confirmations.remove(message.author.id)
            change_confirmations.remove(message.author.id)
        return
    
    #makes the text readable
    for mention in message.mentions:
        user_message =  user_message.replace(f'<@{mention.id}>', '').strip()
    if user_message.startswith(command_prefix):
        await client.process_commands(message)
        return
    winner_user = server_stats.winner_user(guild)
    winner_content = server_stats.winner_content(guild)
    if not dont_send:
    #Starting from here the rest is responses to normal messages
        if user_message.lower() == 'hello' or user_message.lower() == 'hi':
            await message.channel.send(f'Hello {username}')
        elif user_message.lower().strip('?.') in ['what are we watching this sunday', 'what are we going to watch this sunday']:
            if winner_user:
                if winner_user != 1:
                    await message.channel.send(f'<@{winner_user.id}> will be hosting **{winner_content}** this sunday.',allowed_mentions = discord.AllowedMentions(users=False))
                    return
                await message.channel.send(f'<@{winner_user.id} is currently hosting **{winner_content}** in the General VC.', allowed_mentions = discord.AllowedMentions(user=False))
                return
            await message.channel.send('The winner suggestion will only be determined this sunday one hour before the event.')
            return
        elif user_message.lower() == 'bye':
            await message.channel.send(f'Bye {username}')

        elif user_message.lower() == 'tell me a joke':
            jokes = ['Can someone please shed more'
                        'light on how my lamp got stolen?',
                        'Why is she called llene? She'
                        'stands on equal legs.',
                        'What do you call a gazelle in a '
                        'lions territory? Denzel.']
            await message.channel.send(random.choice(jokes))
        elif user_message.lower().strip('?') == 'what can you do':
            await message.channel.send(f'I can respond to basic questions and for commands I can:\n'
                                    'play ping pong (!Ping).\nlist the amount of strikes you have (!my_strikes).\ngive you a list of all the roles in this server (!list_roles).\nMaybe upcoming features.\n(Please note that all the following features are not garanteed to be introduced.):\n' \
                                    'A internet search possibility if asked to the bot' \
                                    'Some new roles.')
        elif user_message.lower().strip('?\'') == 'whats new':
            await message.channel.send('I have a new !gen function that can "generate" python code. I can now respond with gifs and react with emojis.')
        elif user_message.lower().strip('?\'') == 'what are some upcoming features':
            await message.channel.send('Probably some commands that allow you to search things in the internet trough the bot, a !stats command and a new command that lists all the questions that you can ask me (the bot).\nI recieve so many features rn because my creator is really locked in during vacation.')
            pass
        elif user_message.lower().strip('?’,.\'.') == 'who created you':
            await message.channel.send(f'I was created by the clases greatest Python programmer (even better than Telmo) called Rafael.')
        elif user_message.lower().strip('?\'') == 'why didnt my command work':
            await message.channel.send(f'If your command wasn\'t answered by me it probably was because you either wrote it in another channel that is not the bot channel, \nyou wrote the false command or you just dont have enough permsions to use that command.') 

        else:
            await message.channel.send(random.choice(['Unnötige Frage.', 'Give it up twin🥀✌️', "Give it up bro.","Be serious bro.","That’s not it.","Bro please.","Come on bro.","That’s wild.","Bro thought this was smart.","That’s crazy. In a bad way.","Not happening.","Message rejected.","Try again.","Try harder.","Recalculate.","Re-evaluate your choices.","You are lost.","Completely lost.","Orientation missing.","Confidence was there. Logic wasn’t.","That ain’t it.","That’s tough bro.","Bro thought hes tough.","Delete that.","Let’s pretend that didn’t happen.","I’m ignoring this.","No comment.","I refuse.",'Bold move.',"Incorrect move.","Critical thinking left.", "Brain patch missing.","That changed nothing.","Energy wasted.","Time wasted.","Bro typed that confidently but confidence ≠ correctness.","Let’s not.","Just no.","You need a brain reset.","Minimal brain usage.","I’m distancing myself.","Bro why.","Explain yourself.","Just don’t.","Well that’s embarrassing.","This is not it.","I’m logging off mentally.","That’s below expectations. Way below.","Try again tomorrow.","That hurt to read.","Completely unnecessary.","Respectfully no. Disrespectfully also no.","Absolutely not.","At least you tried.", "No shot.","You can’t mean that.","That’s delusional (lightly).","You said that confidently too.","You lost me instantly.","That’s illegal logic.","You typed that willingly.","That’s not defendable.","You overcooked.","You committed too hard.","I’m disappointed in that one.","Even your mom would’ve double-checked that.","Even your mom expected better.","Your mom saw that and logged off.","Your mom would’ve taken five more seconds to write that correctly.","Even your mom knew that wasn’t it.","Even your mom wouldn’t defend that.","Even your mom would’ve googled it first.","Even your mom would’ve edited that.","Even your mom paused before that one.","Even your mom would’ve worded that better.","Even your mom would’ve structured that better."]))


def log(log:dict,message:discord.Message,with_guild = False):
    if message.author.id not in log.keys():
        if with_guild:                     
            log[message.author.id] = {'guild_id':message.guild.id}
        else:
            log[message.author.id] = {}  
    if message.created_at not in log[message.author.id].keys():
        log[message.author.id][message.created_at]  = []
    log[message.author.id][message.created_at].append(message.content)

@client.event
async def on_member_update(before: discord.Member, after: discord.Member):
    guild = before.guild
    if not any(after.id == member.id for member in guild.members):
        return
    if server_stats.stats[guild.id].get('set_up') is not None and server_stats.stats[guild.id].get('set_up') is False:
        return
    if before.roles != after.roles:
        server_stats.stats[guild.id]['user_stats'].update_rank(after,server_stats.stats[guild.id]['server_roles'])


async def rank_check(member: discord.Member):
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
            await promote(old_rank, new_rank, member)

async def promote(old_role: discord.Role, new_role: discord.Role, member: discord.Member):
    guild = member.guild
    await remove_role_logic(member, old_role)
    await give_role_logic(member, new_role)
    user_stats = server_stats.user_stats(guild)
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

@client.command(help='The bot responds with Pong to this cmd.',brief='')
async def ping(ctx):
    await ctx.send('Pong!')

@tasks.loop(seconds=10)
async def is_dict_overflow():
    while len(full_logs) > 500:
        full_logs.pop(next(iter(full_logs)))#removes the first entered key value pair
    save_full_logs = {}
    for time_obj, user_msgs_at_time in full_logs.items():
        time_obj = str(time_obj)
        if time_obj not in save_full_logs.keys():
            save_full_logs[time_obj] = {}
        for user, msgs in user_msgs_at_time.items():
            user = str(user)

            save_full_logs[time_obj][user] = msgs
    with open(r'data/logs.json', 'w') as f:
         json.dump(save_full_logs, f)

@client.command(help='This cmd sets the xp of the given user to the amount given.',brief='Sets a users_xp to a given amount.')
@commands.has_permissions(moderate_members=True)
@commands.bot_has_permissions(manage_messages= True)
async def set_xp(ctx, member: discord.Member, amount:int):
    global server_stats
    guild = member.guild
    server_stats.stats[guild.id]['user_stats'].stats[member.id]['xp'] = amount
    server_stats.save_stats()
    await ctx.send(f'successfully set {member.name}\'s xp to {amount}.')


@client.command(help='This cmd gives the given role to the given user.',brief='Gives the user the given role.')
@commands.has_permissions(manage_roles= True)
@commands.bot_has_permissions(manage_roles = True)
async def give_role(ctx, member: discord.Member, role: discord.Role):
    await give_role_logic(member, role, ctx)

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

@client.command(help='This cmd removes the given role to the given user.',brief='Removes the role from the given user.')
@commands.has_permissions(manage_roles= True)
@commands.bot_has_permissions(manage_roles = True)
async def remove_role(ctx, member: discord.Member, role: discord.Role):
    message = await remove_role_logic(member, role)
    await ctx.send(message)

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
@client.command(help='Lists all server roles.')
async def list_roles(ctx):
    roles = ctx.guild.roles
    roles_list = []
    for role in list(roles):
        if role.name != '@everyone':
            roles_list.append(role.name)
    await ctx.send(f'Avalible roles:\n'+'\n'.join(f'- {role}' for role in roles_list))


@client.command(help='This cmd adds the given role to all users in the server if they don\'t have it already.',brief='Gives everyone the given role.')
@commands.has_permissions(manage_roles= True)
@commands.bot_has_permissions(manage_roles = True)

async def give_all_roles(ctx, role: discord.Role):
    for member in ctx.guild.members:
        try:
            await member.add_roles(role)
            await ctx.send(f'Successfully gave {role.name} to {member.display_name}')
        except discord.Forbidden:
            await ctx.send(f'I do not have permission to add {role.name} to {member.display_name}.')
        except Exception as e:
            print(e)
            await ctx.send('An unexpected Error has occoured please contact the Bot owner.')
    
@client.command(help='This cmd removes the given role from all the users in the server if they have it.',brief='Removes the given role from everyone.')
@commands.has_permissions(manage_roles= True)
@commands.bot_has_permissions(manage_roles = True)

async def remove_all_roles(ctx, role: discord.Role):
    for member in ctx.guild.members:
        try:
            await member.remove_roles(role)
            await ctx.send(f'Successfully removed {role.name} from {member.display_name}.')
        except discord.Forbidden:
            await ctx.send(f'I do not have permission to remove {role.name} from {member.display_name}.')
        except Exception as e:
            print(e)
            await ctx.send('An unexpected Error has occoured please contact the Bot owner.')

@client.event
async def on_member_join(member: discord.Member):
    if client.user.id == member.id:
        return
    guild = member.guild
    if server_stats.stats[guild.id].get('set_up') is not None and server_stats.stats[guild.id].get('set_up') is False:
        return
    channel =  discord.utils.get(guild.channels, name= 'welcome')#welcome channel
    await channel.send(f'Welcome {member.display_name} to the {guild.name} server!')
    role = discord.utils.get(guild.roles, name = 'beginner') 
    await give_role_logic(member, role)
    server_stats.is_dict_complete()

async def remove_suggestion_logic(suggestion,guild):
    server_stats.stats[guild.id]['to_watch'].pop(suggestion)
    to_watch = server_stats.stats[guild.id]['to_watch']
    server_stats.save_stats()
    if not to_watch:#TODO check if if not to_watch is the same as if len(to_watch) == 0
        all_events = await guild.fetch_scheduled_events()
        for event in all_events:
            if event.name.lower() == event_title.lower():
                await event.delete()
                return True
    return False

@client.event
async def on_member_remove(member:discord.Member):
    if member.id == client.user.id:
        return
    guild = member.guild
    if server_stats.stats[guild.id].get('set_up') is not None and server_stats.stats[guild.id].get('set_up') is False:
        return
    channel = discord.utils.get(guild.channels, name = 'goodbye')
    await channel.send(f'Bye {member.name} we are sorry to see you go.')
    is_hosting, suggestion = is_member_hosting(member)
    if is_hosting:
        is_removed = await remove_suggestion_logic(suggestion,member.guild)
        if is_removed is False:
            print('An error occoured when trying to remove a member that left from the suggestion list. Function: on_member_remove.')


@client.command(help='This cmd times out the given member for the given time. You can also provide a optional reason.',brief='Times out the given user.')
@commands.has_permissions(moderate_members=True)
@commands.bot_has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, duration: str, reason: str = 'No valid reason provided'):
    await timeout_logic(ctx, member, duration ,reason = reason) 
    
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

async def add_strike_code(member: discord.Member, amount:int = '1', ctx = None):
    if type(amount) != int:
        amount = int(amount)
    server_stats.stats[member.guild.id]['strikes'][member.id] += amount
    server_stats.save_stats()
    await strikes_punishments(member, ctx)

@client.command(help='This cmd adds the amount of strikes given to the given user.',brief='Adds a strike to the given user.')
@commands.has_permissions(moderate_members=True)
@commands.bot_has_permissions(moderate_members= True)

async def add_strikes(ctx, member: discord.Member, amount = '1' ):
    try:
        if amount == 1:
            await ctx.send(f'Added {amount} strike to {member.name}.')
        else:
            await ctx.send(f'Added {amount} strikes to {member.name}.')
        await add_strike_code(member, amount)
    except discord.Forbidden:
        await ctx.send(f'I do not have permission to do that.')
    except Exception as e:
        print(e)
        await ctx.send('An unexpected Error has occoured please contact the Bot owner.')


@client.command(help='This cmd lists all the strikes of every user in the server if no user is given. If a user is given it will just show the strikes of that user.',brief='Lists the strikes of everyone.')
@commands.has_permissions(manage_roles= True)
@commands.bot_has_permissions(manage_roles= True)
async def strikes_list(ctx, member:discord.Member=None):
    answer = ''
    strikes = server_stats.strikes(ctx.guild)
    for key, value in strikes.items():
        if member and key != member.id:
            continue
        key = client.get_user(key)
        key = key.display_name
        if key is None:
            continue
        if value == 1:
            answer += (f'User: {key} has {value} strike.\n')
        else:
            answer += (f'User: {key} has {value} strikes.\n')
    await ctx.send(answer)

@client.command(help='This cmd shows you how many strikes you currently have.',brief='Shows how many strikes you have.')
async def my_strikes(ctx):
    member = ctx.author
    strikes = server_stats.strikes(ctx.guild)
    if strikes[member.id] == 1:
        await ctx.send(f'You have {strikes[member.id]} strike.')
    else:
        await ctx.send(f'You have {strikes[member.id]} strikes.')


@client.command(help='This cmd sets the amount of strikes a user has to the given amount.',brief='Sets the users_strikes to the given amount.')
@commands.has_permissions(moderate_members=True)
@commands.bot_has_permissions(moderate_members= True)
async def set_strikes(ctx, member: discord.Member, amount= '1'):
    await set_strikes_code(ctx, member, amount)

async def set_strikes_code(ctx, member: discord.Member, amount ='1'):
    if type(amount) != int:
        amount = int(amount)
    server_stats.stats[member.guild.id]['strikes'][member.id] = amount
    await strikes_punishments(member)
    await ctx.send(f'The strikes of {member.display_name} were successfully set to {amount}')


async def strikes_punishments(member: discord.Member, ctx  = None):
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
        await promote(old_role, spammer, member)
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
        await promote(old_role, spammer, member)
        server_stats.save_stats
        await timeout_logic(member, '1d', reason=f'The user has {strikes[member.id]} strikes.')

    elif strikes[member.id] > 40:
        await member.kick(reason='You were kicked because you currently had 40 strikes on the server.\nPlease contact the server admins if you think this treatment is unfair.')
    
    server_stats.save_stats()

@tasks.loop(seconds= 10)
async def is_waiting_expired():
    members_to_remove = []  
    for member in waiting_list:
        user_stats
        guild = client.get_guild(waiting_list[member]['guild'])
        member_obj = guild.get_member(member)
        if waiting_list[member]['time'] <= datetime.now(timezone.utc):
            spammer = discord.utils.get(guild.roles, name = 'spammer')
            new_role = discord.utils.get(guild.roles, name=  server_stats.user_stats(guild).stats[member]['role_before_spam'])
            server_stats.user_stats(guild).stats[member].pop('role_before_spam')
            server_stats.save_stats
            await promote(spammer,new_role, member_obj)
            members_to_remove.append(member)

    for member in members_to_remove:
        waiting_list.pop(member)

async def delete_message(message:discord.Message | list[discord.Message], time = 0):
    """
    Docstring for delete_message
    
    :param message: discord.Message or list containing discord.Message
    :param time: Amount of seconds waiting before deletion.
    """
    if time != 0:
        await asyncio.sleep(time)
    if isinstance(message, discord.Message):
        await message.delete()
        return
    if isinstance(message, list):
        for msg in message:
            if isinstance(msg, discord.Message):
                await msg.delete()


def del_old_logs():
    keys_to_pop = {}
    for user, messages in logs_temp.items():
        for timestamp in messages.keys():
            if timestamp == 'guild_id':
                continue
            five_min_before = datetime.now(timezone.utc) - timedelta(minutes=3)
            if timestamp < five_min_before:
                if user not in keys_to_pop.keys():
                    keys_to_pop[user] = [timestamp]
                else:
                    keys_to_pop[user].append(timestamp)
    for user, time_obj in keys_to_pop.items():
        for timestamp in time_obj:
            logs_temp[user].pop(timestamp)

async def check_spam_without_punishment():
    global is_user_spamming
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

async def check_spam():
    await check_spam_without_punishment()
    await spam_punishment()
    
async def spam_punishment():
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
            await add_strike_code(user_obj, 1)
            logs_temp[user] = {}
            is_user_spamming[user] = False
            break

@client.command(help='This cmd gives the logs for the given user. You can also give a certain amount of msgs that it will show.',brief='Returns the logs.')
@commands.has_permissions(manage_messages=True)
async def logs(ctx,mbr:discord.Member = '', amount:int = 100, sorting:bool = True): # TODO Make it so that it works and only gives the logs of a certain person or of a certain amount not the full logs
    counter = 0
    readable_logs = ''
    sorted_logs = sort_by_newest(full_logs)
    user_msgs = {}
    while counter <= amount:
        for time_obj, user_msgs_at_time in sorted_logs.items():
            if counter >= amount:
                break
            for user, msg_list in user_msgs_at_time.items():
                if len(msg_list) == 0:
                    continue
            user_n =  ctx.guild.get_member(user)
            if user_n == None:
                user_n =  await client.fetch_user(user)
            if user_n.id != mbr.id:
                continue    
            if sorting:
                for msg in msg_list:
                    if user not in user_msgs.keys():
                        user_msgs[user] = f'\nUser {user_n.name} sent:'
                    user_msgs[user] += f'\nmessage: {msg} at {time_obj.strftime("%D %H:%M")}'
            else:
                for msg in msg_list:
                    append_msg = (f'User {user_n.name} sent: ')
                    append_msg += f'\nmessage: {msg} at {time_obj.strftime("%H:%M")}'
                readable_logs += f'{append_msg}\n'
            counter +=1
        break
    if sorting:
        for user, log in user_msgs.items():
            readable_logs += f'\n{log}'
    await ctx.send(file =discord.File(StringIO(readable_logs), filename = 'logs.txt'))


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

@client.command(help='This cmd gives you the code for the given code name.',brief='Gives code for the given name.')
async def gen(ctx:commands.Context, user_input: str='help'): # TODO Make it so that you can do smth like gen(first command(if this command endswith : + 4 spaces , ; (go back four spaces,(, adds a newline))) ) also mayber add a gen cmd for another language
    all_descriptions = 'Avalible code is:'
    for description in code_dict.keys():
        if description == 'help':
            continue
        all_descriptions += '\n' + description
    code_dict['help'] = all_descriptions
    with open('code.json', 'w') as f:
        json.dump(code_dict, f)
    if user_input in code_dict.keys():
        if len(code_dict[user_input]) < 2000:
            await ctx.send(code_dict[user_input])
        else:
            ram = BytesIO(code_dict[user_input].encode('UTF-8'))
            ram.name = f'{user_input}.py'#makes it so that discord treats it like a real file
            await ctx.send(file = discord.File(ram))
    else:
        if any(role.name == 'dev' for role in ctx.author.roles):
            await ctx.send('Would you like to add this code? (y/n)')
            response = await response_waiting(ctx)
            if response == None:
                return
            if response.content.lower() == 'y':
                await ctx.send('What is the code?')
                waiting_confirmations.append(ctx.author.id)
                try:
                    code = await response_waiting(ctx, time = 180)
                    if response is None:
                        None
                    if code.attachments and len(code.content.strip()) == 0:
                        if len(code.attachments) == 1:
                            if any(code.attachments[0].filename.lower().endswith(fileend) for fileend in allowed_file_endings):
                                content_in_bytes = await code.attachments[0].read()
                                try:
                                   code  = content_in_bytes.decode('UTF-8')
                                except UnicodeDecodeError:
                                    print(f'Error while trying to decode file')
                    if isinstance(code, discord.Message):
                        code = code.content
                    change_confirmations.append(ctx.author.id)
                except TimeoutError:
                    await ctx.send('You took too long to respond.')
                    return
                if len(code) > 2000:
                    final_code = format_to_code(code, 'python')
                else:
                    final_code = format_to_code(code, 'python')
                code_dict[user_input] = final_code
                with open(r'data/code.json', 'w') as f:
                    json.dump(code_dict, f)
            elif response.content.lower() == 'n':
                return
        else:
            await ctx.send(f'This gen command does not exist.\nIf you want a list of all possible !gen commands enter !gen help.')
        
def format_to_code(code: str, language:str):
    if len(code) >= 2000:
        final_code = code
    else:
        final_code = f'```{language}\n'
        final_code += code
        final_code += '```'
    return final_code

@client.command(help='This cmd adds the gen code to the gen options.',brief='Deletes the given gen cmd.')
@commands.has_role('dev')
async def gen_edit(ctx, user_input: str):
    if user_input in code_dict.keys():
        await ctx.send('What would you like to change the code to?(Enter exit to exit.)')
        code = await response_waiting(ctx)
        if code == None:
            return
        if code.content == 'exit':
            return
        final_code = format_to_code(code.content)
        code_dict[user_input] = final_code
        with open('code.json', 'w') as f:
                json.dump(code_dict, f)
    else:
        await ctx.send('This code description does not exist in the code dict.')
         
@client.command(help='This cmd deletes the given gen cmd from the gen dict.',brief='Deletes the given gen cmd.')
@commands.has_role('owner') # TODO make it so that also higher roles than dev can acces this command also automaticly including all rules with admin acces and the owner
async def gen_del(ctx, user_input: str):
    if user_input in code_dict.keys():
        await ctx.send('Are you sure that you want to delete the code for this command? (y/n)')
        response = await response_waiting(ctx)
        if response == None:
            return
        if response.content == 'y':
            code_dict.pop(user_input)
        else:
            return
        
    else:
        await ctx.send('This code description does not exist in the code dict.')
    
@client.command(help='This cmd clears all messages in the given channel(channelID).',brief='Clears the given channel.')
@commands.has_permissions(manage_messages = True)
@commands.bot_has_permissions(manage_messages=True)
async def clear_channel (ctx:commands.Context, channel_id: int = None):
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
    response = response_waiting(ctx)
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

@client.command(help='This cmd adds the given channel(channelID) from the channels where the bot can directly talk.',brief='Adds channel to the allowed channels.')
@commands.has_permissions(manage_channels=True)
async def add_allowed_channels(ctx, channel_id: int):
    allowed_channels = server_stats.stats[ctx.guild.id]['allowed_channels']
    for channel in ctx.guild.channels:
        if channel_id == channel.id:
            if channel_id in allowed_channels.values():
                await ctx.send(f'Channel is already an allowed channel.')
                return
            allowed_channels[channel.name] = channel_id
            server_stats.save_stats()
            await ctx.send(f'Successfully added channel {channel.name} to the allowed channels.')
            return
    await ctx.send('Channel was not found. Please make sure that the entered channeld ID is an existing channel.')

@client.command(help='This cmd removes the given channel(channelID) from the channels where the bot can directly talk.',brief='Removes the channel from the bot channels.')
@commands.has_permissions(manage_channels=True)
async def remove_allowed_channels(ctx, channel_id: int):
    allowed_channels = server_stats.stats[ctx.guild.id]['allowed_channels']
    for name, id in allowed_channels.items():
        if channel_id == id:
            allowed_channels.pop(name)
            server_stats.save_stats()
            await ctx.send(f'Successfully removed channel {name} from the allowed channels.')
            return 
    await ctx.send('Channel id is not yet registred to the allowed channels.')

@client.command(help='This cmd sends a stats card of the given user.',brief='Shows stats of the given user.')   
async def stats(ctx, user: discord.Member = None):
    if user == None:
        member = ctx.author
    else:
        member = user
    guild = member.guild
    user_stats = server_stats.user_stats(guild)
    try:
        avatar_in_bytes = await member.display_avatar.read() if member.avatar else await member.default_avatar.read()
        rounded_img, mask = PIL_round_img_obj(avatar_in_bytes, (395,395))
        with Image.open(r'images/base.png','r') as img2:
            white_image = img2.copy()#.copy is absolutly needed here because it would else just reference the object that doesnt exist anymore because with closes it after
        white_image.paste(rounded_img, (7,85), mask=mask)
        width, height = white_image.size
        server = ctx.guild
        index = server.id % 5#this is the server icon discord chooses out of the 5 using the same line
        server_avatar_url = server.icon.url if server.icon else f'https://cdn.discordapp.com/embed/avatars/{index}.png'

        async with aiohttp.ClientSession() as session: #starts a new http session, use it with paragraphs to use the function not the class
            async with session.get(server_avatar_url) as site: #opens the icon or default server icon site
                server_avatar_in_bytes = await site.read() 

        img2,mask = PIL_round_img_obj(server_avatar_in_bytes,(90,90))
        white_image.paste(img2,(535,125),mask=mask)            
        current_xp = user_stats.stats[member.id]['xp']
        try:
            xp_needed = server_stats.stats[guild.id]['roles_requirements'][next(k for k,v in server_stats.stats[guild.id]['server_roles'].items() if v == user_stats.stats[member.id]['next_rank'])]['xp']
        except (KeyError,StopIteration):
            xp_needed = ''
        txt_to_dp = f'XP: {current_xp}/{xp_needed}'
        if type(xp_needed) != int:
            if current_xp != 0:
                xp_needed = current_xp
            else:
                xp_needed = 1
                current_xp = 1
            txt_to_dp = 'Max XP'
        draw = ImageDraw.Draw(white_image)
        progress= current_xp/xp_needed # Total_widht * progress = current xp / needed xp
        full_width = 500
        width_bar = int(full_width * progress)
        percent = f'{int(progress * 100)}%'
        height_bar = 25
        bar = Image.new('RGBA', (width_bar, height_bar), (9, 129, 209))
        for x in range(bar.width):
            if txt_to_dp == 'Max XP':
                start_color = (187,155,73)
                end_color = (255, 255, 200)
            else:
                start_color = (0, 200, 255)
                end_color = (120, 255, 255)
            percentage = x / (bar.width-1)
            bar_pixels = bar.load()
            r = int(start_color[0] + (end_color[0] - start_color[0]) * percentage)# it works because when it gets brighter the way is - so every time it removes more
            g = int(start_color[1] + (end_color[1] - start_color[1]) * percentage)# it takes the base and adds the way multiplied by how far to it
            b = int(start_color[2] + (end_color[2] - start_color[2]) * percentage)
            for y in range(bar.height):
                bar_pixels[x,y] = (r,g,b)

        mask = Image.new('L', (width_bar, height_bar), 0)
        x= int(width/2)
        y = int(height/2.5)
        cords = x,y
        bar_cords = x+width_bar,y-2.5
        radius = height_bar//2 
        draw = ImageDraw.Draw(mask)#makes it possible to draw on the image mask
        if width_bar <= radius*2:
            draw.pieslice((0,0,height_bar, height_bar), 90, 270, fill= 255)
            try:
                draw.rectangle((radius,0, width_bar, height_bar), fill=255)
            except ValueError:
                pass
        else:
            draw.rounded_rectangle((0,0,width_bar,height_bar), radius=radius,fill=255)
        rounded_bar = Image.new('RGBA', (width_bar, height_bar), (0,0,0,0))
        rounded_bar.paste(bar, (0,0), mask=mask)
        bar_cords = bar_cords[0] + 10, bar_cords[1]
        white_image.paste(rounded_bar,(cords), mask=mask)
        draw = ImageDraw.Draw(white_image)
        draw.rounded_rectangle((x, y, x+full_width, y+25), radius=radius,outline=0, width=3)
        extra = 40
        font_size = 28
        cords = (x, 170)
        if txt_to_dp == 'Max XP':
            draw = PIL_text_obj(draw, cords, member.display_name,font_size= 80, text_color=(187,155,73))
        else:
            draw = PIL_text_obj(draw, cords, member.display_name,font_size= 80, text_color=(255,255,255))
        draw = PIL_text_obj(draw,bar_cords,percent,font_size=font_size-2)
        if user_stats.stats[member.id]['xp_for_next_rank'] == 'Owner is the highest rank':
            response = 'There is no way to rank up with xp after at this rank.'
        elif type(user_stats.stats[member.id]['xp_for_next_rank']) == str:
            if user_stats.stats[member.id]['xp_for_next_rank'] == 'There is no greater rank beyond Owner':
                if user_stats.stats[member.id]['rank'] == 'KlasseBot':
                    response = f'There is no higher rank for me.'
                else:
                    response = f'There is no higher rank.'
            else:
                response = f'It is not possible to progress with XP.\nIt is only possible to rank up\n{user_stats.stats[member.id]["xp_for_next_rank"]}.'
        else:
            response = f'You need {user_stats.stats[member.id]["xp_for_next_rank"]} xp to rank up to {user_stats.stats[member.id]["next_rank"]}\n(Every message gives 5xp).\n'
        counter = 0
        for split in user_stats.stats[member.id]['join_date'].split('.'):
            if counter == 0:
                day = str(split)
            elif counter == 1:
                month = months[split]
            elif counter == 2:
                year = str(split)
            counter += 1
        date = f'{day} {month} {year}'
        cords = (x, y-50)
        draw = PIL_text_obj(draw, cords, txt_to_dp,font_size= font_size+10)
        cords = cords[0], cords[1] + extra + 60
        draw = PIL_text_obj(draw,cords, f'Messages        {user_stats.stats[member.id]["message_count"]}',font_size= font_size)
        cords = cords[0], cords[1] + extra
        draw = PIL_text_obj(draw,cords, f'Rank                {user_stats.stats[member.id]["rank"]}',font_size= font_size)
        rank_img = user_stats.stats[member.id]["img"]
        rank_img = Path(rank_img) # handels \ and /
        rank_img = rank_img.as_posix()#turns all \ to /
        if not rank_img.startswith('images/'):
            user_stats.stats[member.id]["img"] = f'images/{rank_img}'
            rank_img = f'images/{rank_img}'
        server_stats.save_stats
        cords = cords[0], cords[1] + extra
        draw = PIL_text_obj(draw,cords, f'Next rank         {user_stats.stats[member.id]["next_rank"]}',font_size= font_size)
        cords = cords[0], cords[1] + extra
        draw = PIL_text_obj(draw,cords, f'Joined              {date}',font_size= font_size)
        cords = cords[0], cords[1] + extra
        draw = PIL_text_obj(draw,cords, f'Total XP           {user_stats.stats[member.id]["xp"]}',font_size= font_size)
        cords = cords[0], cords[1] + extra
        draw = PIL_text_obj(draw,cords, f'{response}',font_size= font_size)
        
        if rank_img != '':
            try:
                with Image.open(rank_img, 'r') as rank_img2:
                    rank_img = rank_img2.copy()
            except Exception as e:
                print(e)
                rank_img = None
        else:
            rank_img = None
        if rank_img != None:
            extra = 50
            rank_img = rank_img.resize((rank_img.width-extra, rank_img.height-extra))
            if rank_img.size == (300-extra,300-extra):
                rank_img = rank_img.resize((200,200))
            white_image.paste(rank_img,(85,550), rank_img)#rank_img works as a mask bcs pillow automaticly only uses the alpha channel of the image that it already has
        white_image.resize((500,333), Image.LANCZOS)
        ram = BytesIO()#creates new ram
        white_image.save(ram, format='PNG')#saves it in the ram
        ram.seek(0)
        file = discord.File(fp=ram, filename='stats_card.png')
        await ctx.reply(file=file)
    except discord.Forbidden:
        await ctx.reply('I do not have permissions to send files in this channel.\nIt is probably deactivated for the bot or for everyone to attach files.')
    except Exception as e:
        print(e)
        await ctx.reply('An error occoured while trying to execute this command!')

def PIL_text_obj(draw: ImageDraw,cords, txt_to_dp = 'hello world',font_size = 20,bold_width = 0.5, text_color = (0,0,0),bold_fill = None, font = 'default'):
        if bold_fill == None:
            bold_fill = text_color
        try:
            font = ImageFont.truetype(font, font_size)
        except OSError:
            try:
                font = ImageFont.truetype("arial.ttf", font_size)  # Works on Windows
            except OSError: # Fallback for Linux/Mac if Arial is not available
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        draw.text(cords,txt_to_dp,fill= text_color, font=font, stroke_width=bold_width, stroke_fill= bold_fill)
        return draw
def PIL_round_img_obj(img, size = None):
    with Image.open(BytesIO(img)).convert('RGBA') as img:
        jpeg_ram = BytesIO()
        img.save(jpeg_ram,'PNG')
        jpeg_ram.seek(0) #read cursor position
        if size != None:
            img = img.resize(size, Image.LANCZOS)
        width, height = img.size
        mask = Image.new('L', (width, height), 0) # L is for grayscale black and white 0 is the color black so everything that is black here covers everyting white shows
        draw = ImageDraw.Draw(mask)#the object you can draw on
        draw.ellipse((0,0, width, height), fill= 255)#it draws an image from (0,0) (x) to (50,50) (y) 
        #puts the mask over the image so only the part inside the circle is visible
        rounded_img = Image.new('RGBA', (width, height), (0,0,0,0))#creates a new Image object with the image size of the full mask and of the image to round
        rounded_img.paste(img, (0,0), mask=mask)#mask is not only just used as out it over the image but it is used as only show whats visible inside and cut the rest away its 0,0 because 0,0 is in the top left 
        return rounded_img, mask   


@client.command(help='This cmd adds the badge coresponding to the given badge name to the given user.',brief='Adds a badge to the given user.')
@commands.has_permissions(manage_messages=True)
async def add_badge(ctx, member: discord.Member,badge_name:str):
    guild = ctx.guild
    if badge_name in badges_imgs.keys():
        server_stats.user_stats(guild).stats[member.id]['badges'].append(badges_imgs.get(badge_name))

def is_member_hosting(member:discord.Member):
    for watch_name, watch_data in server_stats.stats[member.guild.id]['to_watch'].items():
        if watch_data.get('id') == member.id:
            return True, watch_name
    return False, None

@client.command(help='This cmd adds your suggestion to the events suggestions.',brief='Adds your suggestion.')
async def suggest(ctx: commands.Context, watch_name:str, takes_time:int = 2):
    guild = ctx.guild
    if guild.id not in server_stats.stats.keys():
        return
    if server_stats.stats[guild.id]['suggestions_closed']:
        await ctx.send('Suggestion are closed until the upcoming event is over.')
        return
    global next_sunday
    to_watch = server_stats.stats[guild.id]['to_watch']
    watch_name = watch_name.lower()
    is_slur,_,_ = await check_slurs_without_punishment(ctx,watch_name)
    if is_slur:
        return
    is_hosting,_ = is_member_hosting(ctx.author)
    if is_hosting:
        await ctx.send('You are already hosting an event.\nYou can\'t host multiple events at the same time.')
        return
    if watch_name in to_watch.keys():
        member = ctx.guild.get_member(to_watch.get(watch_name).get('id'))
        if member is None:
            display_name = await client.fetch_user(to_watch.get(watch_name).get('id'))
        display_name = member.display_name
        watch_time = to_watch.get(watch_name).get('watch_date')
        await ctx.send(f'{watch_name} is already being hosted by {display_name} at {watch_time.strftime('%d.%m.%Y')}.\nYou can\'t suggest to host the same thing.')
        return
    await ctx.send('Do you want to host it this weekend (You will have to set up what you proposed next sunday) (y/n)?')
    response = await response_waiting(ctx)
    if response is None:
                return
    if response.content.lower() in ['y','yes']:
        next_sunday = next_sunday.replace(tzinfo=timezone.utc)#next sunday replace timezone information with utc timezone
        channel = discord.utils.get(guild.voice_channels, name= 'General')
        server_stats.stats[guild.id]['to_watch'][watch_name] = {'watch_date': next_sunday,
                                'id': ctx.author.id}
        await ctx.reply(f'You are now applied to host **{watch_name}** next sunday.')
        server_stats.save_stats()
        all_events = await guild.fetch_scheduled_events()
        for event in all_events:
            if event.name.lower() == event_title.lower():
                return
        await guild.create_scheduled_event(name=event_title,start_time = next_sunday, 
                                           end_time = next_sunday+timedelta(takes_time),
                                           entity_type=discord.EntityType.voice,description = event_description,
                                           privacy_level=discord.PrivacyLevel.guild_only,
                                           channel = channel)#guild only makes it so that only server members can participate in this event. Else you could see the server in discovery and before accepting rules etc just participate in the event.
    elif response.content.lower() in ['n', 'no']:
        await ctx.reply('Sorry but you can\'t propose something and then not host it. If you want you can try to convince someone else to do it for you.')

@client.command(help='This events removes your suggestion from the event suggestions.',brief='Removes your suggestion.')
async def remove_suggestion(ctx:commands.Context):
    if server_stats.stats[ctx.guild.id]['suggestions_closed']:
        await ctx.send('Suggestions removals are closed until the upcoming event is over.')
        return
    guild = ctx.guild
    is_hosting, watch_name = is_member_hosting(ctx.author)
    if not is_hosting:
        await ctx.reply('You are currently not hosting anything')
        return
    await ctx.send('Are you sure that you want to remove your suggestion?(y/n)')
    response = await response_waiting(ctx)
    if response == None:
        return
    if response.content.lower() in ['y','yes']:
        is_removed = await remove_suggestion_logic(watch_name,guild)
        if is_removed:
            await ctx.send('You were successfully removed from the watch suggestions.')
        


async def event_prep(guild:discord.Guild):
    to_watch = server_stats.stats[guild.id]['to_watch']
    if not to_watch:
        return #an event should never be created then so we dont have to try and delete it.
    winner =  random.choice(list(to_watch.keys()))
    server_stats.stats[guild.id]['winner_watch'] = winner
    winner_data = to_watch.get(winner)
    all_events = await guild.fetch_scheduled_events()
    if all(event.name.lower() != event_title.lower() for event in all_events):
        return
    server_stats.stats[guild.id]['suggestions_closed'] = True
    server_stats.stats[guild.id]['winner_data'][winner] = winner_data
    event_role = discord.utils.get(guild.roles, name= 'events')
    channel = discord.utils.get(guild.channels, name= 'events')
    member = guild.get_member(winner_data.get('id'))
    if member is None:
        return
    if not event_role:
        print('Channel general chat was not found.')
        return
    await channel.send(f'{event_role.mention} The randomly selected suggestion was **{winner}** hosted by <@{member.id}>.\nThe bot doesn\'t take any more invites or suggestion removals until the end of the event.' if event_role else f'The randomly selected suggestion was **{winner}** hosted by <@{member.id}>.\nThe bot doesn\'t take any more invites or suggestion removals until the end of the event.')

async def wait_until_event():
    time_until_next_event = (next_sunday - datetime.now(timezone.utc)- timedelta(hours=1)).total_seconds() # 1 hour before event
    if time_until_next_event <= 0:
        print('Event already in the past. Error happened.')
        return
    await asyncio.sleep(time_until_next_event)
    for guild_id in server_stats.stats.keys():
        if not server_stats.stats[guild_id]['to_watch']:
            return
        if client.get_guild(guild_id) is None:
            return
        await event_prep(client.get_guild(guild_id))
    await wait_until_event()

@client.event
async def on_scheduled_event_update(event_before:discord.ScheduledEvent, event_after:discord.ScheduledEvent):
    guild = event_after.guild
    
    if server_stats.stats[guild.id].get('set_up') is not None and server_stats.stats[guild.id].get('set_up') is False:
        return
    if event_before.name.lower() != event_title.lower():
        return
    if event_after.status.name == 'completed':
        server_stats.stats[event_after.guild.id]['to_watch'] = {}
        server_stats.save_stats()
        server_stats.stats[event_after.guild.id]['suggestions_closed'] = False
    elif event_after.status.name == 'active':
        server_stats.stats[event_after.guild.id]['winner_user'] = 1
        server_stats.stats[event_after.guild.id]['winner_watch'] = 1

@client.command(help='This cmd gives you a bit of xp every 24 hours.',brief='Gives xp every 24 hours.')
async def daily_xp(ctx):
    user_stats = server_stats.user_stats(ctx.guild)
    if user_stats.stats[ctx.author.id].get('time_redeemed') is not None:
        if (user_stats.stats[ctx.author.id]['time_redeemed']+ timedelta(days=1)) >= datetime.now(timezone.utc):# if the diff to 1970 from the date redeemed + 1 day is greater than now then it means that that time + 24 hours are farther from 1970 meaning farther in the future
            diff = (user_stats.stats[ctx.author.id]['time_redeemed']+ timedelta(days=1))- datetime.now(timezone.utc)
            hours, rest = divmod(diff.total_seconds(),timedelta(hours=1).total_seconds())# just does a modulo and returns the rest
            better_diff = f'{int(hours)} hours {int(rest//timedelta(minutes=1).total_seconds())} minutes'
            await ctx.send(f'You cannot redeem your daily xp multiple times in 24 hours.\nYou still have to wait {better_diff}.')
            return
    amount_of_xp = 25
    user_stats.add_xp(ctx.author, amount_of_xp)
    user_stats.stats[ctx.author.id]['time_redeemed']  = datetime.now(timezone.utc)
    server_stats.save_stats
    await ctx.reply(f'You got {amount_of_xp}xp added as your daily xp.')

@client.command(help='This cmd adds xp to the given user.',brief='Adds the given xp the given user.')
@commands.has_permissions(manage_messages=True)
async def add_xp(ctx,member:discord.Member,amount:int = 5):
    server_stats.user_stats(member.guild).add_xp(member,amount)
    await ctx.reply(f'Successfully added {amount}xp to {member.display_name}.')

@client.event
async def on_guild_join(guild):
    server_stats.is_dict_complete()
    server_stats.stats[guild.id]['set_up'] = False
@client.event
async def on_guild_remove(guild):
    server_stats.stats[guild.id]['set_up'] = False
    #TODO Add expiration date for the data

@client.command(help = 'This cmd sets up the bot to be used in a server.',brief='Sets up the bot in the server.')
@commands.has_permissions(manage_guild=True)
async def setup(ctx:commands.Context):
    guild = ctx.guild
    admin_channel = discord.utils.get(guild.channels,name=admin_channel_name)
    bot_channel = discord.utils.get(guild.channels,name=bot_channel_name)
    event_channel = discord.utils.get(guild.channels,name=event_channel_name)
    welcome_channel = discord.utils.get(guild.channels, name = welcome_channel_name)
    goodbye_channel = discord.utils.get(guild.channels, name = goodbye_channel_name)
    nescessary_channels = {admin_channel:admin_channel_name,bot_channel:bot_channel_name,event_channel:event_channel_name,welcome_channel:welcome_channel_name,goodbye_channel:goodbye_channel_name}
    server_stats.is_dict_complete()
    if any(channel is None for channel in nescessary_channels.keys()):
        await ctx.send('Would you like to proceed with creating channels (y/n)?\n(if a needed channel doesn\'t already exist it will ask you if it is allowed to specificly create that channel.)')
        response = await response_waiting(ctx,time=120)
        if response is None:
                return
        if response.content.lower() not in ['y', 'yes']:
            await ctx.send('successfully stopped the setup process.')
            return
    for channel, name in nescessary_channels.items():
        if channel is None:
            await ctx.send(f'A text channel called {name} is needed for the bot to work.\nBut the channel doesn\'t exist in this server. Would you like the bot to create that channel(y/n)?')
            response = await response_waiting(ctx, time= 120)
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
            response = await response_waiting(ctx)
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
    response = await response_waiting_text(ctx,time=600)
    if response not in ['ok','y','yes']:
        return
    
    for num, role_name in roles_name.items():
        role = discord.utils.get(guild.roles, name= role_name)
        if role is None:
            await ctx.send(f'There is no role named {role_name}.\nWould you like me to create that role?')
            response = await response_waiting(ctx,120)
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
                server_stats.stats[guild.id]['roles_imgs'][num] = {9: r'images/owner.png', 8: '','klassebot': r'images/bot.png', 7: r"images/admin.png",6: '',5: r"images/dev.png", 4: r"images/trial_dev.png", 3: r'images/lite_member.png', 2: r"images/member.png", 1: r'images/beginner.png', 'spammer':''}.get(num)
                server_stats.stats[guild.id]['roles_requirements'][num] = {1: {"xp": 0, "strikes": 99}, 2: {"xp": 500, "strikes": 99}, 3: {"xp": 2500, "strikes": 20}, 4: {"xp": 5000, "strikes": 10}, 5: {"xp": 12500, "strikes": 5},6:{'strikes':60},7:{'strikes':80},8:{'strikes':10000},9:{'strikes':9999999999999999999999999}}.get(num)#TODO Make the strikes limit on 
                if num == 9:
                    await ctx.send('As this is the owner role it is normally above the bot, so you will have to move it above the bots rank. ')
                    break
                await guild.edit_role_positions({role:num})
    server_stats.stats[guild.id]['server_roles'] = roles_name#TODO DO NOT CREATE OWNER ROLE JUST SAVE IT, CREATE PERMISSION FOR THE OTHER 3 or so roles. 
    server_stats.stats[guild.id]['set_up'] = True
    server_stats.stats[guild.id]['suggestions_closed'] = False
    server_stats.save_stats 
             
    server_stats.user_stats(guild).complete(guild)
    #TODO come up with ideas on how to personalize this bot the most possible

@setup.error
async def setup_error(ctx:commands.Context,error:commands.CommandError):
    if isinstance(error, discord.ext.commands.errors.CommandInvokeError):
        await ctx.send('I do not have permission to create new roles that are a higher level than me.\nPlease make sure that the bot\'s role is placed above every role that the bot should be managing.\nThe most optimal position would be the one below the owner role.')
        error.handled = True
        return
    else:
        raise error

def hex_color_to_rgb(hex_str:str):
    nums =hex_str.strip('#')#if i would convert it here it would loose its structure bcs dd could turn into more than two positions but in the str it is always 2 positions
    r = int(nums[0:2],16)#first one so pos 0 included second isn't so from 0 to and without 2 so from 0 to 1
    g = int(nums[2:4], 16)
    b = int(nums[4:6],16)
    return r,g,b

def full_rgb(r:int,g:int,b:int):
    if not all(isinstance(char,int) for char in (r,g,b)):
        return None
    rgb = str(r)
    rgb += str(g)
    rgb += str(b)
    return int(rgb)

def other_rbg(r:int,g:int,b:int):
    if not all(isinstance(char,int) for char in (r,g,b)):
        return None
    #rgb is 24 bit each letter occupies max 8 bit and so to combine them we do like basecly a += so like we say r move 16 to the left then move g 8 to the left and then b stays at his place and 
    # so now we can say from the first positon (from left to right) to the 8th position we have the value r from the 8th to the 16th position we have the value of g and the rest is the value of b
    r = r << 16
    g = g << 8
    b = b
    return r+g+b # its like if you have 40 40 94 its 40 00 00 + 40 00 + 94 = 40 40 94 because they are all at different positions

    #if admin channel doesnt exist ask if the bot should create one
    #if bot channel doesnt exist  not ask for permission to create one
    #ask whats the first role in the server 
    #check if role exists else ask to create it
    #...
    #ask whats the 5th role that should be earned with xp if it doesnt exist ask to create one
    #check if a welcome channel, a event channel, a goodbye channel exist if not ask to create one

@client.command(aliases=['8ball'], help = 'This command responds to your questions with yes, no or maybe',brief='Responds to a question.')
async def question_responder(ctx,question:str):
    await ctx.send(random.choice(['yes','no','maybe']))

@client.command(help='This cmd timeouts you for the given amount of seconds.',brief='Times out yourself.')
async def self_timeout(ctx:commands.Context,time:str='60'):
    if not time.isdigit():
        return
    if int(time) > 10000:
        await ctx.reply('You can maximally timout out yourself for 10000 seconds.',delete_after=5)
        await delete_message(ctx.message,time=5)
        return   
    await timeout_logic(ctx,ctx.author,f'{time}s',reason='self_timout')
    await delete_message(ctx.message)   

for cmd in client.commands:
    commands_list.append(cmd.name) 

client.run(token)
#completed have a setup dict that has all the server guild ids in it and if the id is in there of the using server then you cant use it until you have setup
#completed FIX STATS CARD OF OTHER RANKS          
#completed made the bot compatible server wide
#completed added question responder cmd
#completed added self_timout cmd with self choosable times up to 10000
#completed FIX ADD MSG XP
#completed added a help description to every cmd.
#completed made a class of server stats and user stats.
#completed fixed logs.
#TODO add cmd aliases like 8ball for question_responder
#TODO split code into multiple files
#TODO Personalisation
#TODO split into multiple files
#TODO to simplify the transition from a json to database and not changing everything put everything into a guild data json. Also build an automatic migration system for that
#TODO change everything to database
#TODO create a setup command that sets up the entire envoirement that the bot needs and he only adds things if theyre not present
#TODO make every data dict server specific
#TODO add a discussion recommendation if no one speeks and only if he hasnt sent anything not answereed before
#TODO Learn complicated classes 
#TODO add a voting system for mini mod
#TODO fix link opener but when link is invalid
#TODO remove migration system from stats opener
#TODO change 'admin' chanel to logs channel
#TODO make the bot more customizable per server
#TODO for more customizibility make the events toggable
#TODO make welcome goodbye and event channels also toggable
#TODO test if the bot doesnt crash when not having the required permissions in a server
#TODO fix logs displayed and file size