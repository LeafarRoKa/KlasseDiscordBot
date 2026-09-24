from __future__ import annotations #makes all typehints a str and doesn't evaluate it when it reaches it during creation of the classes/functions. 
#But if an external module or your any code tries to get the real typehinted object it will still raise a NameError.
from typing import TYPE_CHECKING, TypedDict, NotRequired,Literal
from datetime import datetime
import discord
from copy import deepcopy
import typing

if TYPE_CHECKING:
    from .server_stats import Server_stats

class User_stats_typed_dict(TypedDict):
    message_count: int
    join_date: str
    xp: int
    badges: list[str]
    time_redeemed: NotRequired[datetime]
    rank: str
    next_rank: str
    img: str
    xp_for_next_rank: int | str
    quizzes: dict[str,dict[Literal['response'],str|bool]]
    role_before_spam: typing.NotRequired[str]

# class User_stats_save_typed_dict(TypedDict):
#     message_count: int
#     join_date: datetime
#     xp: int
#     badges: list[str]
#     time_redeemed: str 
    
    
User_stats_stats_structure = dict[int,User_stats_typed_dict]
# User_stats_save_stats_structure = dict[int,User_stats_save_typed_dict]
class User_stats():
    stats: User_stats_stats_structure
    def __init__(self,server_stats:Server_stats,user_stats:User_stats_stats_structure = {}):
        """Creates a User Stats instance. If data is given it will save that data in the attribute stats. It will default to an empty dict if None is given.

        Args:
            server_stats (Server_stats): The server stats where the user stats will be saved.
            user_stats (User_stats_stats_structure): The stats dict to be turned into the Class object. Defaults to an empty dict.
        """
        self.server_stats = server_stats
        self.stats = user_stats
        self.stats = self.open_stats()
        self.server_stats : Server_stats
        

    def open_stats(self):
        user_stats_copy = self.stats.copy()
        for key in user_stats_copy.keys():
            time_redeemed = self.stats[key].get('time_redeemed')
            if time_redeemed is None:
                continue
            if isinstance(time_redeemed,str):
                self.stats[key]['time_redeemed'] = datetime.fromisoformat(str(time_redeemed))
        user_stats_copy = deepcopy(self.stats)
        self.stats = {}
        for key,val in user_stats_copy.items():
            self.stats[int(key)] = val
        return self.stats
    
    def save_stats(self):
        stats: dict = self.stats
        for key in stats.keys():
            time_redeemed = self.stats[key].get('time_redeemed')
            if time_redeemed is None:
                continue
            stats[key]['time_redeemed'] = str(time_redeemed)
        return stats
    
    def update_rank(self, member:discord.Member):#May create conflicts with personlisation
        # self = self.server_stats.stats[member.guild.id]['user_stats']
        rank = None
        roles_imgs = self.server_stats.stats[member.guild.id]['roles_imgs']
        roles_requirements = self.server_stats.stats[member.guild.id]['roles_requirements']
        roles_list = {v['pos']: name for name,v in  roles_requirements.items()}
        if len(roles_list) >= 9 and any(role.name.lower() == roles_list.get(9) for role in member.roles):
            rank = roles_list[9]
            next_rank = 'None' 
            img = roles_imgs[rank] if not roles_imgs.get(rank.lower()) else roles_imgs[rank]
        elif any(role.name.lower() == 'spammer' for role in member.roles):
            rank = 'spammer'
            next_rank = 'Currently not avalible.'
            img = roles_imgs['spammer']
        elif any(role.name.lower().endswith('bot') for role in member.roles):
            rank = 'Bot'
            next_rank = 'None'
            img = roles_imgs['klassebot'] if not roles_imgs.get(rank.lower()) else roles_imgs[rank]

        elif len(roles_list) >= 8 and any(role.name.lower() == roles_list.get(8) for role in member.roles):
            rank = roles_list[8]
            next_rank = f'Normally there is no greater rank beyond {roles_list[8]}.'
            img = roles_imgs['admin'] if not roles_imgs.get(rank.lower()) else roles_imgs[rank]
        else:
            for i in range(2,7,-1):
                if self.has_role(member,roles_list.get(i,'')):
                    rank = roles_list[i]
                    next_rank = roles_list[i+1]
                    img = roles_imgs[rank]  
                    break
            else: #else for if the user has no registred roles right now 
                rank = roles_list[1]
                next_rank = roles_list[2]
                img = roles_imgs[rank] #roles_imgs['beginner'] if not roles_imgs.get(rank) else roles_imgs[rank] pretty sure this is unnecessary

        self.stats[member.id]['rank'] = rank
        self.stats[member.id]['next_rank'] = next_rank
        self.stats[member.id]['img'] = img
        rank = self.stats[member.id]['rank']
        # try:
        role_num = next((num for num,val in roles_list.items() if val == next_rank),None)
        if role_num is None:
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
            return
        self.stats[member.id]['xp_for_next_rank'] = roles_requirements[rank]['xp'] - self.stats[member.id]['xp']#next only provides the next val of a generator obj. and None prevents errors when nothing is found

    def has_role(self,member:discord.Member,role_name:str) -> bool:
        return any(role_name.lower() == role.name.lower() for role in member.roles)
    
    def add_member(self,member:discord.Member):
        self = self.server_stats.stats[member.guild.id]['user_stats']
        joined_at = member.joined_at
        if joined_at is None:
            return
        self.stats[member.id] = {'message_count': 0, 'join_date': joined_at.strftime('%d.%m.%Y'),'xp': 0, 'badges': [],'rank':'','next_rank':'','img':'','xp_for_next_rank':0,'quizzes':{}}
        self.update_rank(member)

    def complete(self,guild:discord.Guild):
        if not self.server_stats.client:
            return
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
    
    def add_xp(self,member:discord.Member,amount:int=5):
        self.server_stats.stats[member.guild.id]['user_stats'].stats[member.id]['xp'] += amount

