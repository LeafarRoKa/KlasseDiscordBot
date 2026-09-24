from shared_vars import discord, DAYS, RESPOND_TO_QUIZ_CMD_NAME, REWARDS
from stats_system.server_stats import Server_stats,commands
from stats_system.user_stats import User_stats
from datetime import datetime, timezone, timedelta
from colorama import Fore
import asyncio
import random
import typing
from typing import overload
from utils.typing_utils import GuildContext,Initialized_Bot
from utils.utils import red_print
from message_events.message_management_logic import Response_waiting

def get_correct_input(user_input:str,*, prefixes:list = [], endings:list = []) -> tuple[bool|int,str|None]:
    correct_e = not endings
    correct_p = not prefixes
    correct = False
    method = None
    user_input = user_input.lower().strip()
    for ending in endings:
        if user_input.endswith(ending):
            user_input = user_input.removesuffix(ending).strip()
            correct_e = True
            method = ending
            break

    for prefix in prefixes:
        if user_input.startswith(prefix):
            user_input = user_input.removeprefix(prefix).strip()
            correct_p = True
            break

    if user_input.strip().isdigit():
        correct = int(user_input) if correct_e and correct_p else False
        
    return correct, method


def give_rewards(user_stats:User_stats, name:str, amount:int, member: discord.Member): 
    if name not in REWARDS:
        print(f'{Fore.RED}The given Reward is not in the rewards list.')
        print(Fore.RESET,end='')
        return
    func = getattr(user_stats,f'add_{name}',None)
    if not func:
        red_print('An error has occoured! file: quiz logics.py; folder: quiz_system; function: give_rewards; Error: False function was not caught before getting it with an attribute!')
        return
    func(member,amount)


async def is_role(id:int,guild:discord.Guild):
    role = guild.get_role(id)
    return False if not role else role

async def is_channel(id:int,guild:discord.Guild):
    channel = guild.get_channel(id)
    return False if not channel else channel

@overload
async def num_checking_input(
    prompt:str,
    response_waiter:Response_waiting, 
    ctx:GuildContext,
    *,
    accept_none:typing.Literal[False]=False, 
    accept_everything_or_everyone:typing.Literal[False]=False,
    lower_bound:int|None=None,upper_bound:int|None=None, 
    accept_point:bool= False, 
    accept_exit:typing.Literal[False]= False
    ) -> int: ... 


@overload
async def num_checking_input(
    prompt:str,
    response_waiter:Response_waiting, 
    ctx:GuildContext, 
    *,
    accept_none:bool, 
    accept_everything_or_everyone: bool=False,
    lower_bound:int|None=None,
    upper_bound:int|None=None, 
    accept_point:bool = False, 
    accept_exit:bool = False
    ) -> typing.Literal['none','everything','everyone','exit']|int: ... 

@overload
async def num_checking_input(
            prompt:str,response_waiter:Response_waiting, ctx:GuildContext, 
            *,accept_none:typing.Literal[False] = False, accept_everything_or_everyone:typing.Literal[False]= False,
            lower_bound:int|None=None,upper_bound:int|None=None, accept_point:bool=False, accept_exit:typing.Literal[True]
            ) -> typing.Literal['exit']|int: ... 

async def num_checking_input(prompt:str,response_waiter:Response_waiting, ctx:GuildContext, *, accept_none:bool= False, accept_everything_or_everyone:bool = False,lower_bound:int|None=None,upper_bound:int|None=None, accept_point:bool = False, accept_exit:bool= False):
    question_count = await response_waiter.send_and_response_waiting_text(prompt)
    if accept_point:
        question_count = question_count.strip('.')  
    if accept_none and question_count.lower() == 'none' or accept_everything_or_everyone and question_count.lower() in ['everything','everyone'] or accept_exit and question_count.lower() in ['exit']:
        return question_count
    if not question_count.isdigit() or lower_bound and int(question_count) < lower_bound or upper_bound and int(question_count) > upper_bound:
        await ctx.send(f'{question_count} is not a valid input.')
        return typing.cast(str|int,await num_checking_input(prompt, response_waiter, ctx,accept_none, accept_everything_or_everyone,lower_bound,upper_bound,accept_point,accept_exit))
    return int(question_count)

async def time_diff(day:str, response_waiter:Response_waiting, ctx:GuildContext, hour:int|None = None) -> tuple[int,str,int]:
    user_day,day_in_text = await get_day(day)
    if not user_day:
        raise ValueError('The given day was not a valid day')
    day_in_text = typing.cast(str,day_in_text)
    user_hour = await num_checking_input('At what hour would you like the quiz to happen (utc)?',response_waiter,ctx,lower_bound= 0, upper_bound= 23) if not hour else hour
    today = datetime.now(timezone.utc)
    this_day = today.weekday() + 1
    to_wait = user_day - this_day  if this_day < user_day else user_day - this_day if user_day == this_day and user_hour > today.hour else 7-this_day + user_day
    user_day  = today.replace(hour=0,minute=0,second=0,microsecond=0) + timedelta(days=to_wait,hours=user_hour)
    diff = (user_day-today).total_seconds()
    return int(diff), day_in_text, user_hour

