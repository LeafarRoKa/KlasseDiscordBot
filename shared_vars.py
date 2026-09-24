import discord
import easyocr
import nudenet
import json
from datetime import datetime, date, timedelta, time,timezone
import os

def open_save_files():
    """This function checks if all required bot files exist. If a file doesn't exist it will create the file with an empty dict.
    """
    global code_dict
    porpouse = 'code'
    try:
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
        old_path = f'{file_type_name}.json'
        new_path = f'data/{file_type_name}.json'
        try:
            os.rename(old_path, new_path)
        except FileNotFoundError:
            with open(new_path, 'w') as f:
                json.dump({},f)

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
waiting_list = {}
text_detection_ai = easyocr.Reader(['en']) # loads AI into that obj
forbidden_words = []
days_until_sunday = (6 - date.today().weekday()) % 7
if days_until_sunday == 0:  # If today is Saturday, move to next week
    days_until_sunday = 7
next_sunday = datetime.combine(date.today()+ timedelta(days=days_until_sunday), time(16)) #16 is the time of the day that we watch
next_sunday = next_sunday.replace(tzinfo=timezone.utc)
permissions_per_role = {1:[discord.Permissions(view_channel=True,create_instant_invite=True,change_nickname=True, send_messages=True, create_polls=True,add_reactions=True,read_message_history=True,connect=True,use_application_commands=True,send_messages_in_threads=True,speak=True),"#2FE489F2"], 
                        2:[discord.Permissions(view_channel=True,create_expressions=True,create_instant_invite=True, change_nickname=True,send_messages=True,send_messages_in_threads=True,create_public_threads=True,embed_links=True,attach_files=True,add_reactions=True,use_external_emojis=True,use_external_stickers=True,read_message_history=True,send_tts_messages=True,send_voice_messages=True,use_soundboard=True,use_external_sounds=True,use_voice_activation=True,use_application_commands=True,use_embedded_activities=True),"#9b59b6"],
                        3:[discord.Permissions(view_channel=True,create_expressions=True,create_instant_invite=True,change_nickname=True,send_messages=True,send_messages_in_threads=True,create_public_threads=True,create_private_threads=True,embed_links=True,attach_files=True,add_reactions=True,use_external_emojis=True,use_external_stickers=True,read_message_history=True,send_tts_messages=True,send_voice_messages=True,connect=True,speak=True,stream=True,use_soundboard=True,use_external_sounds=True,use_voice_activation=True,use_application_commands=True,use_embedded_activities=True,use_external_apps=True), '#d261ff'],
                        4:[discord.Permissions(view_channel=True,create_expressions=True,create_instant_invite=True,change_nickname=True,send_messages_in_threads=True,send_messages=True, create_public_threads=True,create_private_threads=True,embed_links=True,attach_files=True,add_reactions=True,use_external_emojis=True,use_external_stickers=True,read_message_history=True,send_tts_messages=True,send_voice_messages=True,create_polls=True,connect=True,speak=True,stream=True,use_soundboard=True,use_external_sounds=True,use_voice_activation=True,use_application_commands=True,use_embedded_activities=True,use_external_apps=True),'#206694'],
                        5:[discord.Permissions(view_channel=True,create_expressions=True,manage_expressions=True,create_instant_invite=True,change_nickname=True,send_messages=True,send_messages_in_threads=True,create_private_threads=True,create_public_threads=True,embed_links=True,attach_files=True,add_reactions=True,use_external_emojis=True,use_external_stickers=True,read_message_history=True,send_tts_messages=True,send_voice_messages=True,create_polls=True,connect=True,speak=True,stream=True,use_soundboard=True,use_voice_activation=True,priority_speaker=True,use_application_commands=True,use_embedded_activities=True,use_external_apps=True,create_events=True),'#3498db'],
                        6:[discord.Permissions(view_channel=True,manage_roles=True,create_expressions=True,manage_expressions=True,view_audit_log=True,create_instant_invite=True,change_nickname=True,manage_nicknames=True,kick_members=True, moderate_members=True,send_messages=True,send_messages_in_threads=True,create_public_threads=True,create_private_threads=True,embed_links=True,attach_files=True,add_reactions=True,use_external_emojis=True,use_external_stickers=True,mention_everyone=True,manage_messages=True,manage_channels=True,manage_threads=True,read_message_history=True,send_tts_messages=True,send_voice_messages=True,create_polls=True,connect=True,speak=True,stream=True,use_soundboard=True,use_external_sounds=True,use_voice_activation=True,priority_speaker=True,mute_members=True,use_application_commands=True,use_embedded_activities=True,use_external_apps=True,create_events=True,manage_events=True),'#b65bda'],
                        7:[discord.Permissions(view_channel=True,manage_channels=True,manage_roles=True,create_expressions=True,manage_expressions=True,view_audit_log=True,create_instant_invite=True,change_nickname=True,manage_nicknames=True,kick_members=True,moderate_members=True,send_messages=True,send_messages_in_threads=True,create_private_threads=True,create_public_threads=True,embed_links=True,attach_files=True,add_reactions=True,use_external_emojis=True,use_external_stickers=True,mention_everyone=True,manage_messages=True,manage_threads=True,read_message_history=True,send_tts_messages=True,send_voice_messages=True,create_polls=True,connect=True,speak=True,stream=True,use_soundboard=True,use_external_sounds=True,use_voice_activation=True,priority_speaker=True,mute_members=True,deafen_members=True,move_members=True,use_application_commands=True,use_embedded_activities=True,use_external_apps=True,create_events=True,manage_events=True),'#a65cc3'],
                        8:[discord.Permissions(administrator=True),'#e90367'],                        
                        9:[discord.Permissions(administrator=True),'#b300ff']
                        }
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
ENDING_IMGS = ['png','jpeg','jpg']
ALLOWED_FILE_ENDINGS = ['txt']
def save_data(purpose:str, item):
    """Saves data to a JSON file. Will overwrite all the data in the existing file

    Args:
        purpose (str): 
            Is the start of the file path. It only gets .json added for the full path.
        item (Any):
            The data to write to the file.
            
    """
    with open(f'data/{purpose}.json', 'w') as f:
        json.dump(item,f)

