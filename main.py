import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import difflib
import pytesseract
import platform
import asyncio
from unittest.mock import AsyncMock
from shared_vars import  command_prefix#TODO ask why it fixes to move the import before the import of the class Fun or Basic cmds
from message_events.message_management_logic import delete_message
from event_listeners.event_logics import wait_until_event
from quiz_system.quiz_logic import time_diff
from stats_system.server_stats import Server_stats, User_stats
from event_listeners.basic_events import Basic_events
from message_events.message_events import Message_events, Message_checks
from message_events.message_management_cmds import Message_management
from user_management.user_management_cmds import User_management
from user_management.user_strikes_cmds import User_strikes
from user_cmds.fun_cmds import Fun_cmds
from user_cmds.useful_cmds import Basic_cmds
from suggestion_system.suggestion_cmds import Suggestion_cmds
from tests.basic_test import Basic_tests
from quiz_system.quiz_cmds import Quiz_system
from quiz_system.quiz_logic import Quiz_logics
from server_management.server_management_cmds import Server_management
load_dotenv('data/.env') 

if platform.system().lower() == 'windows':
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
elif platform.system().lower() == 'linux':
    pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
client = commands.Bot(command_prefix= command_prefix, intents = intents)
token = os.getenv('TOKEN')
user_stats = User_stats
badges_imgs  = {}
server_stats = Server_stats(client)


                                                    ###################################################
                                                    #TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO#
                                                    #TODO      in file message_events_logic.py    TODO#
                                                    #TODO      change function spam punishenment  TODO#
                                                    #TODO       to server specific so it works    TODO#
                                                    #TODO             server wide                 TODO#
                                                    #TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO#
                                                    ###################################################

async def load_cogs():
    global basic_tests
    """
    This function loads and adds all the extensions to the bot.
    """
    #Load events
    basic_tests = Basic_tests(client=client,server_stats=server_stats)
    await basic_tests.setup()

    #basic tests    
    await client.add_cog(Basic_events(client=client,server_stats=server_stats))

    #Message_events
    await client.add_cog(Message_events(client=client,server_stats=server_stats))
    await client.add_cog(Message_management(client=client,server_stats=server_stats))

    #User_managemt
    await client.add_cog(User_management(client=client,server_stats=server_stats))
    await client.add_cog(User_strikes(client=client,server_stats=server_stats))
    
    #user_cmds
    await client.add_cog(Fun_cmds(client=client,server_stats=server_stats))
    await client.add_cog(Basic_cmds(client=client,server_stats=server_stats))
    
    #suggestion system
    await client.add_cog(Suggestion_cmds(client=client,server_stats=server_stats))

    #events system
    await client.add_cog(Quiz_system(client=client,server_stats=server_stats))

    #server management commands
    await client.add_cog(Server_management(client=client,server_stats=server_stats))

    #command checks
    Message_checks(client,server_stats)


def mismatch_message(user_command:str) -> str:
    """Compares a command name with all bot command names and returns the best matching one.

    If no command matches with at least a 40% similarity score,
    a message stating that the command is invalid is returned.

    Args:
        user_command (str): The command name that the user used and was not found.

    Returns:
        str: A string containing either the closest matching command name or a message stating that the command given is invalid.
    """
    best_match_percentage = -1
    for command in commands_list:
        match_perecentage = difflib.SequenceMatcher(a = user_command,b = command).ratio()
        if match_perecentage > best_match_percentage:
            best_match_percentage = match_perecentage
            best_matching_command = command
    if best_match_percentage < 0.4:
        return f'Unknown command.\nType !help to see all commands.'
    else:
        return f'Invalid command.\nDid you mean: {best_matching_command}?\nType !help to see all commands.'



@client.event
async def on_command_error(ctx:commands.Context, error:commands.CommandError) -> None:
    """This is the global error catcher. This function is only meant for discords api

    Args:
        ctx (commands.Context): The command that caused the event.
        error (discord.CommandError): The error that was raised during that command execution.

    Returns:
        None:
    """

    delete_user_msg = True
    print(type(error))
    print(error)
    if getattr(error, 'handled', False):#if it doesn't have the attribute it means it wasn't handled and will return the here defined default false so it won't return if it doesn't have the attribute and if it does it only is correct if set to True
        return
    if isinstance(error, commands.RoleNotFound):
        await ctx.reply('The role does not exist.',delete_after=5)
    elif isinstance(error, commands.MissingPermissions):
        await ctx.reply('You lack the permissions to execute this command.',delete_after=5)
    elif isinstance(error, commands.MemberNotFound):
        await ctx.reply('Member not found. Please ensure you mentioned a valid Member.',delete_after=5)
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.reply('I lack the permissions to execute this command. Please contact the bot owner if this behaviour is unexpected.',delete_after=5)
    elif isinstance(error, commands.BadArgument):
        await ctx.reply('Member not found. Please ensure you mentioned a valid Member.',delete_after=5)
    elif isinstance(error, discord.Forbidden):
        await ctx.reply('I am not capable of performing actions for members above or at my same rank.',delete_after=5)
    elif isinstance(error, commands.CommandNotFound):
        await ctx.reply(mismatch_message(str(ctx.invoked_with)),delete_after=5)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply('You are missing an argument.',delete_after=5)
    elif isinstance(error, commands.errors.NotOwner):
        await ctx.reply('Only the bot owner can use this cmd.', delete_after=5)
    elif isinstance(error,commands.errors.CheckFailure):
        if getattr(ctx,'set_up',True):
            delete_user_msg = False
            #await ctx.reply('You cannot use this command at the moment.' ,delete_after=5)
    else:
        await ctx.send('An error has occured while trying to execute this command.',delete_after=5)
    if delete_user_msg: 
        await delete_message(ctx.message,time=5)
    
