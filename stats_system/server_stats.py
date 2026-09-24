from __future__ import annotations#future has to be the first import else it will fail.
#this feature is only on by default in 3.14 this code was developed in 3.13
import json
from datetime import datetime,timedelta
import discord
from typing import TypedDict
from discord.ext import commands
import typing
import sys
from shared_vars import migrate_or_create
from utils.typing_utils import TEMP_LOGS_PATTERN,FULLS_LOGS_PATTERN,Initialized_Bot
from .user_stats import User_stats
from utils.utils import make_datetime
from user_management.user_management_logic import get_member

class Roles_requirement(TypedDict):
    xp: int
    strikes: int
    pos: int
    
class To_watch_structure(TypedDict):
    watch_date: datetime
    id: int

class Starting_day_structure(TypedDict):
    save_var: int
    user_day: str
    user_hour: int

    
class Quizzes_structure(TypedDict):
    frequency:str
    role_pinged:discord.Role
    question_channel:discord.TextChannel
    response: str
    question: str
    can_respond:bool
    question_response: dict[str,list[str]]
    starting_day: Starting_day_structure
    rewards: str

LOGS_STRUCTURE = dict[int,dict[str|datetime,int|list[str]]]


class Guild_dict_structure(TypedDict):
    set_up : bool
    user_stats: User_stats
    roles_imgs: dict[str,str]
    roles_requirements: dict[str,Roles_requirement]
    server_roles: dict[int,str] 
    strikes: dict[int,int]
    allowed_channels:list[int]#list of the channel id's originally was dict[str,int] the name as the key and the id beeing the value 
    #but it was changed bcs there can be multiple channels named the same and also the name can be looked up when the channel obj is created.
    suggestions_closed: bool
    to_watch: dict[str,To_watch_structure]
    quizzes: dict[str,Quizzes_structure]
    temp_logs: TEMP_LOGS_PATTERN
    full_logs: FULLS_LOGS_PATTERN#this could be easily saved in a var for not writing it 2 times but this improves 
    #readability in quick view
    badges_imgs:dict[str,str]#name of the badge and path to the img 
    remove_on_date: None | datetime