async def get_day(day:str|int):
    day = str(day).strip()
    temp_day:int|None = DAYS.index(day)+1 if day in DAYS else int(day) if day.isdigit() and int(day) in range(1,7) else None
    if temp_day is None:
        return False, temp_day#it will never be zero bcs before it checks if its in range 1 to 7
    return temp_day, DAYS[temp_day-1]

class Quiz_logics():
    def __init__(self, response_waiter: Response_waiting, ctx: GuildContext, server_stats: Server_stats, client: Initialized_Bot):
        """Initialize the class with the Discord bot and the server stats. During the initialization adds a global check to the Discord bot.

        Args:
            client (Initialized_Bot): The Discord Bot.
            server_stats (Server_stats): The server stats.
        """
        self.response_waiter = response_waiter
        self.ctx = ctx
        self.server_stats = server_stats
        self.client = client
        
    @classmethod
    def better_setup(cls,ctx:GuildContext,server_stats: Server_stats,client:Initialized_Bot,quiz_name:str,time:int=30):
        response_waiter = Response_waiting(ctx,client,time)
        quiz_logics =  Quiz_logics(response_waiter,ctx,server_stats,client)
        change_functions = {1:{'func':quiz_logics.is_unique,'param':'What would you like to call this quiz?','save_var':''},2:{'func':quiz_logics.enter_frequency,'param':None,'save_var':''},3:{'func':quiz_logics.input_role,'param':'What role (enter the id) would you like to get pinged for this quiz? (None for no ping, Everyone to ping everyone.)','save_var':''},
                            4:{'func':quiz_logics.input_channel,'param':'In wich channel would you like the questions to be sent? (enter channelid)','save_var':''},5:{'func':response_waiter.send_and_response_waiting_bool,'param':'Would you like that people can respond to the question by using a bot cmd. (y,n)','save_var':''},
                            6:{'func':quiz_logics.question_asking,'param':None,'save_var':''},7:{'func':quiz_logics.ask_start_date,'param':'At what day of the week would you like the quiz to first start?','save_var':'','user_day':'','user_hour':''},8:{'func':quiz_logics.ask_reward,'param':'What reward would you like to give? Options are ' + ' '.join(option for option in REWARDS),'save_var':''}} 
        counter = iter(change_functions.keys())
        
        for k in server_stats.stats[quiz_logics.ctx.guild.id]['quizzes'][quiz_name]:
            num = next(counter) +1 
            if k in ['question','response']:
                break
            if num != 7:
                    change_functions[num]['save_var'] = server_stats.stats[ctx.guild.id]['quizzes'][quiz_name][k]
            else:
                    change_functions[num]['save_var'], change_functions[num]['user_day'], change_functions[num]['user_hour'] = server_stats.stats[ctx.guild.id]['quizzes'][quiz_name][k]['save_var'], server_stats.stats[ctx.guild.id]['quizzes'][quiz_name][k]['user_day'], server_stats.stats[ctx.guild.id]['quizzes'][quiz_name][k]['user_hour']
        change_functions[1]['save_var'] = quiz_name   
        quiz_logics.give_change_functions(change_functions)
        return quiz_logics

    def give_change_functions(self, change_functions:dict):
        self.change_functions = change_functions

    def better_quiz_desc(self):
            quiz_description = f'This quiz is called {self.change_functions[1]['save_var']}.\n'
            quiz_description += f'The quiz will first start next {self.change_functions[7]['user_day']} at {self.change_functions[7]['user_hour']} and will then occour every {self.change_functions[2]['save_var']}.\n'
            quiz_description += f'It will ping the role {self.change_functions[3]['save_var'].name}. ' if isinstance(self.change_functions[3]['save_var'], discord.Role) else 'It won\'t ping any role. '
            quiz_description += f'The members of this server ' 
            quiz_description += 'will' if self.change_functions[5]['save_var'] else 'won\'t'
            quiz_description +=' be able to respond to questions asked.\n'
            quiz_description += f'Questions will be sent in the channel {self.change_functions[4]['save_var']}.\n' #TODO add it so it is possible to return the channel in wich the questions are sent as #channel_name
            quiz_description += f'The questions and responses are {self.change_functions[6]['save_var']}.\n'
            quiz_description += f'The rewards given will be {self.change_functions[8]['save_var']}.\n'
            return quiz_description

    async def change_menu(self, name:str):
        change = await self.response_waiter.send_and_response_waiting_text('The options are the following: 1 quiz name, 2 frequency, 3 role pinged, 4 question channel, 5 if users can respond , 6 questions and responses, 7 starting day and time, 8 reward given\nWhat would you like to change (exit to exit)?')
        counter = iter(self.change_functions.keys())
        for k in self.server_stats.stats[self.ctx.guild.id]['quizzes'][name]:
            num = next(counter)+1
            if num != 7:
                    self.change_functions[num]['save_var'] = self.server_stats.stats[self.ctx.guild.id]['quizzes'][name][k]
            else:
                    self.change_functions[num]['save_var'], self.change_functions[num]['user_day'], self.change_functions[num]['user_hour'] = self.server_stats.stats[self.ctx.guild.id]['quizzes'][name][k]['save_var'], self.server_stats.stats[self.ctx.guild.id]['quizzes'][name][k]['user_day'], self.server_stats.stats[self.ctx.guild.id]['quizzes'][name][k]['user_hour']
        self.change_functions[1]['save_var'] = name          

        if len(change) == 1 and change.isdigit() and int(change) in self.change_functions.keys():
            num = int(change)
            if num == 7:
                self.change_functions[num]['save_var'], self.change_functions[num]['user_day'], self.change_functions[num]['user_hour'] = await self.change_functions[num]['func'](self.change_functions[num]['param']) if self.change_functions[num]['param'] is not None else await self.change_functions[num]['func']()
            elif num == 5:
                self.change_functions[6]['param'] = self.change_functions[5]['save_var']
            else:
                self.change_functions[num]['save_var'] = await self.change_functions[num]['func'](self.change_functions[num]['param']) if self.change_functions[num]['param'] is not None else await self.change_functions[num]['func']()
            if self.change_functions[num]['save_var'] is None:
                return await self.change_menu(name)
            if name != self.change_functions[1]['save_var']:
                    self.server_stats.stats[self.ctx.guild.id]['quizzes'].pop(name)
            await self.save_quizzes()
            await self.ctx.send(f'The updated quiz description is: {self.better_quiz_desc()}')
            return await self.change_menu(name)
        elif change == 'exit':
            return self.server_stats.stats[self.ctx.guild.id]['quizzes']
        else:
            await self.ctx.send('Invalid input.') 
            return await self.change_menu(name)
            
    async def save_quizzes(self):
        self.server_stats.stats[self.ctx.guild.id]['quizzes'][self.change_functions[1]['save_var']] = {'frequency':self.change_functions[2]['save_var'],'role_pinged':self.change_functions[3]['save_var'],'question_channel':self.change_functions[4]['save_var'],'can_respond':self.change_functions[5]['save_var'],'question_response':self.change_functions[6]['save_var'],'starting_day':{'save_var': self.change_functions[7]['save_var'], 'user_day':self.change_functions[7]['user_day'], 'user_hour':self.change_functions[7]['user_hour']},'rewards':self.change_functions[8]['save_var']}#type:ignore #FIXME
        if len(self.change_functions.keys()) != len(self.server_stats.stats[self.ctx.guild.id]['quizzes'][self.change_functions[1]['save_var']]) +1:
                print(f'{Fore.RED}The saved dictionary is not complete!')
                print(Fore.RESET)
        await self.server_stats.save_stats()
    
    async def ask_start_date(self, prompt:str):
        date = await self.response_waiter.send_and_response_waiting_text(prompt)
        time_difference, day_in_text, user_hour = await time_diff(date,self.response_waiter, self.ctx)
        if not type(time_difference) is int:
            await self.ctx.send(f'The day: {day_in_text} is not a valid day.\n Please ensure that the day is mentioned in this list: {DAYS}')
            return await self.ask_start_date(prompt)
        return time_difference, day_in_text, user_hour
    
    async def ask_reward(self,prompt):
        user_input = await self.response_waiter.send_and_response_waiting_text(prompt)
        correct, reward = get_correct_input(user_input,endings=REWARDS)
        if not correct:
            await self.ctx.send('The given input does not meet the requirement. Try again.')
            return await self.ask_reward(prompt)
        return f'{correct} {reward}'#just use .split() to separate and differenciate the reward from the amount 
        
