import discord
import os
import random
from dotenv import load_dotenv
from discord.ext import commands, tasks
import re
from datetime import timedelta, datetime, timezone
import json
import difflib
import math
import statistics
import asyncio
import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import aiohttp
from pathlib import Path
load_dotenv() 

strikes = {}
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
command_prefix = '!'
client = commands.Bot(command_prefix= command_prefix, intents = intents)
commands_list = []
logs = {}
is_user_spamming = {}
forbidden_words = ['67']
waiting_confirmations = []
change_confirmations = []
token = os.getenv('TOKEN')
waiting_list  = {}
d_face_reacts = ['skillissue', 'brofailed', 'rip', 'imagine']
user_stats = {}

with open('roles_requirements.json','r') as f:
    roles_requirements = json.load(f)

with open('stats.json', 'r') as f:
    user_stats = json.load(f)

with open('allowed_channels.json', 'r') as f:
    allowed_channels = json.load(f)

with open('code.json', 'r') as f:
    code_dict = json.load(f)

with open('fr.txt', 'r') as f:
    for word in set(f):
        forbidden_words.append(word.strip('\n'))

with open('de.txt', 'r') as f:
    for word in set(f):
        forbidden_words.append(word.strip('\n'))

with open('en.txt', 'r') as f:
    for word in set(f):
        forbidden_words.append(word.strip('\n'))

with open('strikes.json', 'r', encoding = 'utf-8') as f:
    strikes = json.load(f)

months = {'01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'}
roles_imgs = {'owner': r'owner.png', 'mini mod': '','klassebot': r'bot.png', 'admin': r"admin.png", 'dev': r"dev.png", 'trial dev': r"trial_dev.png", 'elite member': r'Elite_member.png', 'member': r"member.png", 'beginner': r'beginner.png', 'spammer':''}

admin_channel_id = 1466034381499007084
bot_channel_id = 1466034381499007082
welcome_channel_id = 1466034381499007083
server_id = 1466034380656083089


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
async def on_command_error(ctx, error):
    print(error)
    if isinstance(error, commands.RoleNotFound):
        await ctx.send('The role does not exist.')
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send('You lack the permissions to execute this command.')
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send('Member not found. Please ensure you mentioned a valid Member.')
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send('I lack the permissions to execute this command. Please contact the bot owner if this behaviour is unexpected.')
    elif isinstance(error, commands.BadArgument):
        await ctx.send('Member not found. Please ensure you mentioned a valid Member.')
    elif isinstance(error, discord.Forbidden):
        await ctx.send('I am not capable of performing actions for members above or at my same rank.')
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send(mismatch_message(str(ctx.invoked_with)))
    else:
        await ctx.send('An error has occured while trying to execute this command.')

def is_dict_complete():
    for server in client.guilds:
        for member in server.members:
            if member.name not in strikes.keys() and member.name != client.user.name:
                strikes[member.name] = 0
                with open('strikes.json', 'w') as f:
                    json.dump(strikes, f)
            if member.name not in user_stats.keys():
                user_stats[member.name] = {'message_count': 0, 'join_date': member.joined_at.strftime('%d.%m.%Y'),'xp': 0 }
                update_rank(member)
                with open('json.stats', 'w') as f:
                    json.dump(user_stats, f)

