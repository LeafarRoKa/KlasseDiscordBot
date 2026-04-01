import sys
sys.path.insert(0,r'C:\PythonPersonalProjects\DiscordBotProjects\KlasseBot')
from discord.ext import commands
from colorama import Fore
from shared_vars import Server_stats
from unittest.mock import AsyncMock, Mock
from event_listeners.basic_events import Basic_events
from message_events.message_events import Message_events
from message_events.message_management_cmds import Message_management
from user_management.user_management_cmds import User_management
from user_management.user_strikes_cmds import User_strikes
from user_cmds.fun_cmds import Fun_cmds
from user_cmds.useful_cmds import Basic_cmds
from suggestion_system.suggestion_cmds import Suggestion_cmds
from datetime import datetime, timedelta
from user_cmds.cmds_logic import can_do_daily
class Basic_tests():
    def __init__(self, client,server_stats):
        self.client = client
        self.server_stats = server_stats
        self.fun_cmds = Fun_cmds(client=client, server_stats=server_stats)
        #Load events
        self.basic_events = Basic_events(client=client,server_stats=server_stats)

        #Message_events
        self.message_events = Message_events(client=client,server_stats=server_stats)
        self.message_management = Message_management(client=client,server_stats=server_stats)

        #User_managemt
        self.user_management = User_management(client=client,server_stats=server_stats)
        self.user_strikes = User_strikes(client=client,server_stats=server_stats)
        
        #user_cmds
        self.fun_cmds = Fun_cmds(client=client,server_stats=server_stats)
        self.basic_cmds = Basic_cmds(client=client,server_stats=server_stats)
        
        #suggestion system
        self.suggestion_cmds = Suggestion_cmds(client=client,server_stats=server_stats)
        
        self.fun_cmds.server_stats = self.server_stats
        self.server_stats_data = Server_stats({"0": 
                                  {"set_up": True, 
                                   "roles_requirements": {"1": {"xp": 0, "strikes": 99}, "2": {"xp": 500, "strikes": 99}, "3": {"xp": 2500, "strikes": 50}, "4": {"xp": 5000, "strikes": 20}, "5": {"xp": 12500, "strikes": 10}},
                                    "roles_imgs": {"owner": "images/owner.png", "mod": "", "mini mod": "", "klassebot": "images/bot.png", "admin": "images/admin.png", "dev": "images/dev.png", "trial dev": "images/trial_dev.png", "elite member": "images/lite_member.png", "member": "images/member.png", "beginner": "images/beginner.png", "spammer": ""}, 
                                    "server_roles": {"1": "low", "2": "low_to_mid", "3": "mid", "4": "mid_to_high", "5": "high", "6": "mini_mod", "7": "mod", "8": "admin", "9": "owner"},
                                     "strikes": {"0": 0},
                                    "allowed_channels": {"admin": 1465322601198125066, "spam": 1483871754307895427, "bot": 1464956404837384233},
                                      "to_host": {}, 
                                     "suggestions_closed": False, "to_watch": {}, "winner_data": {}, 
                                     "winner": None, "winner_watch": None, "badges_imgs": {}, "winner_user": None, 
                                     "user_stats": 
                                     {"0": {"message_count": 36, "join_date": "27.01.2026", "xp": 0, 
                                            "badges": [], "rank": "high", "next_rank": "mini_mod", "img": "images/dev.png", 
                                            "xp_for_next_rank": "through votes of users with the rank member or higher", "time_redeemed": "2026-03-18 17:13:43.218036+00:00", 
                                            "role_before_spam": "low"}}}})
    async def run_tests(self):
        problems_list = []
        cmds_list = [getattr(self, cmd) for cmd in [func for func in dir(self) if func.startswith('test')]]
        for cmd in cmds_list:
            problems_list.extend(await cmd())
        if not problems_list:
            print(Fore.GREEN + 'All tests were successful.',end='')
            print(Fore.RESET)
            return True
        print(Fore.RED + f'The following errors occoured during testing:\n{problems_list}')
        print(Fore.RESET)
        return problems_list

    async def test_ping(self):
        expected_results = ['Pong!']#first all using reply then all using send.
        cmd_name = 'test_ping'
        ctx = AsyncMock()
        await self.fun_cmds.ping(self.fun_cmds,ctx)
        msg_responses = [msg.args[0] for msg in ctx.reply.call_args_list] + [msg.args[0] for msg in ctx.send.call_args_list]
        return [] if msg_responses == expected_results else [f'Cmd {cmd_name} did not return the extected result.\nRecieved result(s): {msg_responses}, the expected result were: {expected_results}\n']
    
    async def test_daily(self):
        cmd_name = 'daily_xp'
        expected_results =  [True,True,False,False]
        recieved_results = []
        can_do,_,__ =   can_do_daily(datetime(2005,3,4))
        recieved_results.append(can_do)
        can_do,_,__ =   can_do_daily(None)
        recieved_results.append(can_do)
        can_do,_,__ =  can_do_daily(datetime.now())
        recieved_results.append(can_do)
        can_do,_,__ =  can_do_daily(datetime.now()-timedelta(hours=23,minutes=59))
        recieved_results.append(can_do)
        return [] if recieved_results == expected_results else [f'Cmd {cmd_name} did not return the extected result.\nRecieved result(s): {recieved_results}, the expected result were: {expected_results}\n']
    
    async def test_question_responder(self):
        ctx = AsyncMock()
        expected_results = ['yes','no','maybe']#first all using reply then all using send.
        cmd_name = 'test_question_responder'
        await self.fun_cmds.question_responder(self.fun_cmds,ctx,'')
        msg_responses = [msg.args[0] for msg in ctx.reply.call_args_list] + [msg.args[0] for msg in ctx.send.call_args_list]
        return [] if any(msg in expected_results for msg in msg_responses) else [f'Cmd {cmd_name} did not return the extected result.\nRecieved result was: {msg_responses}, the result was expected to be in: {expected_results}\n']
    
    async def test_gen(self):
        cmd_name = 'test_gen'
        not_found_text = [f'This gen command does not exist.\nIf you want a list of all possible !gen commands enter !gen help.']
        problems = [f'Cmd {cmd_name} did not return the extected result.\nRecieved result had at least one code_name out of help that was not associated with existing code.\n']
        ctx = AsyncMock()
        await self.basic_cmds.gen(self.basic_cmds,ctx,'eafeafafaofjiosjfioasghfweaopifg30223r1-eafoeaihfpioeahfpeasi')#invalid code name
        msg_responses = [msg.args[0] for msg in ctx.reply.call_args_list] + [msg.args[0] for msg in ctx.send.call_args_list]
        ctx = AsyncMock()
        await self.basic_cmds.gen(self.basic_cmds,ctx)
        if [msg.args[0] for msg in ctx.reply.call_args_list] + [msg.args[0] for msg in ctx.send.call_args_list] != not_found_text:
            problems.append('The gen command did not return the not found text when recieving an obviously invalid code name.')
        ctx = AsyncMock()
        for code_name in msg_responses:
            await self.basic_cmds.gen(self.basic_cmds,ctx,code_name)
        return [] if all(code != not_found_text for code in msg_responses) else problems
    
    async def test_gen_del_edit(self): 
        ctx = AsyncMock()
        expected_results = ['You do not own this bot.']*2 #first all using reply then all using send.
        cmd_name = 'test_gen_del_edit'
        msg_responses = []
        ctx.author = Mock(id=0)
        ctx.bot = self.client
        try:
            await self.basic_cmds.gen_del.can_run(ctx)
        except commands.errors.NotOwner as e:
            msg_responses.append(e.args[0])
        try:
            await self.basic_cmds.gen_edit.can_run(ctx)
        except commands.errors.NotOwner as e:
            msg_responses.append(e.args[0])
        return [] if msg_responses == expected_results else [f'Cmd {cmd_name} did not return the extected result.\nRecieved result was: {msg_responses}, the result was expected to be: {expected_results}']
    
    async def test_stats(self): 
        return [] # TODO for later implement test_stats
    
    async def test_add_badge(self): 
        return [] # TODO implement for later

    async def test_add_set_remove_xp(self):
        ctx = AsyncMock()
        member = AsyncMock()
        member.id = 0 
        ctx.guild.id = 0
        member.guild.id = 0
        expected_results = [20,30,0] #first all using reply then all using send.
        msg_responses = []
        cmd_name = 'test_add_set_remove_xp'
        self.basic_cmds.server_stats = self.server_stats_data
        await self.user_management.set_xp(self.basic_cmds,ctx,member,20)
        msg_responses.append(self.basic_cmds.server_stats.stats[0]['user_stats'].stats[0]['xp'])
        await self.user_management.add_xp(self.basic_cmds,ctx,member,10)
        msg_responses.append(self.basic_cmds.server_stats.stats[0]['user_stats'].stats[0]['xp'])
        await self.user_management.remove_xp(self.basic_cmds,ctx,member,30)
        msg_responses.append(self.basic_cmds.server_stats.stats[0]['user_stats'].stats[0]['xp'])
        return [] if msg_responses == expected_results else [f'Cmd {cmd_name} did not return the extected result.\nRecieved result was: {msg_responses}, the result was expected to be in: {expected_results}']
    #TODO write all the other tests
        
    #add_badge          Adds a badge to the given user.
    #add_xp             Adds the given xp the given user.
    #give_all_roles     Gives everyone the given role.
    #give_role          Gives the user the given role.
    #remove_all_roles   Removes the given role from everyone.
    #remove_role        Removes the role from the given user.
    #self_timeout       Times out yourself.
    #set_xp             Sets a users_xp to a given amount.
    #timeout  

    #TODO these lines that are commented are all attributes of the ctx obj for daily to use for testing.
    #Shortcut to get a lot of cursors hold alt then hold ctrl on top of that and go down or up with the buttons
    #ctx.kwargs : {}
    #ctx.prefix : '!'
    #ctx.command : daily_xp
    #ctx.invoked_with : 'daily_xp'
    #ctx.invoked_parents : []
    #ctx.invoked_subcommand : None
    #ctx.subcommand_passed : None
    #ctx.command_failed : False
    #ctx.current_parameter : None
    #ctx.current_argument : None
    #ctx.interaction : None
    #... any number of arguments 
    