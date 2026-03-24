import json
from datetime import datetime
import discord
from typing import TypedDict
from typing import Any as typing_any
import os
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

class User_stats():
    def __init__(self,guild:discord.Guild,server_stats,user_stats:dict =None):
        self.server_stats = server_stats
        if user_stats is None:
            self.stats = {}
        else:
            self.stats = user_stats
        self.stats = self.open_stats()
        self.server_stats : Server_stats
        #self.complete(guild)
        

    def open_stats(self):
        user_stats_copy = self.stats.copy()
        for key in user_stats_copy.keys():
            if self.stats[key].get('time_redeemed') is None:
                continue
            if isinstance(self.stats[key]['time_redeemed'],str):
                self.stats[key]['time_redeemed'] = datetime.fromisoformat(self.stats[key]['time_redeemed'])
        user_stats_copy = self.stats.copy()
        self.stats = {}
        for key,val in user_stats_copy.items():
            self.stats[int(key)] = val
        return self.stats
    
    def save_stats(self):
        for key in self.stats.keys():
            if self.stats[key].get('time_redeemed') is None:
                continue
            self.stats[key]['time_redeemed'] = str(self.stats[key]['time_redeemed'])
        return self.stats
    
    def update_rank(self, member:discord.Member,roles_list:list ):#May create conflicts with personlisation
        self = self.server_stats.stats[member.guild.id]['user_stats']
        roles_imgs = self.server_stats.stats[member.guild.id]['roles_imgs']
        roles_requirements = self.server_stats.stats[member.guild.id]['roles_requirements']
        if len(roles_list) == 9 and any(role.name.lower() == roles_list[9] for role in member.roles):
            rank = roles_list[9]
            next_rank = 'None' 
            img = roles_imgs['owner']
        elif any(role.name.lower().endswith('bot') for role in member.roles):
            rank = 'Bot'
            next_rank = 'None'
            img = roles_imgs['klassebot']
        elif len(roles_list) == 8 and any(role.name.lower() == roles_list[8] for role in member.roles):
            rank = roles_list[8]
            next_rank = f'Normally there is no greater rank beyond {roles_list[8]}.'
            img = roles_imgs['admin']
        elif len(roles_list) == 7 and any(role.name.lower() == roles_list[7] for role in member.roles):
            rank = roles_list[7]
            next_rank = roles_list[8]
            img = roles_imgs['mod']
        elif len(roles_list) == 6 and any(role.name.lower() == roles_list[6] for role in member.roles):
            rank = roles_list[6]
            next_rank = roles_list[7]
            img = roles_imgs['mini_mod']
        elif len(roles_list) == 5 and any(role.name.lower() == roles_list[5] for role in member.roles):
            rank = roles_list[5]
            next_rank =  roles_list[6]
            img = roles_imgs['dev']
        elif len(roles_list) == 4 and any(role.name.lower() == roles_list[4] for role in member.roles):
            rank = roles_list[4]
            next_rank = roles_list[5]
            img = roles_imgs['trial dev']
        elif len(roles_list) == 3 and any(role.name.lower() == roles_list[3] for role in member.roles):
            rank = roles_list[3]
            next_rank = roles_list[4]
            img = roles_imgs['trial member']
        elif len(roles_list) == 2 and any(role.name.lower() == roles_list[2] for role in member.roles):
            rank = roles_list[2]
            next_rank = roles_list[3]
            img = roles_imgs['member']
        elif any(role.name.lower() == 'spammer' for role in member.roles):
            rank = 'spammer'
            next_rank = 'Currently not avalible.'
            img = roles_imgs['spammer']
        else:
            rank = roles_list[1]
            next_rank = roles_list[2]
            img = roles_imgs['beginner']
        
        self.stats[member.id]['rank'] = rank
        self.stats[member.id]['next_rank'] = next_rank
        self.stats[member.id]['img'] = img
        rank = self.stats[member.id]['rank']
        try:
            self.stats[member.id]['xp_for_next_rank'] = roles_requirements[next((num for num,val in roles_list.items() if val == next_rank),None)]['xp'] - self.stats[member.id]['xp']#next only provides the next val of a generator obj. and None prevents errors when nothing is found
        except KeyError as e:
            print(e)
            promotion_path = 'None'
            if self.stats[member.id]['rank'].lower() == 'bot':
                promotion_path = 'Bots can\'t rank up.'
            elif len(roles_list) >= 6 and  next_rank == roles_list[6]:
                promotion_path = 'through votes of users with the rank member or higher'
            elif len(roles_list) >= 7 and  next_rank == roles_list[7] or len(roles_list) >= 7 and  next_rank == roles_list[7]:
                promotion_path = 'trough manual promotion.'
            elif next_rank.lower() == 'currently not avalible.':
                promotion_path = 'by loosing the role spammer'

            elif len(roles_list) >= 9 and rank == roles_list[9]:
                promotion_path = 'There is no greater rank beyond Owner'

            self.stats[member.id]['xp_for_next_rank'] = promotion_path
        self.save_stats()

    def add_member(self,member:discord.Member):
        self = self.server_stats.stats[member.guild.id]['user_stats']
        self.stats[member.id] = {'message_count': 0, 'join_date': member.joined_at.strftime('%d.%m.%Y'),'xp': 0, 'badges': []}
        self.update_rank(member,self.server_stats.stats[member.guild.id]['server_roles'])
        self.save_stats()

    def complete(self,guild:discord.Guild):
        if self.server_stats.client.get_guild(guild.id) is None:
            return
        for member in guild.members:
            if member.id not in self.stats.keys():
                self.server_stats.stats[member.guild.id]['user_stats'].add_member(member)
    
    def set_xp(self,member:discord.Member, amount:int):
        self.server_stats.stats[member.guild.id]['user_stats'].stats[member.id]['xp'] = amount
        
                    
    def add_msg(self, member:discord.Member,amount:int=1):
        
        self.server_stats.stats[member.guild.id]['user_stats'].stats[member.id]['xp'] += 5*amount
        self.server_stats.stats[member.guild.id]['user_stats'].stats[member.id]['message_count'] += amount
        self.server_stats.save_stats()
    
    def add_xp(self,member:discord.Member,amount:int=5):
        self.server_stats.stats[member.guild.id]['user_stats'].stats[member.id]['xp'] += amount