def update_rank(member: discord.Member):
    if any(role.name.lower() == 'owner' for role in member.roles):
        rank = 'owner'
        next_rank = 'None'
        img = roles_imgs['owner']
    elif any(role.name.lower() == 'klassebot' for role in member.roles):
        rank = 'KlasseBot'
        next_rank = 'None'
        img = roles_imgs['klassebot']
    elif any(role.name.lower() == 'admin' for role in member.roles):
        rank = 'admin'
        next_rank = 'Normally there is no greater rank beyond admin.'
        img = roles_imgs['admin']
    elif any(role.name.lower() == 'mini mod' for role in member.roles):
        rank = 'mini mod'
        next_rank = 'admin'
        img = roles_imgs['mini_mod']
    elif any(role.name.lower() == 'dev' for role in member.roles):
        rank = 'dev'
        next_rank = 'mini mod'
        img = roles_imgs['dev']
    elif any(role.name.lower() == 'trial dev' for role in member.roles):
        rank = 'trial dev'
        next_rank = 'dev'
        img = roles_imgs['trial dev']
    elif any(role.name.lower() == 'elite member' for role in member.roles):
        rank = 'elite member'
        next_rank = 'trial dev'
        img = roles_imgs['elite member']
    elif any(role.name.lower() == 'member' for role in member.roles):
        rank = 'member'
        next_rank = 'elite member'
        img = roles_imgs['member']
    elif any(role.name.lower() == 'spammer' for role in member.roles):
        rank = 'spammer'
        next_rank = 'Currently not avalible.'
        img = roles_imgs['spammer']
    else:
        rank = 'beginner'
        next_rank = 'member'
        img = roles_imgs['beginner']
    
    user_stats[member.name]['rank'] = rank
    user_stats[member.name]['next_rank'] = next_rank
    user_stats[member.name]['img'] = img
    try:
        user_stats[member.name]['xp_for_next_rank'] = roles_requirements[next_rank]['xp'] - user_stats[member.name]['xp']
    except KeyError:
        promotion_path = 'error'
        if next_rank == 'mini mod':
            promotion_path = 'through votes of users with the rank member or higher'
        elif next_rank == 'admin':
            promotion_path = 'trough manual promotion of the server owner. You also need to be a mini mod at the moment of promotion.'
        elif next_rank == 'Currently not avalible.':
            promotion_path = 'by loosing the role spammer'        
        if next_rank == 'None':
            user_stats[member.name]['xp_for_next_rank'] = 'There is no greater rank beyond Owner'
        else:
            user_stats[member.name]['xp_for_next_rank'] = promotion_path

    with open('stats.json', 'w') as f:
        json.dump(user_stats, f)

@client.event
async def on_ready():
    print(f'Logged in as bot {client}')
    is_dict_complete()
    is_waiting_expired.start()

