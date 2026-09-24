from shared_vars import discord, waiting_confirmations,change_confirmations, headers, admin_channel_name, allowed_types_in_bytes, ENDING_IMGS, command_prefix
from shared_vars import NOT_TO_USE,IQ_REACTIONS,SIDEEYE_REACTIONS,NPC_REACTIONS,ABSOLUTE_CINEMA_REACTIONS,SUS_REACTIONS,SKILLISSUE_REACTIONS,FIGHT_STARTING_REACTIONS,ONE_WORD_AKWARD,OVERDRAMATIC_REACTIONS,TEXT_DETECTION_CONFIDENCE_PERCENTAGE
from stats_system.user_stats import User_stats
from stats_system.server_stats import Server_stats,commands
from message_events.message_events_logic import sort_by_newest, check_spam,rank_check,check_slurs,get_matching_return_message,check_unsafe_text,check_unsafe_image_content
from user_management.user_strikes import add_strike_code
from message_events.message_management_logic import delete_message, log
from utils.typing_utils import enforce_guild,GuildMessage,Initialized_Bot
from utils.utils import get_admin_channel
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import asyncio
import os
import aiohttp
import re
import urllib.error
import random


d_face_reacts = ['skillissue', 'brofailed', 'rip', 'imagine']

class Message_events(commands.Cog):
    def __init__(self,client:Initialized_Bot,server_stats:Server_stats):
        """Initialize the class with the Discord bot and the server stats. 

        Args:
            client (Initialized_Bot): The Discord Bot.
            server_stats (Server_stats): The server stats.
        """
        self.client = client
        self.server_stats = server_stats

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_message(self,message:GuildMessage):
        """
        Called when a message gets sent in guild with this bot.
            Does the following:
                    - Has a chance depending on the content of the message to react with a GIF or emoji.
                    - Logs the message.
                    - Checks for spam.
                    - Checks for slurs and nudity in images attached and the message content.
                    - Adds the corresponding xp to the message author.
                    - Checks if the user can be promoted.
                    - Responds if the message was sent in an allowed channel.
        Args:
            message (discord.Message): The sent message.
        """
        global waiting_confirmations, change_confirmations
        guild = message.guild
        if not guild:
            return
        user_stats = self.server_stats.user_stats(guild)
        user_stats : User_stats
        if message.author.id == self.client.user.id:
            if self.server_stats.stats[guild.id]['set_up'] is True:
                user_stats.add_msg(message.author)
            return        
        message = enforce_guild(message)
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
        for word in NOT_TO_USE:
            if word in message.content.lower().replace('@', 'a').replace('1', 'i').replace('!', 'i').replace('ĝ','g').replace('é', 'e').replace('ř', 'r').strip('?=’,.\'.').replace('4','a').replace('1','i').replace('3', 'e').replace('5','s').replace('8', 'o'):
                dont_send = True
                break
        
        if dont_send == False:
            #reacting to messages
            if message.content.lower().strip() in d_face_reacts:
                if random.randint(1, 10) == 1:
                    await message.add_reaction('\\<:DFace:1470918226446782763>')
                    return
        
            for text in SIDEEYE_REACTIONS:
                if text in message.content.lower():
                    if random.randint(1,5) == 1:
                        if random.randint(1,3) == 2:
                            await message.reply(random.choice(['https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExem16OG5jZTVpMzg4eHJyZWM5NmI5ZHd0YXJoZGZidTd2cXAwNWllcyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/9G1pzYSsO90rBapiEv/giphy.gif',
                                            'https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExdXNwN2dvbHV5em9jdndqYnZ6NjdxZDR5MnoxaTcwdW5nbzUyZWZ3bCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/cFgb5p5e1My3K/giphy.gif']))
                            break
                        else:
                            await message.add_reaction('🤨')
                            break
            for text in SKILLISSUE_REACTIONS:
                if text in message.content.lower():
                    if random.randint(1,5) == 1:
                        if random.randint(1,3) == 2:
                            await message.reply(random.choice(gif_reactions['skillissue']))
                            break
                        await message.add_reaction(random.choice(['💀', '\\<:embarassing:1471526438057410763>','🤡']))
                        break   

            for text in IQ_REACTIONS:
                if text in message.content.lower():
                    if random.randint(1,8) == 1:
                        if random.randint(1,5) == 4:
                            await message.reply(random.choice(gif_reactions['iq']))
                            break
                        await message.add_reaction(random.choice(['🧠', '🤯', '🔥']))
                        break
            
            for text in SUS_REACTIONS:
                if text in message.content.lower():
                    if random.randint(1,5) == 1:
                        if random.randint(1,3) == 2:
                            await message.reply(random.choice(gif_reactions['sus']))
                            break
                        await message.add_reaction(random.choice(['🤨', '😳', '👀','\\<:pause:1471529450712731860>' ]))
                        break

            for text in ONE_WORD_AKWARD:
                if text == message.content.lower():
                    if random.randint(1,5) == 1:
                        if random.randint(1,3) == 2:
                            await message.reply(random.choice(gif_reactions['akward_silence']))
                            break
                        await message.add_reaction(random.choice(['😐', '😶', '🦗','\\<:embarassing:1471526438057410763>']))
                        break

            for text in NPC_REACTIONS:
                if text in message.content.lower():
                    if random.randint(1,5) == 1:
                        if random.randint(1,3) == 2:
                            await message.reply( random.choice(gif_reactions['npc_moments']))
                            break
                        await message.add_reaction(random.choice(['🤖','\\<:NPC:1471531032447684834>','\\<:bot:1471531101381066886>']))
                        break

            for text in FIGHT_STARTING_REACTIONS:
                if text in message.content.lower():
                    if random.randint(1,5) == 1:
                        await message.channel.send(random.choice(gif_reactions['fight_starting']))
                        break

            if message.content.upper() == message.content and '!' in message.content:
                if random.randint(1,8) == 1:
                    await message.channel.send(random.choice(gif_reactions['chaos']))
            
            for text in OVERDRAMATIC_REACTIONS:
                if text in message.content.lower():
                    if random.randint(1,5) == 1:
                        await message.channel.send(random.choice(gif_reactions['overdramatic']))
            
            for text in ABSOLUTE_CINEMA_REACTIONS:
                if text in message.content.lower():
                    if random.randint(1,4) == 1:
                        await message.channel.send(random.choice(gif_reactions['absolute_cinema']))
                
        if message.guild and message.guild.id != guild.id:#print('Mesage was sent in the wrong server.')
            return
        elif not message.guild:#print('Message was sent in a dm.')
            return


        if self.server_stats.stats[guild.id].get('set_up') is not None and self.server_stats.stats[guild.id].get('set_up') is False:
            if message.content.lower() != '!setup':
                #checks if the user was doing a confirmation
                if message.author.id in waiting_confirmations:
                    if message.author.id in change_confirmations:
                        waiting_confirmations.remove(message.author.id)
                        change_confirmations.remove(message.author.id)
                    return
                msg = await message.channel.send('You have to set up the bot with !setup to be able to use the bot.',reference=message)
                await delete_message([msg,message],time=5)
            return

              
        #logs the sent message
        temp_logs = self.server_stats.stats[message.guild.id]['temp_logs']
        full_logs = self.server_stats.stats[message.guild.id]['full_logs']
        self.server_stats.stats[message.guild.id]['temp_logs'] = log(temp_logs,message)
        self.server_stats.stats[message.guild.id]['full_logs'] = log(full_logs, message)
        full_logs = sort_by_newest(full_logs)
        save_full_logs = {}
        for time_obj, user_msgs_at_time in full_logs.items():
            time_obj = str(time_obj)
            if time_obj not in save_full_logs.keys():
                save_full_logs[time_obj] = {}
            for user, msgs in user_msgs_at_time.items():
                save_full_logs[time_obj][user] = msgs
        await self.server_stats.save_stats()
        if message.channel != 'spam':
            await check_spam(self.client, message.guild,self.server_stats,message) #checks if the messages are spam
        username = str(message.author).split('#')[0]
        try:
            channel = message.channel.name
        except AttributeError:
            channel = 'DM channel'

        channel_id = message.channel.id
        user_message = str(message.content)
        guild_name = guild.name
        print(f'Message {user_message} was sent by {username} in the following channel: {channel} in the server {guild_name}')
        strikes  = self.server_stats.strikes(guild)

        #returns a score between 0 and 1 about how save a img object is
        async def check_image_safety(attachment_in_bytes:bytes):
            """Checks if the given image contains either nudity or slurs. Message gets deleted if either is detected.

            Args:
                attachment_in_bytes (bytes): The sent image in bytes.
            """
            risk = 0
            with Image.open(BytesIO(attachment_in_bytes)) as img:
                img = img.convert('L')
                filepath = r'images/sent_img.png'
                img.save(filepath,format='PNG')
                _, risk = await check_unsafe_text(filepath)
                data = await check_unsafe_image_content(filepath,risk)
                risk += data[1]
                del data
                os.remove(filepath)
                if risk == 5 or risk == 4:
                    channel = discord.utils.get((channel for channel in guild.channels if isinstance(channel,discord.abc.Messageable)),name=admin_channel_name)
                    if not channel:
                        return 
                    await channel.send(f'Flagged image from user <@{message.author.id}>.\nIts risk was rated {risk}/9.\nLink to message {message.jump_url}.',allowed_mentions=discord.AllowedMentions(users=True))
                elif risk > 5:
                    channel_admin = get_admin_channel(guild)
                    reason = 'sending an explicit image'
                    await add_strike_code(message.author, self.server_stats, message,1,reason)
                    await delete_message(message)
                    if not channel_admin:
                        return
                    try:
                        await message.author.send(f'You got one strike for {reason}. Please be sure to follow the server rules or else you could be timed out or banned.\nYou currently have {str(strikes[message.author.id])} strikes.',allowed_mentions=discord.AllowedMentions(users=False))
                        await channel_admin.send(f'User <@{message.author.id}> got one strike for {reason}.\nUser <@{message.author.id}> currently has {str(strikes[message.author.id])} strikes.',allowed_mentions=discord.AllowedMentions(users=False))
                    except discord.Forbidden:
                        await message.channel.send(f'User <@{message.author.id}> got one strike for {reason}.\nThis message was sent in admin because I cannot send DM to <@{message.author.id}> (DMs disabled or blocked).',allowed_mentions=discord.AllowedMentions(users=False))
                    except Exception as e:
                        print(e)
                        await channel_admin.send(f'An unexpected error occured while trying to send strike warning to <@{message.author.id}>.\nError: {e}',allowed_mentions=discord.AllowedMentions(users=False))         
        
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
                                    async with session.get(url, timeout=aiohttp.ClientTimeout(10)) as page:
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
                                async for file_part in page.content.iter_chunked(1024):
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
                    channel = get_admin_channel(guild)
                    if channel is None:
                        return
                    await channel.send(f'Flagged image from user {message.author.name}.\nIts image size was greater than 20MB/9.')
                    await channel.send(f'Message link {message.jump_url}')

            if message.attachments:
                for attachment in message.attachments:
                    if any(attachment.filename.lower().endswith(ending) for ending in ENDING_IMGS):
                        attachment_in_bytes = await attachment.read()
                        await check_image_safety(attachment_in_bytes)
                                
            print(type(message))
            await check_slurs(message,self.server_stats,self.client)

            #levels up the stats  
            await rank_check(message.author,self.server_stats)

            allowed_channels = self.server_stats.stats[guild.id]['allowed_channels']        
            #checks if the message was sent in another channel and if thats true it checks if the bot was mentioned.
            if allowed_channels:
                if channel_id not in allowed_channels: #checks if the channel wich the message was sent in is allowed.
                    if message.channel.name.lower() != 'admin':
                        if self.client.user not in message.mentions and message.mentions != f'<{self.client.user.id}>':
                            return
                        if user_message.replace(f'<@{str(self.client.user.id)}>', '').strip().startswith(command_prefix):
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
        user_stats.add_msg(message.author)
        
        #makes the text readable
        for mention in message.mentions:
            user_message =  user_message.replace(f'<@{mention.id}>', '').strip()
        if user_message.startswith(command_prefix):
            if message.content.startswith(command_prefix):
                return
            await self.client.process_commands(message)
            return
        winner_user = await self.server_stats.winner_user(guild)
        winner_content = await self.server_stats.winner_content(guild)
        if not dont_send:
        #Starting from here the rest is responses to normal messages
            if user_message.lower().strip('?.\'"') in ['what are we watching this sunday', 'what are we going to watch this sunday']:
                            if winner_user:
                                if winner_user != 1:
                                    to_send= f'<@{winner_user.id}> will be or is hosting **{winner_content}** this sunday.'
                                else:
                                    to_send = f'<@{winner_user.id} is currently hosting **{winner_content}** in the General VC.'

                            else:
                                to_send = 'The winner suggestion will only be determined this sunday one hour before the event.'
            else:
                to_send = get_matching_return_message(message)
            allowed_mentions= discord.AllowedMentions(everyone=False,users=False,roles=False)
            try:
                await message.reply(to_send,allowed_mentions=allowed_mentions)
            except discord.errors.HTTPException:
                await message.channel.send(to_send,allowed_mentions=allowed_mentions)
