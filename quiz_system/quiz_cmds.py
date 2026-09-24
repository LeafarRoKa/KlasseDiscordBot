from shared_vars import REWARDS
from stats_system.server_stats import Server_stats,commands
from stats_system.user_stats import User_stats
from message_events.message_management_logic import Response_waiting, send_and_response_waiting_text, send_and_response_waiting_bool
from quiz_system.quiz_logic import Quiz_logics, exitsts_with_questions, create_counter, num_checking_input, give_rewards
from user_management.user_management_logic import get_member
from utils.typing_utils import GuildContext, Initialized_Bot

class Quiz_system(commands.Cog):
    def __init__(self, client:Initialized_Bot,server_stats:Server_stats):
        """Initialize the class with the Discord bot and the server stats. Additionally creates an attributes for user responses.

        Args:
            client (Initialized_Bot): The Discord Bot.
            server_stats (Server_stats): The server stats.
        """
        self.client = client
        self.server_stats = server_stats
        self.responses = {}

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_events=True)
    async def create_quiz(self,ctx:GuildContext):
                        #where would you like the responses to be sent
        response_waiter = Response_waiting(ctx,self.client,300)

        #completed add await to all response waiting and ctx.send
        
        quiz_logics = Quiz_logics(response_waiter=response_waiter,ctx=ctx,server_stats=self.server_stats,client=self.client)
        
        change_functions = {1:{'func':quiz_logics.is_unique,'param':'What would you like to call this quiz?','save_var':''},2:{'func':quiz_logics.enter_frequency,'param':None,'save_var':''},3:{'func':quiz_logics.input_role,'param':'What role (enter the id) would you like to get pinged for this quiz? (None for no ping, Everyone to ping everyone.)','save_var':''},
                            4:{'func':quiz_logics.input_channel,'param':'In wich channel would you like the questions to be sent? (enter channelid)','save_var':''},5:{'func':response_waiter.send_and_response_waiting_bool,'param':'Would you like that people can respond to the question by using a bot cmd. (y,n)','save_var':''},
                            6:{'func':quiz_logics.question_asking,'param':None,'save_var':''},7:{'func':quiz_logics.ask_start_date,'param':'At what day of the week would you like the quiz to first start?','save_var':'','user_day':'','user_hour':''},8:{'func':quiz_logics.ask_reward,'param':'What reward would you like to give? Options are ' + ' '.join(option for option in REWARDS),'save_var':''}}
        
        quiz_logics.give_change_functions(change_functions=change_functions)

        for num in change_functions.keys():
             if num == 7:
                 change_functions[num]['save_var'], change_functions[num]['user_day'], change_functions[num]['user_hour'] = await change_functions[num]['func'](change_functions[num]['param']) if change_functions[num]['param'] is not None else await change_functions[num]['func']()
                 continue
             change_functions[num]['save_var'] = await change_functions[num]['func'](change_functions[num]['param']) if change_functions[num]['param'] is not None else await change_functions[num]['func']()
             if num == 5:
                change_functions[6]['param'] = change_functions[5]['save_var']
        
        quiz_description = quiz_logics.better_quiz_desc()
        response = await response_waiter.send_and_response_waiting_text(f'This is the final quiz description {quiz_description}\n If you want to change someting enter **change** else your quiz will be saved and start at the next date.')
            
        if response.lower() == 'change':
            await quiz_logics.save_quizzes()
            self.server_stats.stats[ctx.guild.id]['quizzes'] = await quiz_logics.change_menu(change_functions[1]['save_var'])
            
        await quiz_logics.save_quizzes()
        await quiz_logics.quiz_countdown()    
        

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_events=True)
    async def edit_quiz(self,ctx:GuildContext, quiz_name:str | None  = None):
        """Let a user edit a created quiz.

        Args:
            ctx (GuildContext): The command context.
            quiz_name (str | None, optional): The name of the quiz to edit. Defaults to None.
        """
        # if not quiz_name:
        #     ...#TODO make it ask the name if no or an invalid quiz name are given bcs else it would only work with "" if they have a name with a space   
        if not quiz_name in self.server_stats.stats[ctx.guild.id]['quizzes']:
            quiz_names = [name for name in self.server_stats.stats[ctx.guild.id]['quizzes'].keys()]
            await ctx.send(f'There is no existing current quiz called {quiz_name}. If you want to create a new quiz use quiz_setup.\nThe existing quizzes are {quiz_names}')
            return
        quiz_logics = Quiz_logics.better_setup(ctx,self.server_stats,self.client,quiz_name,time=300)
        quiz_logics : Quiz_logics
        await quiz_logics.save_quizzes()
        await quiz_logics.change_menu(quiz_name)
    
    @commands.command()
    @commands.guild_only()
    async def respond_to_quiz(self, ctx:GuildContext,quiz_name:str):
        """Let a user respond to the named quiz with their response.

        Args:
            ctx (GuildContext): The command context.
            quiz_name (str): The quiz they want to respond to.
        """
        is_missing = exitsts_with_questions(quiz_name=quiz_name,server_stats=self.server_stats,ctx=ctx)
        if is_missing:
            await ctx.reply(is_missing)
            return 
        response = await send_and_response_waiting_text(ctx, self.client,'What will your response be?',time=120)
        if not response:
            return
        set_response = self.server_stats.stats[ctx.guild.id]['quizzes'][quiz_name]['response'] 
        # if not self.server_stats.stats[ctx.guild.id]['user_stats'].stats[ctx.author.id].get('quizzes'):
        #     self.server_stats.stats[ctx.guild.id]['user_stats'].stats[ctx.author.id]['quizzes'] = {}
        if not self.server_stats.stats[ctx.guild.id]['user_stats'].stats[ctx.author.id]['quizzes'].get(quiz_name):
            self.server_stats.stats[ctx.guild.id]['user_stats'].stats[ctx.author.id]['quizzes'][quiz_name] = {} 
        self.server_stats.stats[ctx.guild.id]['user_stats'].stats[ctx.author.id]['quizzes'][quiz_name]['response'] = response if not set_response else any(response.lower() == given_response.lower() for given_response in set_response)
    
    @commands.command()
    @commands.has_permissions(manage_events=True)
    async def get_responses(self, ctx:GuildContext,quiz_name:str) -> list[tuple[str,int]] | None:
        """Sends all user responses to the named quiz.

        Args:
            ctx (GuildContext): The command context.
            quiz_name (str): The quiz name the user wants to respond to.

        Returns:
            list[list[str]] | None: Returns either a list in a list containing the user response with a number assigned to it and the user stats object or None if there are no responses.
        """
        is_missing = exitsts_with_questions(quiz_name=quiz_name,server_stats=self.server_stats,ctx=ctx)
        if is_missing:
            await ctx.reply(is_missing)
            return
        counter = create_counter()
        responses = [(f'{next(counter)}. {self.server_stats.stats[ctx.guild.id]['user_stats'].stats[user_id]['quizzes'][quiz_name]['response']}\n',user_id)
                     for user_id in self.server_stats.stats[ctx.guild.id]['user_stats'].stats 
                     if self.server_stats.stats[ctx.guild.id]['user_stats'].stats[user_id].get('quizzes') 
                     and self.server_stats.stats[ctx.guild.id]['user_stats'].stats[user_id]['quizzes'].get(quiz_name) 
                     and self.server_stats.stats[ctx.guild.id]['user_stats'].stats[user_id]['quizzes'][quiz_name].get('response')]
        self.responses[quiz_name] = responses
        response_text = ''.join(txt[0] for txt in responses) if not self.server_stats.stats[ctx.guild.id]['quizzes'][quiz_name]['response'] else f'Correct {sum(bool(correct[0].strip('\n ').split()[1].strip()) for correct in responses)*100/len(responses)}% False {(len(responses) - sum(bool(correct[0].strip('\n ').split()[1].strip()) for correct in responses))*100/len(responses)}%.'
        await ctx.reply(response_text)
        return responses
    
    @commands.command()
    @commands.has_permissions(manage_events=True)
    async def give_rewards(self, ctx:GuildContext,quiz_name:str):
        """Shows the responses with the get_responses function. Allows choosing which answers receive the reward by number if no clear answer was set, otherwise allows confirming that the correct answers receive it. 

        Args:
            ctx (GuildContext): The command context.
            quiz_name (str): The quiz name to give the rewards to the answers.

        Returns:
            None: Returns early if a process is cancelled or the reward giveaway is completed. 
        """
        responses =  await self.get_responses(ctx,quiz_name)
        if not responses:
            return
        user_stats = self.server_stats.user_stats(ctx.guild)
        user_stats : User_stats
        quiz_data = self.server_stats.stats[ctx.guild.id]['quizzes'][quiz_name]
        rewards = quiz_data['rewards']
        amount, name =  int(rewards.split()[0]), rewards.split()[1]
        response_waiter = Response_waiting(ctx,self.client,time=120)
        if responses[0][0].strip(' \n').endswith('True') or responses[0][0].strip(' \n').endswith('False'):
            response = await send_and_response_waiting_bool(ctx, self.client, 'Are you sure you want to give all of the users that have the correct answer the coresponding reward?(y,n)',time=120)
            if not response:
                if response == False:
                    await ctx.reply('The rewards givaway was successfully cancaled.')
                return
            for user_data in responses:
                member = await get_member(ctx.guild, user_data[1])
                if not member:
                    continue
                give_rewards(user_stats,name,amount,member)
            return 
        
        async def ask_num_until_exit(prompt:str):
            """A loop that asks a number until exists 

            Args:
                prompt (str): _description_

            Returns:
                _type_: _description_
            """
            num = await num_checking_input(prompt,response_waiter,ctx,accept_point=True,lower_bound=1, upper_bound=len(responses)+1,accept_exit=True)
            if num  == 'exit':
                return
            member = await get_member(ctx.guild, responses[num-1][1])
            if not member:
                return await ask_num_until_exit(prompt)
            give_rewards(user_stats,name,amount,member)
            return
        await ask_num_until_exit('What response should recieve a reward. (exit to exit)')

    @commands.command()
    @commands.is_owner()
    async def execute_quiz(self,ctx:GuildContext,name:str):
        if not name in self.server_stats.stats[ctx.guild.id]['quizzes']:
            await ctx.reply(f'The event {name} does not yet exist.\nPlease either use the command !create_quiz to create a new quiz or try again with another name.')
            return
        quiz_logics = Quiz_logics.better_setup(ctx,self.server_stats,self.client,name,time=300)
        quiz_logics : Quiz_logics
        await quiz_logics.quiz_execution(60)

    @commands.command()
    async def list_quizzes(self,ctx:GuildContext):
        """Sends a list of all existing quizzes. 

        Args:
            ctx (GuildContext): The commands context.
        """        
        leading = '\n*    '
        await ctx.reply(leading + leading.join(quiz_name for quiz_name in self.server_stats.stats[ctx.guild.id]['quizzes'].keys()))