@client.event
async def on_message(message):
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
    #prevents the bot responding to himself
    if message.author == client.user:
        user_stats[message.author.name]['xp'] += 5
        user_stats[message.author.name]['message_count'] += 1
        with open('stats.json', 'w') as f:
            json.dump(user_stats, f)
        return
    
    dont_send= False
    for word in not_to_use:
        if word in message.content.lower().replace('@', 'a').replace('1', 'i').replace('!', 'i').replace('ĝ','g').replace('é', 'e').replace('ř', 'r').strip('?=’,.\'.').replace('4','a').replace('1','i').replace('3', 'e').replace('5','s').replace('8', 'o'):
            dont_send= True
            break   
    
    if dont_send == False:
        #reacting to messages
        if message.content.lower().strip() in d_face_reacts:
            if random.randint(1, 10) == 1:
                await message.add_reaction('\<:DFace:1470918226446782763>')
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
                    await message.add_reaction(random.choice(['💀', '\<:embarassing:1471526438057410763>','🤡']))
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
                    await message.add_reaction(random.choice(['🤨', '😳', '👀','\<:pause:1471529450712731860>' ]))
                    break

        for text in one_word_akward:
            if text == message.content.lower():
                if random.randint(1,5) == 1:
                    if random.randint(1,3) == 2:
                        await message.reply(random.choice(gif_reactions['akward_silence']))
                        break
                    await message.add_reaction(random.choice(['😐', '😶', '🦗','\<:embarassing:1471526438057410763>']))
                    break

        for text in npc_reactions:
            if text in message.content.lower():
                if random.randint(1,5) == 1:
                    if random.randint(1,3) == 2:
                        await message.reply( random.choice(gif_reactions['npc_moments']))
                        break
                    await message.add_reaction(random.choice(['🤖','\<:NPC:1471531032447684834>','\<:bot:1471531101381066886>']))
                    break

        

        for text in fight_starting_reactions:
            if text in message.content.lower():
                if random.randint(1,5) == 1:
                    await message.channel.send(random.choice(gif_reactions['fight_starting']))
                    break
        #is_spam = False
        #for user in is_user_spamming:
       #     if user:
       #         is_spam = True

        #if is_spam:
        #    if random.randint(1,4) == 2:
        #        await message.channel.send(random.choice(gif_reactions['chaos']))


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
            
    if message.guild and message.guild.id != server_id:#print('Mesage was sent in the wrong server.')
        return
    elif not message.guild:#print('Message was sent in a dm.')
        return
    #logs the sent message
    if message.author not in logs.keys():                       
        logs[message.author] = {}
    if message.created_at not in logs[message.author].keys():
        logs[message.author][message.created_at]  = []
    logs[message.author][message.created_at].append(message.content)

    if message.channel != 'spam':
        await check_spam() #checks if the messages are spam

    username = str(message.author).split('#')[0]
    try:
        channel = message.channel.name
    except AttributeError:
        channel = 'DM channel'
    channel_id = message.channel.id
    user_message = str(message.content)
    print(f'Message {user_message} was sent by {username} in the following channel: {channel}')
    
    #checks for slurs in the message
    if channel != 'spam':
        words_in_phrase = re.findall(r'\b\w+\b', user_message.lower()) #splits the message content into words
        for word in words_in_phrase:
            word = word.lower().strip('?’=,.\'.').replace('@', 'a').replace('1', 'i').replace('!', 'i').replace('ĝ','g').replace('é', 'e').replace('ř', 'r').replace('4','a').replace('1','i').replace('3', 'e').replace('5','s').replace('8', 'o')
            if word in forbidden_words:
                channel = client.get_channel(admin_channel_id) #admin channel
                await add_strike_code(message.author, '1', await client.get_context(message))
                try:
                    await message.author.send(f'You got one strike for sayng: {word}. Please be sure to follow the server rules or else you could be timed out or banned.\nYou currently have {str(strikes[message.author.name])} strikes.')
                    channel = client.get_channel(admin_channel_id)
                    await channel.send(f'User {message.author.name} got one strike for sayng: {word}.\nUser {message.author.name} currently has {str(strikes[message.author.name])} strikes.')
                except discord.Forbidden:   
                    await message.reply(f'User {username} got one strike for saying: {word}.\nThis message was sent in admin because I cannot send DM to {message.author} (DMs disabled or blocked).')
                except Exception as e:
                    await message.reply(f'An unexpected error occured while trying to send strike warning to {username}.\nError: {e}')
                await delete_message(message)
                return
        
    #levels up the stats
    user_stats[message.author.name]['xp'] += 5
    user_stats[message.author.name]['message_count'] += 1
    with open('stats.json', 'w') as f:
        json.dump(user_stats, f)
    await rank_check(message.author)
    

    #checks if the message was sent in another channel and if thats true it checks if the bot was mentioned.
    if len(allowed_channels) > 0:
        if channel_id not in allowed_channels.values(): #checks if the channel wich the message was sent in is allowed.
            if client.user not in message.mentions and message.mentions != f'<{client.user.id}>':
                return
            if user_message.replace(f'<@{str(client.user.id)}>', '').strip().startswith(command_prefix):
                    reply = await message.reply(f'Please use the bot commands channel for bot commands.', delete_after = 5) # later adapt it so it "pings" the bot commands channel.
                    await asyncio.sleep(5)
                    await delete_message(message)
                    await delete_message(reply)
                    return
            
    #checks if the user was doing a confirmation
    if message.author in waiting_confirmations:
        if message.author in change_confirmations:
            waiting_confirmations.remove(message.author)
        return
    
    #makes the text readable
    for mention in message.mentions:
        user_message =  user_message.replace(f'<@{mention.id}>', '').strip()
    if user_message.startswith(command_prefix):
        await client.process_commands(message)
        return
    
    if dont_send == False:
    #Starting from here the rest is responses to normal messages
        if user_message.lower() == 'hello' or user_message.lower() == 'hi':
            await message.channel.send(f'Hello {username}')
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


@client.event
async def on_member_update(before: discord.Member, after: discord.Member):
    if before.roles != after.roles:
        update_rank(after)


async def rank_check(member: discord.Member):
    next_rank = user_stats[member.name]['next_rank']
    user_xp = user_stats[member.name]['xp']
    user_strikes = strikes[member.name]
    if next_rank in roles_requirements.keys():
        if roles_requirements[next_rank]['xp'] <= user_xp and roles_requirements[next_rank]['strikes'] >= user_strikes:
            guild = client.get_guild(server_id)
            old_rank = discord.utils.get(guild.roles, name= user_stats[member.name]['rank'])
            new_rank = discord.utils.get(guild.roles, name = next_rank)
            await promote(old_rank, new_rank, member)