#completed change the quiz_cmds file so that it only uses the functions from this file and then test if everything works

    async def question_asking(self,need_response:bool=True):
        question_and_response = {}
        question_count = await num_checking_input('How many questions would you like there to be?', self.response_waiter, self.ctx)
        for num in range(question_count):
            question  = await self.response_waiter.send_and_response_waiting_text(f'What would your {num+1}. question be?')
            if need_response:
                answer_amount = await num_checking_input('How many answers to this question would you like there to be?\nIf you would like that there is no clear response enter 0.',self.response_waiter, self.ctx)
                responses = []
                for i in range(answer_amount):
                    responses.append(await self.response_waiter.send_and_response_waiting_text(f'What would the {i+1}. response be to the question?'))
                question_and_response[question] = responses
        return question_and_response
    #completed add await to all response waiting and ctx.send
    
    async def input_role(self,prompt:str):
        response = await num_checking_input(prompt, self.response_waiter, self.ctx, accept_none=True,accept_everything_or_everyone=True)#completed find out how to mention everyone
        if isinstance(response,str):
            return '@everyone' if response.lower() in ['everything','everyone'] else ''
        
        
        role = await is_role(response,self.ctx.guild)
        if not role:
            await self.ctx.reply(f'There is no role in the server with the id {response}.')
            return await self.input_role(prompt)
        return role

    async def input_channel(self,prompt:str):
        response = await num_checking_input(prompt, self.response_waiter, self.ctx)
        channel = await is_channel(response,self.ctx.guild)
        if not channel:
            await self.ctx.reply(f'There is no channel in the server with the id {response}.')
            return await self.input_channel(prompt)
        return channel

    async def is_unique(self,prompt:str):
        quiz_name = await self.response_waiter.send_and_response_waiting_text('What would you like to call this quiz?')
        if quiz_name.lower() in self.server_stats.stats[self.ctx.guild.id]['quizzes'].keys():
            await self.ctx.send(f'A quiz called {quiz_name} already exists please choose a different name.')
            return await self.is_unique(prompt)
        return quiz_name

    async def enter_frequency(self):
        endings = ['hours','DAYS','weeks']
        often = await self.response_waiter.send_and_response_waiting_text('What would you like the quiz frequency to be?\n 1) every x hours 2) every x DAYS 3) every x weeks  Example input: every 3 DAYS')
        correct, ending = get_correct_input(often,prefixes=['every'],endings=endings)
        if not correct:
            await self.ctx.send(f'{often} is not a valid input.')
            return await self.enter_frequency()
        return f'{correct} {ending}'
        
        
    async def quiz_countdown(self, intervall:int = 240):
        if self.change_functions[7]['save_var'] - intervall < 0 or not intervall:
            intervall =  self.change_functions[7]['save_var']
        self.change_functions[7]['save_var'] -= intervall
        print(f'{self.change_functions[7]['save_var'] if self.change_functions[7]['save_var'] > intervall else intervall} seconds remaining for quiz {self.change_functions[1]['save_var']}')
        if intervall <= 0:
            return await self.quiz_execution(intervall)
        await asyncio.sleep(intervall)
        return await self.quiz_countdown(intervall)
            
    async def quiz_execution(self,intervall:int=5):
        question = random.choice(list(self.change_functions[6]['save_var'].keys()))
        response = self.change_functions[6]['save_var'][question]
        mentioned = self.change_functions[3]['save_var']
        quiz_name = self.change_functions[1]['save_var']
        quiz_data = self.server_stats.stats[self.ctx.guild.id]['quizzes'][quiz_name]
        if self.server_stats.stats[self.ctx.guild.id]['quizzes'].get('question') == question:
            await self.quiz_execution(intervall)
        self.server_stats.stats[self.ctx.guild.id]['quizzes'][quiz_name]['question'] = question
        self.server_stats.stats[self.ctx.guild.id]['quizzes'][quiz_name]['response'] = response
        to_send = f'Quiz **{quiz_name}**\n' 
        to_send += f'<@&{mentioned.id}>\n' if not type(mentioned) is str else f'@{mentioned}' if mentioned else ''
        to_send += f'```The question is: {question}\n'
        to_send += f'You can respond with your response using the bot command {RESPOND_TO_QUIZ_CMD_NAME} {quiz_name}' if self.change_functions[5]['save_var'] else ''
        to_send += '```'
        await self.change_functions[4]['save_var'].send(to_send)
        frequency = quiz_data['frequency']
        diff = (timedelta(**{frequency.split()[1]:int(frequency.split()[0])})).total_seconds()

        self.change_functions[7]['save_var'] = diff
        await self.quiz_countdown(intervall) 

def exitsts_with_questions(quiz_name:str, server_stats:Server_stats, ctx: GuildContext):
    if server_stats.stats[ctx.guild.id]['quizzes'].get(quiz_name) is None or server_stats.stats[ctx.guild.id]['quizzes'][quiz_name].get('question') is None:
        return f'There is no currently open quiz for responses.\nThe event will happen next {server_stats.stats[ctx.guild.id]['quizzes'][quiz_name]['starting_day']['user_day']} at {server_stats.stats[ctx.guild.id]['quizzes'][quiz_name]['starting_day']['user_hour']}' if server_stats.stats[ctx.guild.id]['quizzes'].get(quiz_name) is not None else 'This quiz does not currently exist.'
    return ''

def create_counter(num = 0):
     while True:
          yield num + 1
