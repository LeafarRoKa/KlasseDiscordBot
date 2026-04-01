from discord.ext import commands
import discord
from stats_system.server_stats import Server_stats,User_stats, migrate_or_create
import easyocr
import nudenet
import json
from datetime import datetime, date, timedelta, time,timezone
def open_save_files():
    global code_dict
    try:
        porpouse = 'code'
        with open(r'data/code.json', 'r') as f:
            code_dict = json.load(f)  
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        migrate_or_create(porpouse)
open_save_files()
waiting_confirmations = []
change_confirmations = []
command_prefix = '!'
admin_channel_name = 'admin'
event_title = 'Watch party'
event_description = 'watching one randomly selected suggestion.'
bot_channel_name = 'bot'
welcome_channel_name = 'welcome'
event_channel_name = 'events'
goodbye_channel_name = 'goodbye'
logs_temp = {}
waiting_list = {}
text_detection_ai = easyocr.Reader(['en']) # loads AI into that obj
forbidden_words = []
days_until_sunday = (6 - date.today().weekday()) % 7
if days_until_sunday == 0:  # If today is Saturday, move to next week
    days_until_sunday = 7
next_sunday = datetime.combine(date.today()+ timedelta(days=days_until_sunday), time(16)) #16 is the time of the day that we watch
next_sunday = next_sunday.replace(tzinfo=timezone.utc)
permissions_per_role = {1:[discord.Permissions(view_channel=True,create_instant_invite=True,change_nickname=True, send_messages=True, create_polls=True,add_reactions=True,read_message_history=True,connect=True,use_application_commands=True,send_messages_in_threads=True,speak=True),"#2FE489F2"], 2: [discord.Permissions(view_channel=True,create_expressions=True,create_instant_invite=True, change_nickname=True,send_messages=True,send_messages_in_threads=True,create_public_threads=True,embed_links=True,attach_files=True,add_reactions=True,use_external_emojis=True,use_external_stickers=True,read_message_history=True,send_tts_messages=True,send_voice_messages=True,use_soundboard=True,use_external_sounds=True,use_voice_activation=True,use_application_commands=True,use_embedded_activities=True),"#9b59b6"],3:[discord.Permissions(view_channel=True,create_expressions=True,create_instant_invite=True,change_nickname=True,send_messages=True,send_messages_in_threads=True,create_public_threads=True,create_private_threads=True,embed_links=True,attach_files=True,add_reactions=True,use_external_emojis=True,use_external_stickers=True,read_message_history=True,send_tts_messages=True,send_voice_messages=True,connect=True,speak=True,stream=True,use_soundboard=True,use_external_sounds=True,use_voice_activation=True,use_application_commands=True,use_embedded_activities=True,use_external_apps=True), '#d261ff'],
                        4:[discord.Permissions(view_channel=True,create_expressions=True,create_instant_invite=True,change_nickname=True,send_messages_in_threads=True,send_messages=True, create_public_threads=True,create_private_threads=True,embed_links=True,attach_files=True,add_reactions=True,use_external_emojis=True,use_external_stickers=True,read_message_history=True,send_tts_messages=True,send_voice_messages=True,create_polls=True,connect=True,speak=True,stream=True,use_soundboard=True,use_external_sounds=True,use_voice_activation=True,use_application_commands=True,use_embedded_activities=True,use_external_apps=True),'#206694'],
                        5: [discord.Permissions(view_channel=True,create_expressions=True,manage_expressions=True,create_instant_invite=True,change_nickname=True,send_messages=True,send_messages_in_threads=True,create_private_threads=True,create_public_threads=True,embed_links=True,attach_files=True,add_reactions=True,use_external_emojis=True,use_external_stickers=True,read_message_history=True,send_tts_messages=True,send_voice_messages=True,create_polls=True,connect=True,speak=True,stream=True,use_soundboard=True,use_voice_activation=True,priority_speaker=True,use_application_commands=True,use_embedded_activities=True,use_external_apps=True,create_events=True),'#3498db'],
                        6: [discord.Permissions(view_channel=True,manage_roles=True,create_expressions=True,manage_expressions=True,view_audit_log=True,create_instant_invite=True,change_nickname=True,manage_nicknames=True,kick_members=True, moderate_members=True,send_messages=True,send_messages_in_threads=True,create_public_threads=True,create_private_threads=True,embed_links=True,attach_files=True,add_reactions=True,use_external_emojis=True,use_external_stickers=True,mention_everyone=True,manage_messages=True,manage_channels=True,manage_threads=True,read_message_history=True,send_tts_messages=True,send_voice_messages=True,create_polls=True,connect=True,speak=True,stream=True,use_soundboard=True,use_external_sounds=True,use_voice_activation=True,priority_speaker=True,mute_members=True,use_application_commands=True,use_embedded_activities=True,use_external_apps=True,create_events=True,manage_events=True),'#b65bda'],
                        7:[discord.Permissions(view_channel=True,manage_channels=True,manage_roles=True,create_expressions=True,manage_expressions=True,view_audit_log=True,create_instant_invite=True,change_nickname=True,manage_nicknames=True,kick_members=True,moderate_members=True,send_messages=True,send_messages_in_threads=True,create_private_threads=True,create_public_threads=True,embed_links=True,attach_files=True,add_reactions=True,use_external_emojis=True,use_external_stickers=True,mention_everyone=True,manage_messages=True,manage_threads=True,read_message_history=True,send_tts_messages=True,send_voice_messages=True,create_polls=True,connect=True,speak=True,stream=True,use_soundboard=True,use_external_sounds=True,use_voice_activation=True,priority_speaker=True,mute_members=True,deafen_members=True,move_members=True,use_application_commands=True,use_embedded_activities=True,use_external_apps=True,create_events=True,manage_events=True),'#a65cc3'],
                        8:[discord.Permissions(administrator=True),'#e90367'],                        
                        9:[discord.Permissions(administrator=True),'#b300ff']}
with open(r'data/de.txt', 'r') as f:
    for word in set(f):
        forbidden_words.append(word.strip('\n'))

with open(r'data/en.txt', 'r') as f:
    for word in set(f):
        forbidden_words.append(word.strip('\n'))
headers = {
    "User-Agent": "Mozilla/5.0"
}
nudity_classification = nudenet.NudeDetector()
allowed_types_in_bytes= [b'\x89PNG',          # PNG
                         b'\xff\xd8\xff',     # JPEG
                         b'GIF87a',           # GIF
                         b'GIF89a',           # GIF
                         b'BM']               # BMP
ending_imgs = ['png','jpeg']
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
allowed_file_endings = ['txt']
def save_data(porpouse:str, item):
    with open(f'data/{porpouse}.json', 'w') as f:
        json.dump(item,f)
months = {'01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'May', '06': 'Jun', '07': 'Jul', '08':  'Aug', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'}
is_user_spamming = {}#false in some files