async def promote(old_role: discord.Role, new_role: discord.Role, member: discord.Member):
    await remove_role_logic(member, old_role)
    await give_role_logic(member, new_role)
    user_stats[member.name]['xp'] = 0
    with open('stats.json', 'w') as f:
            json.dump(user_stats, f)
    update_rank(member)
    try:
        await member.send(f'You successfully got promoted from {old_role.name} to {new_role.name}.')
    except discord.Forbidden:
        channel = client.get_channel(admin_channel_id)
        await channel.send(f'Successfully promoted {member.name} from {old_role.name} to {new_role.name}.')
    except Exception as e:
        print(e)
        channel = client.get_channel(admin_channel_id)
        await channel.send(f'An error occoured while trying to promote {member.name} from {old_role.name} to {new_role.name}.\nPlease contact the bot dev if this behaviour is unexpected.')

@client.command()
async def ping(ctx):
    await ctx.send('Pong!')


@client.command()
@commands.has_role('dev')
@commands.bot_has_permissions(manage_messages= True)
async def set_xp(ctx, member: discord.Member, amount):
    if type(amount) != int:
        amount = int(amount)
    user_stats[member.name]['xp'] = amount
    with open('stats.json', 'w') as f:
        json.dump(user_stats, f)
    await ctx.send(f'succecfully set {member.name}\'s xp to {amount}.')


@client.command()
@commands.has_permissions(manage_roles= True)
@commands.bot_has_permissions(manage_roles = True)

async def give_role(ctx, member: discord.Member, role: discord.Role):
    await give_role_logic(member, role, ctx)

async def give_role_logic(member: discord.Member, role: discord.Role, ctx = None):
    if ctx == None:
        channel = client.get_channel(admin_channel_id) #admin channel
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

@client.command()
@commands.has_permissions(manage_roles= True)
@commands.bot_has_permissions(manage_roles = True)

async def remove_role(ctx, member: discord.Member, role: discord.Role):
    message = await remove_role_logic(member, role)
    await ctx.send(message)

async def remove_role_logic(member: discord.Member, role: discord.Role):
    try:
        await member.remove_roles(role)
        channel = client.get_channel(admin_channel_id)
        await channel.send(f'Successfully removed {role.name} from {member.display_name}.')
        return f'Successfully removed {role.name} from {member.display_name}.'
    except discord.Forbidden:
        return f'I do not have permission to remove role: {role.name} from {member.name}.'
    except Exception as e:
        print(e)
        return 'An unexpected Error has occoured please contact the Bot owner.'
@client.command()
async def list_roles(ctx):
    roles = ctx.guild.roles
    roles_list = []
    for role in list(roles):
        if role.name != '@everyone':
            roles_list.append(role.name)
    await ctx.send(f'Avalible roles:\n'+'\n'.join(f'- {role}' for role in roles_list))


@client.command()
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
    
@client.command()
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
    channel =  client.get_channel(welcome_channel_id)#welcome channel
    await channel.send(f'Welcome {member.name}!')
    guild = client.get_guild(server_id)
    role = discord.utils.get(guild.roles, name = 'beginner') 
    give_role(member, role)

@client.command()
@commands.has_permissions(moderate_members=True)
@commands.bot_has_permissions(moderate_members=True)

async def timeout(ctx, member: discord.Member, duration: str, *,reason: str = 'No valid reason provided'):
    await timeout_logic(ctx, member, duration ,reason = reason) 
    
async def timeout_logic(ctx, member: discord.Member, duration: str, *,reason: str = 'No valid reason provided'):
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
            if ctx == None:
                return 'Please enter a allowed time value. Valid formats are: s, m, h, d.'
            else:
                await ctx.send('Please enter a allowed time value. Valid formats are: s, m, h, d.')
        await member.timeout(timeout_time, reason=reason)
        channel =  client.get_channel(admin_channel_id)
        await channel.send(f'Member {member.name} has been timed out for {duration}. Reason: {reason}.')
    except ValueError:
        channel = client.get_channel(admin_channel_id)
        await channel.send(f'Member {member.name} has not been timed out for {duration}. Reason {reason}.\nIt failed because of a ValueError.')
    except discord.Forbidden:
        await ctx.send('I am not capable of performing actions for members above or at my same rank.')