JOKES = ['Can someone please shed more light on how my lamp got stolen?',
        'Why is she called llene? She stands on equal legs.',
        'What do you call a gazelle in a  lions territory? Denzel.']

MONTHS = {'01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'May', '06': 'Jun', '07': 'Jul', '08':  'Aug', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'}
is_user_spamming = {}#false in some files
DAYS = ['monday','tuesday','wendsday','thursday','friday','saturday','sunday']
RESPOND_TO_QUIZ_CMD_NAME = '!respond_to_quiz'
REWARDS = ['xp']
SIDEEYE_REACTIONS = ['trust me', 'trust me bro', '100%']
SKILLISSUE_REACTIONS = ['why doesnt','why doesn\'t','it doesn\'t work', 'it doesnt work','how do i', 'error','broken', 'i lost', 'i messed up']
IQ_REACTIONS = ['actually', 'you can just','instead do']
SUS_REACTIONS = ['hypothetically','dont ask why','for a friend','i have a girlfriend', 'i have a gf', 'i have a bf', 'i have a boyfriend',"i dont lose","i don’t lose","i never lose","i never miss","too easy","light work","i calculated it","i calculated that","we’ll see","well see","im built different","i knew that","obviously","trust me","trust me bro","it’s proven","its proven","they don’t want you to know","they dont want you to know",]
FIGHT_STARTING_REACTIONS = ['actually', 'technically','well', 'no, because']
ONE_WORD_AKWARD = ['ok', 'cool','hello','hi guys']
NPC_REACTIONS = ['good morning','im bored','how are you', 'whats up', 'what\'s up','anyone here']
OVERDRAMATIC_REACTIONS = ['“my code has one error','it’s over', 'its over', 'i’m done', 'im done','this is the end', 'i quit', 'i can’t anymore', 'i cant anymore', 'worst day ever', 'i’m finished', 'in finished', 'i am finished','why does this always happen to me','of course', 'just my luck','i’m cursed', 'im cursed', 'i am cursed',"that’s it","thats it","i’m done",'i’m leaving',"im leaving","goodbye forever","i’m done with this server","im done with this server","you won’t see me again","you wont see me again","this server fell off"]
ABSOLUTE_CINEMA_REACTIONS = ["you will regret this","remember this","this is your last warning","im done","watch what happens","you have no idea","mark my words","it begins","this changes everything","just wait","this isn’t over","this isnt over", "say that again","i’m built different","listen carefully",]
NOT_TO_USE = [ "die", "dead", "death", "suicide", "funeral", "grave","mother", "father", "mom", "dad", "grandmother", "grandfather","sister", "brother", "uncle", "aunt", "cousin", "pet","depression", "anxiety", "panic", "therapy", "suicidal","selfharm", "relapse","divorce", "abuse", "harassment", "assault","war", "accident", "hospital", "cancer"]
TEXT_DETECTION_CONFIDENCE_PERCENTAGE = 0.5
REQUIREMENTS_TEMPLATE = {1:{"xp": 0, "strikes": 99}, 2: {"xp": 500, "strikes": 99}, 3: {"xp": 2500, "strikes": 20}, 4: {"xp": 5000, "strikes": 10}, 5: {"xp": 12500, "strikes": 5},6:{'xp':0,'strikes':60},7:{'xp':0,'strikes':80},8:{'xp':0,'strikes':10000},9:{'xp':0,'strikes':9999999999999999999999999}}