##class Guild_dict_structure(TypedDict):
#    user_stats: User_stats
#    roles_imgs: list[str]
#    roles_requirements: dict[int,dict]
#
class Server_stats():
    stats: dict[int,dict[str, dict]]
    def __init__(self,client):
        self.client = client
        self.stats = {}
        self.open_stats()
        self.is_dict_complete()
        self.save_stats()
        self.client: discord.Client

    def open_stats(self):
        try:
            porpouse = 'server_stats'
            with open('data/server_stats.json','r') as f:
                stats = json.load(f)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            migrate_or_create(porpouse)
            self.open_stats()
        for guild_id in stats.keys():
            stats[guild_id]['user_stats'] = User_stats(self.client.get_guild(guild_id),server_stats=self,user_stats=stats[guild_id]['user_stats'])
            stats[guild_id]['user_stats'].stats =  stats[guild_id]['user_stats'].open_stats()
            stats[guild_id]['server_roles'] = {int(k):v for k,v in stats[guild_id]['server_roles'].items()}
            stats[guild_id]['roles_requirements'] = {int(k):v for k,v in  stats[guild_id]['roles_requirements'].items()}
            stats[guild_id]['server_roles'] = {int(k):v for k,v in stats[guild_id]['server_roles'].items()}
            stats[guild_id]['allowed_channels'] = {k:int(v) for k,v in stats[guild_id]['allowed_channels'].items()}
            stats[guild_id]['to_watch'] = {watch_name:{k:datetime.fromisoformat(v) if k == 'watch_date' else int(v) for k,v in dict(watch_data).items()} for watch_name,watch_data in stats[guild_id]['to_watch'].items()}
            stats[guild_id]['strikes'] = {int(k): int(v) for k,v in stats[guild_id]['strikes'].items()}
            if stats.get(guild_id).get('roles_imgs') is None:
                stats[guild_id]['roles_imgs'] = {'owner': r'images/owner.png', 'mod':'','mini mod': '','klassebot': r'images/bot.png', 'admin': r"images/admin.png", 'dev': r"images/dev.png", 'trial dev': r"images/trial_dev.png", 'elite member': r'images/lite_member.png', 'member': r"images/member.png", 'beginner': r'images/beginner.png', 'spammer':''}
            else:
                stats[guild_id]['roles_imgs'] = stats.get(guild_id).get('roles_imgs')
            self.stats = {int(k):v for k,v in stats.items()}
        

    def save_stats(self):
        to_save = {}
        for guild_id in self.stats.keys():
            to_save[guild_id] = {k:v for k,v in self.stats[guild_id].items() if k != 'user_stats'}
            to_save[guild_id]['user_stats'] = self.stats[guild_id]['user_stats'].save_stats()
            to_save[guild_id]['to_watch'] = {k:{k2:str(v2) for k2,v2 in v.items()} for k,v in to_save[guild_id]['to_watch'].items()}
        with open('data/server_stats.json','w') as f:
            json.dump(to_save,f)
        self.open_stats()

    def strikes(self,guild:discord.Guild):
        return self.stats[guild.id]['strikes']

    def set_suggestion_status(self,guild,status:bool=True):
        self.stats[guild.id]['suggestions_closed'] = status

    def winner_user(self,guild:discord.Guild):
        if self.stats[guild.id]['winner_data']:
            user_id = list(self.stats[guild.id]['winner_data'].values())[0]
            return self.client.get_guild(user_id)
        return None

    def winner_content(self,guild:discord.Guild):
        return None if self.winner_user(guild) is None else list(self.stats[guild.id]['winnner_data'].keys())[0]
        

    def is_dict_complete(self):
        for guild in self.client.guilds:
            if guild.id not in self.stats.keys():
                self.stats[guild.id] = {'set_up':False,'user_stats':User_stats(guild,self),'roles_requirements': {"1": {"xp": 0, "strikes": 99},"2": {"xp": 500, "strikes": 99}, "3": {"xp": 2500, "strikes": 50}, "4": {"xp": 5000, "strikes": 20}, "5": {"xp": 12500, "strikes": 10}},'roles_imgs':  {'owner': r'images/owner.png', 'mod':'','mini mod': '','klassebot': r'images/bot.png', 'admin': r"images/admin.png", 'dev': r"images/dev.png", 'trial dev': r"images/trial_dev.png", 'elite member': r'images/lite_member.png', 'member': r"images/member.png", 'beginner': r'images/beginner.png', 'spammer':''},'server_roles': {},'strikes':{},'allowed_channels':{},'suggestions_closed': True,'to_watch':{},'winner_data':{},'winner': None,'winner_watch':None} 
            for member in guild.members:
                if self.stats[guild.id]['strikes'].get(member.id) is None:
                    self.stats[guild.id]['strikes'][member.id] = 0
            self.save_stats()
            

    def user_stats(self,guild:discord.Guild):
        return self.stats[guild.id]['user_stats']