async def add_strike_code(member: discord.Member, amount = '1', ctx = None):
    if type(amount) != int:
        amount = int(amount)
    strikes[member.name] += amount
    await strikes_punishments(member, ctx)

@client.command()
@commands.has_permissions(moderate_members=True)
@commands.bot_has_permissions(moderate_members= True)

async def add_strike(ctx, member: discord.Member, amount = '1' ):
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


@client.command()
@commands.has_permissions(manage_roles= True)
@commands.bot_has_permissions(manage_roles= True)
async def strikes_list(ctx):
    answer = ''
    for key, value in strikes.items():
        if value == 1:
            answer += (f'User: {key} has {value} strike.\n')
        else:
            answer += (f'User: {key} has {value} strikes.\n')
    await ctx.send(answer)

@client.command()
async def my_strikes(ctx):
    member = ctx.author
    if strikes[member.name] == 1:
        await ctx.send(f'You have {strikes[member.name]} strike.')
    else:
        await ctx.send(f'You have {strikes[member.name]} strikes.')


@client.command()
@commands.has_permissions(moderate_members=True)
@commands.bot_has_permissions(moderate_members= True)
async def set_strikes(ctx, member: discord.Member, amount= '1'):
    await set_strikes_code(ctx, member, amount)

async def set_strikes_code(ctx, member: discord.Member, amount ='1'):
    if type(amount) != int:
        amount = int(amount)
    strikes[member.name] = amount
    await strikes_punishments(member)
    await ctx.send(f'The strikes of {member.name} were successfully set to {amount}')


async def strikes_punishments(member: discord.Member, ctx  = None):
    channel =  client.get_channel(admin_channel_id) #admin channel
    guild = client.get_guild(server_id)
    old_role = discord.utils.get(guild.roles, name = user_stats[member.name]['rank'])
    spammer = discord.utils.get(guild.roles, name= 'spammer')
    if old_role.name == 'owner' or old_role.name == 'admin' or old_role.name == 'mini mod' or old_role.name == 'dev' or old_role.name == 'trial dev':
        if strikes[member.name] < roles_requirements[old_role.name]['strikes']+ 10:
            return
    if channel is None:
        print('Could not find channel with the set channel ID.')
        return
    if strikes[member.name] == 1:
        time = '1m'
        await timeout_logic(ctx, member, time, reason= 'The user has one strike')
        await channel.send(f'{member.name} was timedout for {time} for having {strikes[member.name]} strikes.')
    elif strikes[member.name] == 2:
        time = '5m'
        msg = await timeout_logic(ctx, member, time, reason= 'The user has two strikes')
        print(msg)
        await channel.send(f'{member.name} was timedout for {time} for having {strikes[member.name]} strikes.')
    elif strikes[member.name] >= 3 and strikes[member.name] <= 19:
        user_stats[member.name]['role_before_spam'] = old_role.name
        await promote(old_role, spammer, member)
        with open('stats.json', 'w') as f:
            json.dump(user_stats, f)
        ban_time = timedelta(seconds = 100)
        if strikes[member.name] == 4:
            ban_time = timedelta(minutes= 5)
        elif strikes[member.name] == 5:
            ban_time = timedelta(minutes= 10)
        elif strikes[member.name] == 6:
            ban_time = timedelta(minutes= 15)
        elif strikes[member.name] == 7:
            ban_time = timedelta(minutes= 20)
        elif strikes[member.name] == 8:
            ban_time = timedelta(minutes= 30)
        elif strikes[member.name] == 9:
            ban_time = timedelta(hours= 1)
        elif strikes[member.name] == 10:
            ban_time = timedelta(hours= 2)
        elif strikes[member.name] == 11:
            ban_time = timedelta(hours= 3)
        elif strikes[member.name] == 12:
            ban_time = timedelta(hours= 4)
        elif strikes[member.name] == 13:
            ban_time = timedelta(hours= 5)
        elif strikes[member.name] == 14:
            ban_time = timedelta(hours= 6)
        elif strikes[member.name] == 15:
            ban_time = timedelta(hours= 7)
        elif strikes[member.name] == 16:
            ban_time = timedelta(hours= 8)
        elif strikes[member.name] == 17:
            ban_time = timedelta(hours= 9)
        elif strikes[member.name] == 19:
            ban_time = timedelta(hours= 10)
        if member not in waiting_list.keys():
            waiting_list[member] = datetime.now(timezone.utc) + ban_time
        else:
            waiting_list[member] += ban_time

        if ctx == None:
            await channel.send(f'User {member.name} got flagged for spamming.')
        else:
            await ctx.reply('You got flagged for spamming or saying slurs.', delete_after = 5)

    elif strikes[member.name] >= 20 and strikes[member.name] <= 40:
        user_stats[member.name]['role_before_spam'] = old_role.name
        await promote(old_role, spammer, member)
        with open('stats.json', 'w') as f:
            json.dump(user_stats, f)
        await timeout_logic(member, '1d', reason=f'The user has {strikes[member.name]} strikes.')

    elif strikes[member.name] > 40:
        await member.kick(reason='You were kicked because you currently had 40 strikes on the server.\nPlease contact the server admins if you think this treatment is unfair.')
    
    with open('strikes.json', 'w') as f:
        json.dump(strikes, f)


