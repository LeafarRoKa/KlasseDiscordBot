from shared_vars import commands,Server_stats,discord, waiting_confirmations,change_confirmations, logs_temp, text_detection_ai, headers, nudity_classification, admin_channel_name, allowed_types_in_bytes, ending_imgs, command_prefix, full_logs
import random
from message_events.message_events_logic import sort_by_newest, check_spam, check_slurs_without_punishment,rank_check,check_slurs
from io import BytesIO
from PIL import Image, UnidentifiedImageError
import asyncio
from user_management.user_strikes import add_strike_code
from message_events.message_management import delete_message
import os
import aiohttp
import re
import urllib
d_face_reacts = ['skillissue', 'brofailed', 'rip', 'imagine']
class Message_events(commands.Cog):
    def __init__(self,client:commands.Bot,server_stats:Server_stats):
        self.client = client
        self.server_stats = server_stats

    @commands.Cog.listener()
    async def on_message(self,message:discord.Message):
        global waiting_confirmations, change_confirmations
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
        user_stats = self.server_stats.user_stats(guild)

        #prevents the bot from responding to himself
        if message.author.id == self.client.user.id:
            if self.server_stats.stats[guild.id]['set_up'] is True:
                user_stats.add_msg(message.author)
            return        
        if self.server_stats.stats[guild.id].get('set_up') is not None and self.server_stats.stats[guild.id].get('set_up') is False:
            if message.content.lower() != '!setup':
                #checks if the user was doing a confirmation
                if message.author.id in waiting_confirmations:
                    if message.author.id in change_confirmations:
                        waiting_confirmations.remove(message.author.id)
                        change_confirmations.remove(message.author.id)
                    return
                await message.channel.send('You have to set up the bot with !setup to be able to use the bot.')
            else:
                await self.client.process_commands(message)
            return
        
        
        #logs the sent message
        self.log(logs_temp,message,with_guild=True)
        self.log(full_logs, message)
        full_logs = sort_by_newest(full_logs)
        save_full_logs = {}
        for time_obj, user_msgs_at_time in full_logs.items():
            time_obj = str(time_obj)
            if time_obj not in save_full_logs.keys():
                save_full_logs[time_obj] = {}
            for user, msgs in user_msgs_at_time.items():
                user = str(user)
                save_full_logs[time_obj][user] = msgs
        self.server_stats.save_stats()
        if message.channel != 'spam':
            await check_spam(self.client,self.server_stats) #checks if the messages are spam

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
                    await add_strike_code(message.author, self.server_stats, '1', await self.client.get_context(message))
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
            await check_slurs(message,self.server_stats,self.client)

            #levels up the stats  
            await rank_check(message.author,self.server_stats)

            allowed_channels = self.server_stats.stats[guild.id]['allowed_channels']        
            #checks if the message was sent in another channel and if thats true it checks if the bot was mentioned.
            if allowed_channels:
                if channel_id not in allowed_channels.values(): #checks if the channel wich the message was sent in is allowed.
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
        
        #makes the text readable
        for mention in message.mentions:
            user_message =  user_message.replace(f'<@{mention.id}>', '').strip()
        if user_message.startswith(command_prefix):
            if message.content.startswith(command_prefix):
                return
            await self.client.process_commands(message)
            return
        winner_user = self.server_stats.winner_user(guild)
        winner_content = self.server_stats.winner_content(guild)
        if not dont_send:
        #Starting from here the rest is responses to normal messages
            if user_message.lower() == 'hello' or user_message.lower() == 'hi':
                await message.channel.send(f'Hello {username}')
            elif user_message.lower().strip('?.\'"') in ['what are we watching this sunday', 'what are we going to watch this sunday']:
                if winner_user:
                    if winner_user != 1:
                        await message.channel.send(f'<@{winner_user.id}> will be or is hosting **{winner_content}** this sunday.',allowed_mentions = discord.AllowedMentions(users=False))
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


    def log(self,logs:dict,message:discord.Message,with_guild = False):
        if message.author.id not in logs.keys():
            if with_guild:                     
                logs[message.author.id] = {'guild_id':message.guild.id}
            else:
                logs[message.author.id] = {}  
        if message.created_at not in logs[message.author.id].keys():
            logs[message.author.id][message.created_at]  = []
        logs[message.author.id][message.created_at].append(message.content)