@client.event
async def on_ready():
    """This function runs when the bot is ready and runs the nescessary setup including:
        - Loading and setting up the server stats
        - running tests
        - checking if the server stats are complete
        - recalculates the time needed for all upcoming quizzes and starts the countdown for each of them.
 
        This function is only meant for discords api.
    """
    global server_stats
    if getattr(client, 'set_up', False):
        return
    await server_stats.setup()
    #adds the other cogs to the main bot.
    await load_cogs()
    await basic_tests.run_tests()
    await server_stats.open_stats()
    server_stats.is_dict_complete()
    for guild_id in server_stats.stats.keys():
        for quiz_name in server_stats.stats[guild_id]['quizzes'].keys():
            ctx = AsyncMock()
            ctx.guild.id = guild_id
            #TODO start the countdown for all quizzes again and uptade there to_wait seconds on restart
            quiz_logics = Quiz_logics.better_setup(ctx,server_stats,client,quiz_name)
            server_stats.stats[guild_id]['quizzes'][quiz_name]['starting_day']['save_var'],_,_ = await time_diff(server_stats.stats[guild_id]['quizzes'][quiz_name]['starting_day']['user_day'],quiz_logics.response_waiter,ctx,server_stats.stats[guild_id]['quizzes'][quiz_name]['starting_day']['user_hour'])
            quiz_logics = Quiz_logics.better_setup(ctx,server_stats,client,quiz_name)
            asyncio.create_task(quiz_logics.quiz_countdown())
            print(f'Started countdown for quiz {quiz_name}')
    print(f'Logged in as bot {client}')
    client.set_up = True
    await wait_until_event(server_stats=server_stats,client=client)
commands_list = [cmd.name for cmd in client.commands]



client.run(token)
#TODO fix role images command
#completed testing system
#completed set the default of the gen command parameter to help
#completed LOAD ALL COGS and fix everything!
#completed have a setup dict that has all the server guild ids in it and if the id is in there of the using server then you cant use it until you have setup
#completed FIX STATS CARD OF OTHER RANKS          
#completed made the bot compatible server wide
#completed added question responder cmd
#completed added self_timout cmd with self choosable times up to 10000
#completed FIX ADD MSG XP
#completed added a help description to every cmd.
#completed made a class of server stats and user stats.
#completed fixed logs.
#completed add cmd aliases like 8ball for question_responder
#completed split code into multiple files
#completed to simplify the transition from a json to database and not changing everything put everything into a guild data json. Also build an automatic migration system for that
#completed create a setup command that sets up the entire envoirement that the bot needs and he only adds things if theyre not present
#completed make every data dict server specific
#completed fix logs displayed and file size
#complted make the bot customizable per server
#TODO add a report command and so every user can report someone else but they have
# a cooldown on how much they can report and they can give a reason and after like x amount of people 
#have reported that person then the admins will be noticed of that. The amount of people until the admins get noticed should depend of the amount of people in the server
#TODO change the gen command so that you can change it per server but you can toggle if you want to automaticly recieve new commands added be the owner and else you can add them through a cmd that lists all features not in your gen cmd
#TODO learn / commands
#TODO change the setup so that it allows for more customizability so you can choose the exact channels it uses for example you can choose the channels where error msgs are sent doesnt have to be admin
#TODO create an auto-setup command
#TODO respond with reactions
#completed rename question responder with an alias
#TODO Personalisation
#TODO change everything to database
#TODO add a discussion recommendation if no one speeks and only if he hasnt sent anything not answereed before
#TODO add a voting system for mini mod
#TODO fix link opener but when link is invalid
#completed remove migration system from stats opener
#TODO change 'admin' channel to logs channel
#TODO for more customizibility make the events toggable
#TODO make welcome goodbye and event channels also toggable
#TODO test if the bot doesnt crash when not having the required permissions in a server
#completed Learn complicated classes 