async def set_strikes_code(ctx, member: discord.Member, amount ='1'):
    if type(amount) != int:
        amount = int(amount)
    strikes[member.name] = amount
    await strikes_punishments(member)
    await ctx.send(f'The strikes of {member.name} were successfully set to {amount}')


@tasks.loop(seconds= 10)
async def is_waiting_expired():
    guild = client.get_guild(server_id)#server ID
    members_to_remove = []
    spammer = discord.utils.get(guild.roles, name = 'spammer')
    for member in waiting_list:
        if waiting_list[member] <= datetime.now(timezone.utc):
            new_role = discord.utils.get(guild.roles, name= user_stats[member.name]['role_before_spam'])
            user_stats[member.name].pop('role_before_spam')
            with open('stats.json', 'w') as f:
                json.dump(user_stats, f)
            await promote(spammer,new_role, member)
            members_to_remove.append(member)

    for member in members_to_remove:
        waiting_list.pop(member)

async def delete_message(message, time = 0):
    """
    Docstring for delete_message
    
    :param message: discord.Message or list containing discord.Message
    :param time: Amount of seconds waiting before deleting.
    """
    if time != 0:
        await asyncio.sleep(time)
    if isinstance(message, discord.Message):
        await message.delete()
    if isinstance(message, list):
        for msg in message:
            if isinstance(msg, discord.Message):
                await msg.delete()


def del_old_logs():
    keys_to_pop = {}
    for user, messages in logs.items():
        for timestamp in messages.keys():
            five_min_before = datetime.now(timezone.utc) - timedelta(minutes=3)
            if timestamp < five_min_before:
                if user not in keys_to_pop.keys():
                    keys_to_pop[user] = [timestamp]
                else:
                    keys_to_pop[user].append(timestamp)
    for user, time in keys_to_pop.items():
        for timestamp in time:
            logs[user].pop(timestamp)

async def check_spam_without_punishment():
    global is_user_spamming
    del_old_logs()
    is_user_spamming = {}
    for user, message_logs in logs.items():
        all_msg_per_user = []
        for message_list in message_logs.values():
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
            for remove_msg in msg_to_remove:
                not_compared_msgs.remove(remove_msg)
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

    for user in is_user_spamming:
        if user == True:
            return True
        return False

async def check_spam():
    await check_spam_without_punishment()
    await spam_punishment()

async def spam_punishment():
    channel = client.get_channel(1466034381499007084) # admin channel
    for user in is_user_spamming:
        if is_user_spamming[user]:
            await channel.send(f'User {user} is spamming.')
            await add_strike_code(user, 1)
            logs[user] = {}
            is_user_spamming[user] = False
            break

@client.command()
@commands.has_permissions(manage_messages=True)
async def show_logs(ctx):
    readable_logs = ''
    for user, message_list in logs.items():
        append_msg = (f'User: {user} sent: ')
        for time, message in message_list.items():
            append_msg += f'\nmessages: {message} at {time.strftime("%H:%M:%M")}'
        readable_logs += f'{append_msg}\n'
    await ctx.send(readable_logs)