class Server_stats():
    stats: dict[int,Guild_dict_structure]#str only for test cases.
    client: commands.Bot | None
    
    def __init__(self,client:commands.Bot | dict[int,Guild_dict_structure]):
        """Creates a Server stats instance. For testing purposes the client can be replaced with a dictionary. In that case the data won't be pulled from the save file.

        Args:
            client (Initialized_Bot | dict): The discord bot or dict.
        """
        self.client = client if isinstance(client,commands.Bot) else None #client should always be a discord Bot unless if its for testing porpouses 
        self.stats = {} if isinstance(client, commands.Bot) else client
        # typing.cast(dict[int, Guild_dict_structure] | None,self.stats)
        # client: Initialized_Bot | None 
        if not isinstance(self.client,Initialized_Bot):
            return
        # client: Initialized_Bot

    async def setup(self):
        self.is_dict_complete()
        await self.open_stats()
        self.is_dict_complete()
        await self.save_stats()
    
    async def open_stats(self,crashed=False):
        porpouse = 'server_stats'
        path = f'data/{porpouse}.json'
        try:
            if not crashed:
                try:
                    with open(path) as f:
                        data = f.read()
                        new_path = f'{path[:-5]}.txt'
                        try:
                            with open(new_path,'w') as file:
                                file.write(data)
                        except FileNotFoundError:
                            with open(new_path,'x') as file:
                                file.write(data)
                except FileNotFoundError:
                    pass
            with open(path,'r') as f:
                stats = json.load(f) if self.stats.get(0) is None else self.stats
        except FileNotFoundError:
            migrate_or_create(porpouse)
            return await self.open_stats()
        except json.decoder.JSONDecodeError: 
            sys.exit(101)
        for guild_id in stats.keys():
            guild = self.client.get_guild(int(guild_id)) if isinstance(self.client, Initialized_Bot) else None
            if not guild and isinstance(self.client, Initialized_Bot):
                try:
                    guild = await self.client.fetch_guild(int(guild_id))
                except:
                    continue
            #CANNOT BE MOVED TO SHARED VARS! Bcs it creates the User_stats with self here.
            TEMPLATE:Guild_dict_structure = {'set_up':False,'user_stats':User_stats(self),'roles_requirements': {'1': {"xp": 0, "strikes": 99,'pos':1}, '2': {"xp": 500, "strikes": 99,'pos':2}, '3': {"xp": 2500, "strikes": 50,'pos':3},'4': {"xp": 5000, "strikes": 20,'pos':4}, '5': {"xp": 12500, "strikes": 10,'pos':5}},'roles_imgs':  {'owner': r'images/owner.png', 'mod':'','mini mod': '','klassebot': r'images/bot.png', 'admin': r"images/admin.png", 'dev': r"images/dev.png", 'trial dev': r"images/trial_dev.png", 'elite member': r'images/lite_member.png', 'member': r"images/member.png", 'beginner': r'images/beginner.png', 'spammer':''},'server_roles': {},'strikes':{},'allowed_channels':[],'suggestions_closed': True,'to_watch':{},'badges_imgs':{},'quizzes':{},'full_logs':{},'temp_logs':{},'remove_on_date':None}
            for k in TEMPLATE:
                if k not in stats[guild_id].keys():
                    stats[guild_id][k] = TEMPLATE[k]
            test_data = self.stats.get(0,{}).get('user_stats')

            stats[guild_id]['user_stats'] = User_stats(self,test_data) if isinstance(test_data,dict) else User_stats(server_stats=self,user_stats=typing.cast(dict,stats[guild_id]['user_stats']))#here it is not a user_stats object bcs it is saved as a dict but it should normally be user_stats 
            stats[guild_id]['user_stats'].stats =  stats[guild_id]['user_stats'].open_stats() 
            stats[guild_id]['server_roles'] = {int(k):v for k,v in stats[guild_id]['server_roles'].items()} 
            stats[guild_id]['allowed_channels'] = [ int(obj) for obj in stats[guild_id]['allowed_channels'].values()] if isinstance(stats[guild_id]['allowed_channels'],dict) else [int(i) for i in stats[guild_id]['allowed_channels']] #type:ignore[attr-defined] 
            stats[guild_id]['to_watch'] = {str(watch_name):typing.cast(To_watch_structure,{k:datetime.fromisoformat(v) if k == 'watch_date' and isinstance(v,str) else int(str(v)) for k,v in dict(watch_data).items() if k in ('id','watch_date')}) for watch_name,watch_data in stats[guild_id]['to_watch'].items()}
            stats[guild_id]['strikes'] = {int(k): int(v) for k,v in stats[guild_id]['strikes'].items()}
            stats[guild_id]['quizzes'] = {str(k) : 
                                          typing.cast(Quizzes_structure,{str(k2):guild.get_channel(int(str(v2))) if v2 and k2 in ['question_channel'] else guild.get_role(int(str(v2))) if k2 in ['role_pinged'] and v2 else v2 for k2,v2 in v.items() if guild}) for k,v in stats[guild_id]['quizzes'].items()} if guild else {
                                        str(k) : 
                                        typing.cast(Quizzes_structure,{str(k2):int(str(v2)) if v2 and k2 in ['question_channel'] else int(str(v2)) if k2 in ['role_pinged'] and v2 else v2 for k2,v2 in v.items()}) for k,v in stats[guild_id]['quizzes'].items()}#TODO this is technically false but i did do it like that to simplify it. Bcs this is only for testing check if it can be fixed.
                
            stats[guild_id]['roles_imgs'] = {'owner': r'images/owner.png', 'mod':'','mini mod': '','klassebot': r'images/bot.png', 'admin': r"images/admin.png", 'dev': r"images/dev.png",
                                              'trial dev': r"images/trial_dev.png", 'elite member': r'images/lite_member.png', 'member': r"images/member.png", 'beginner': r'images/beginner.png', 
                                              'spammer':''} if stats[guild_id].get('roles_imgs') is None else stats[guild_id].get('roles_imgs')

            stats[guild_id]['temp_logs'] = typing.cast(TEMP_LOGS_PATTERN,{int(k) : {datetime.fromisoformat(str(k2)) if k2 != 'guild_id' else typing.cast(typing.Literal['guild_id'],str(k2)) : typing.cast(list[str],v2) if k2 != 'guild_id' else int(str(v2))  for k2,v2 in v.items()}  for k,v in stats[guild_id]['temp_logs'].items()})
            stats[guild_id]['full_logs'] = {int(k) : {datetime.fromisoformat(str(k2)):v2 for k2,v2 in v.items()} for k,v in stats[guild_id]['full_logs'].items()}
            remove_on_date = stats[guild_id]['remove_on_date']
            stats[guild_id]['remove_on_date'] = remove_on_date if remove_on_date is None else datetime.fromisoformat(str(remove_on_date))
            if isinstance(remove_on_date,datetime):
                if remove_on_date.date() <= datetime.now().date():
                    stats.pop(guild_id)
        self.stats = {int(k):v for k,v in stats.items()}

    # def get_userdata(self,guild_id:int):
    #     if not self.stats:
    #         return
    #     return self.stats[guild_id]['user_stats']
    
    async def save_stats(self):
        if self.stats is None:
            return
        
        if self.stats.get(0) or self.stats.get('0'):#type:ignore bcs this is only for tests
                return
        
        to_save = {}
        for guild_id in self.stats.keys():
            if not any(guild_id ==guild.id for guild in typing.cast(Initialized_Bot,self.client).guilds):#this should intentionally fail when 
                #called in test cases to protect data 
                continue
            to_save[guild_id] = {k:v for k,v in self.stats[guild_id].items() if k != 'user_stats'}
            to_save[guild_id]['user_stats'] = self.stats[guild_id]['user_stats'].save_stats()
            to_save[guild_id]['to_watch'] = {k:{k2:str(v2) for k2,v2 in v.items()} for k,v in to_save[guild_id]['to_watch'].items()}
            # to_save[guild_id]['winner_data'] = {k:{k2:str(v2) for k2,v2 in v.items()} for k,v in to_save[guild_id]['winner_data'].items()}
            # to_save[guild_id]['quizzes'] = {k : {k2:v2 if k2 in ['role_pinged','question_channel'] and v2 else v2 for k2,v2 in v.items()} for k,v in to_save[guild_id]['quizzes'].items()}
            to_save[guild_id]['temp_logs'] = {k : {str(k2):v2 for k2,v2 in v.items()} if k != 'guild_id' else v for k,v in to_save[guild_id]['temp_logs'].items() }
            to_save[guild_id]['full_logs'] = {k : {str(k2):v2 for k2,v2 in v.items()} for k,v in to_save[guild_id]['full_logs'].items()}
        with open('data/server_stats.json','w') as f:
            json.dump(to_save,f)
        await self.open_stats()

    def strikes(self,guild:discord.Guild):
        return self.stats[guild.id]['strikes']

    def set_suggestion_status(self,guild,status:bool=True):
        self.stats[guild.id]['suggestions_closed'] = status

    async def winner_user(self,guild:discord.Guild):
        if self.stats[guild.id]['to_watch']:
            suggestion = list(self.stats[guild.id]['to_watch'])[0]
            user_id = self.stats[guild.id]['to_watch'][suggestion]['id']
            return await get_member(guild,user_id)
        return None

    async def winner_content(self,guild:discord.Guild):
        return None if await self.winner_user(guild) is None else list(self.stats[guild.id]['to_watch'].keys())[0]

    def add_guild(self,guild_id:int):
        if self.stats.get(guild_id,{}).get('remove_on_date') is None:
            raise ValueError('Cannot activate a guild that is not registered or was not removed.')
        self.stats[guild_id]['remove_on_date'] = None
        
    def guild_data(self,guild_id:int):
        return self.stats.get(guild_id)

    def remove_guild(self,guild_id:int):
        self.stats[guild_id]['remove_on_date'] = make_datetime(datetime.now().date() +timedelta(days=90))
        
    def is_dict_complete(self):
        TEMPLATE:Guild_dict_structure = {'set_up':False,'user_stats':User_stats(self),'roles_requirements': {'1': {"xp": 0, "strikes": 99,'pos':1}, '2': {"xp": 500, "strikes": 99,'pos':2}, '3': {"xp": 2500, "strikes": 50,'pos':3},'4': {"xp": 5000, "strikes": 20,'pos':4}, '5': {"xp": 12500, "strikes": 10,'pos':5}},'roles_imgs':  {'owner': r'images/owner.png', 'mod':'','mini mod': '','klassebot': r'images/bot.png', 'admin': r"images/admin.png", 'dev': r"images/dev.png", 'trial dev': r"images/trial_dev.png", 'elite member': r'images/lite_member.png', 'member': r"images/member.png", 'beginner': r'images/beginner.png', 'spammer':''},'server_roles': {},'strikes':{},'allowed_channels':[],'suggestions_closed': True,'to_watch':{},'badges_imgs':{},'quizzes':{},'full_logs':{},'temp_logs':{},'remove_on_date':None}
        #roles_requirements:dict[int,dict[str,int]]
        #stats_copy =  deepcopy(self.stats)
        if not self.client:
            return
        for guild in self.client.guilds:
            if guild.id not in self.stats.keys():
                self.stats[guild.id] = TEMPLATE
            for member in guild.members:
                if self.stats[guild.id]['strikes'].get(member.id) is None:
                    self.stats[guild.id]['strikes'][member.id] = 0
                if self.stats[guild.id]['set_up']:
                    if not self.stats[guild.id]['user_stats'].stats.get(member.id):
                        self.stats[guild.id]['user_stats'].add_member(member)
            #for k in TEMPLATE:
            #    if k not in self.stats[guild.id].keys():
            #        self.stats[guild.id][k] = TEMPLATE[k]

        #return stats_copy == self.stats


    def user_stats(self,guild:discord.Guild) -> User_stats:
        return self.stats[guild.id]['user_stats']
    