@client.command()
async def gen(ctx, user_input: str):
    all_descriptions = 'Avalible code is:'
    for description in code_dict.keys():
        if description == 'help':
            continue
        all_descriptions += '\n' + description
    code_dict['help'] = all_descriptions
    with open('code.json', 'w') as f:
        json.dump(code_dict, f)
    if user_input in code_dict.keys():
        await ctx.send(code_dict[user_input])
    else:
        if any(role.name == 'dev' for role in ctx.author.roles):
            await ctx.send('Would you like to add this code? (y/n)')
            waiting_confirmations.append(ctx.author)
            def check(msg: discord.Message):
                return msg.author != client.user and msg.author == ctx.author and msg.channel == ctx.channel
            try:
                response = await client.wait_for('message', timeout= 30, check = check)
                change_confirmations.append(ctx.author)
            except TimeoutError:
                await ctx.send('You took too long to respond.')
                return
            if response.content.lower() == 'y':
                await ctx.send('What is the code?')
                waiting_confirmations.append(ctx.author)
                try:
                    code = await client.wait_for('message', timeout= 180 , check = check)
                    change_confirmations.append(ctx.author)
                except TimeoutError:
                    await ctx.send('You took too long to respond.')
                    return
                final_code = format_to_python(code.content)
                code_dict[user_input] = final_code
                with open('code.json', 'w') as f:
                    json.dump(code_dict, f)
            elif response.content.lower() == 'n':
                return
        else:
            await ctx.send(f'This gen command does not exist.\nIf you want a list of all possible !gen commands enter !gen help.')
        
def format_to_python(code: str):
    final_code = '```python\n'
    final_code += code
    final_code += '```'
    return final_code

@client.command()
@commands.has_role('dev')
async def gen_edit(ctx, user_input: str):
    if user_input in code_dict.keys():
        def check(msg: discord.Message):
            return msg.author != client.user and msg.author == ctx.author and msg.channel == ctx.channel
        await ctx.send('What would you like to change the code to?(Enter exit to exit.)')
        waiting_confirmations.append(ctx.author)
        try:
            code = await client.wait_for('message', timeout= 180 , check = check)
            change_confirmations.append(ctx.author)
        except TimeoutError:
            await ctx.send('You took too long to respond.')
            return
        if code.content == 'exit':
            return
        final_code = format_to_python(code.content)
        code_dict[user_input] = final_code
        with open('code.json', 'w') as f:
                json.dump(code_dict, f)
    else:
        await ctx.send('This code description does not exist in the code dict.')
         
@client.command()
@commands.has_role('dev')
async def gen_del(ctx, user_input: str):
    if user_input in code_dict.keys():
        def check(msg: discord.Message):
            return msg.author != client.user and msg.author == ctx.author and msg.channel == ctx.channel
        await ctx.send('Are you sure that you want to delete the code for this command? (y/n)')
        waiting_confirmations.append(ctx.author)
        try:
            respnse = await client.wait_for('message', timeout= 100 , check = check)
            change_confirmations.append(ctx.author)
        except TimeoutError:
            await ctx.send('You took too long to respond.')
            return
        if respnse.content == 'y':
            code_dict.pop(user_input)
        else:
            return
        
    else:
        await ctx.send('This code description does not exist in the code dict.')
    
@client.command()
@commands.has_permissions(manage_messages = True)
@commands.bot_has_permissions(manage_messages=True)
async def clear_channel(ctx, channel_id: int = None):
    try:
        channel_name =   ctx.guild.get_channel(admin_channel_id).name 
    except:
        channel_name = 'general'
    if ctx.channel.name != channel_name: # admin channel
        return
    if channel_id == None:
        reply = await ctx.reply('Please enter a channel_ID')
        await delete_message([ctx, reply], time=5)
    try:
        channel = ctx.guild.get_channel(channel_id)
    except discord.NotFound:
        reply = 'Channel does not exist.\nPlease enter a valid channel_ID.'
        reply = await ctx.reply(reply)
        await delete_message([ctx, reply], time=5)
    await ctx.send(f'Are you sure that you want to delete all messages of the channel {channel.name}. Type y to confirm and n to exit.')
    waiting_confirmations.append(ctx.author)
    def check(msg: discord.Message):
        return msg.author != client.user and msg.author == ctx.author and msg.channel == ctx.channel
    try:
        response = await client.wait_for('message', timeout=30, check=check)
        change_confirmations.append(ctx.author)
    except asyncio.TimeoutError:
        await ctx.send('You took too long to respond.')
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

@client.command()
@commands.has_permissions(manage_channels=True)
async def add_allowed_channels(ctx, channel_id: str):
    for channel in ctx.guild.channels:
        if int(channel_id) == channel.id:
            if int(channel_id) in allowed_channels.values():
                await ctx.send(f'Channel is already an allowed channel.')
                return
            allowed_channels[channel.name] = int(channel_id)
            await ctx.send(f'Successfully added channel {channel.name} to the allowed channels.')
            return
    await ctx.send('Channel was not found. Please make sure that the entered channeld ID is an existing channel.')

@client.command()
@commands.has_permissions(manage_channels=True)
async def remove_allowed_channels(ctx, channel_id: str):
    for name, id in allowed_channels.items():
        if channel_id == id:
            allowed_channels.pop(name)
            await ctx.send(f'Successfully removed channel {name} from the allowed channels.')
    await ctx.send('Channel id is not yet registred to the allowed channels.')

@client.command()   
async def stats(ctx, user: discord.Member = None):
    if user == None:
        member = ctx.author
    else:
        member = user
    try:
        avatar_in_bytes = await member.display_avatar.read() if member.avatar else await member.default_avatar.read()
        rounded_img, mask = PIL_round_img_obj(avatar_in_bytes, (395,395))
        with Image.open('base.png','r') as img2:
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
        current_xp = user_stats[member.name]['xp']
        try:
            xp_needed = roles_requirements[user_stats[member.name]['next_rank']]['xp']
        except KeyError:
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
        if user_stats[member.name]['xp_for_next_rank'] == 'Owner is the highest rank':
            response = 'There is no way to rank up with xp after at this rank.'
        elif type(user_stats[member.name]['xp_for_next_rank']) == str:
            if user_stats[member.name]['xp_for_next_rank'] == 'There is no greater rank beyond Owner':
                if user_stats[member.name]['rank'] == 'KlasseBot':
                    response = f'There is no higher rank for me.'
                else:
                    response = f'There is no higher rank.'
            else:
                response = f'It is not possible to progress with XP.\nIt is only possible to rank up\n{user_stats[member.name]['xp_for_next_rank']}.'
        else:
            response = f'You need {user_stats[member.name]['xp_for_next_rank']} xp to rank up {user_stats[member.name]['next_rank']}\n(Every message gives 5xp).\n'
        counter = 0
        for split in user_stats[member.name]['join_date'].split('.'):
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
        draw = PIL_text_obj(draw,cords, f'Messages        {user_stats[member.name]['message_count']}',font_size= font_size)
        cords = cords[0], cords[1] + extra
        draw = PIL_text_obj(draw,cords, f'Rank                {user_stats[member.name]['rank']}',font_size= font_size)
        cords = cords[0], cords[1] + extra
        draw = PIL_text_obj(draw,cords, f'Next rank         {user_stats[member.name]['next_rank']}',font_size= font_size)
        cords = cords[0], cords[1] + extra
        draw = PIL_text_obj(draw,cords, f'Joined              {date}',font_size= font_size)
        cords = cords[0], cords[1] + extra
        draw = PIL_text_obj(draw,cords, f'Total XP           {user_stats[member.name]['xp']}',font_size= font_size)
        cords = cords[0], cords[1] + extra
        draw = PIL_text_obj(draw,cords, f'{response}',font_size= font_size)
        rank_img = user_stats[member.name]['img']
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
        white_image.save(ram,format='PNG')#saves it in the ram
        ram.seek(0)
        file = discord.File(fp=ram, filename='stats_card.png')
        await ctx.reply(file=file)#await ctx.reply(file=discord.File(file_to_send))
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

for cmd in client.commands:
    commands_list.append(cmd.name) 

client.run(token)