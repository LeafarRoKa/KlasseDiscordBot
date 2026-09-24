import discord
from discord.ext import commands
from utils.typing_utils import GuildContext,Initialized_Bot,GuildInteraction
from shared_vars import waiting_confirmations,change_confirmations
import typing
from stats_system.server_stats import Server_stats
class Message_checks(commands.Cog):
    def __init__(self, client: Initialized_Bot, server_stats:Server_stats):
        """Initialize the class with the Discord bot and the server stats. During the initialization adds a global check to the Discord bot.

        Args:
            client (Initialized_Bot): The Discord Bot.
            server_stats (Server_stats): The server stats.
        """
        self.client = client
        self.server_stats = server_stats
        self.client.add_check(self.is_in_confirmation)
       

    def is_in_confirmation(self,ctx:commands.Context):
        if not ctx.guild:
            return False
        
        ctx = typing.cast(GuildContext,ctx)
        
        if ctx.guild.id == 0:
            return True
        
        if not self.server_stats.stats[ctx.guild.id]['set_up'] and ctx.message.content.strip() != '!setup':
            return False
        
        
        if ctx.author.id == self.client.user.id or  ctx.author.id in waiting_confirmations and ctx.author.id not in change_confirmations:
            return False
        
        allowed_channels = self.server_stats.stats[ctx.guild.id]['allowed_channels']        
        #checks if the message was sent in another channel and if thats true it checks if the bot was mentioned.
        if allowed_channels:
            if ctx.channel.id not in allowed_channels: #checks if the channel wich the message was sent in is allowed.
                if ctx.channel.name.lower() != 'admin':
                    return False
        return True

class Interaction_checks(commands.Cog):
    def __init__(self,client: Initialized_Bot, server_stats:Server_stats) -> None:
        self.client = client
        self.server_stats = server_stats
        self.client.tree.interaction_check = self.interaction_checks#this overides the function interaction_check in the client that every time gets called but bcs the original
        #funtion just returns true so it lets all interactions trough by default

    
    async def interaction_checks(self, interaction: discord.Interaction) -> bool:

        if not interaction.guild:
            return False
        
        interaction = typing.cast(GuildInteraction,interaction)
        
        if not self.server_stats.stats[interaction.guild.id]['set_up']:
            if not interaction.command or not interaction.command.name == 'setup':
                return False

        if interaction.user.id == self.client.user.id or interaction.user.id in waiting_confirmations and interaction.user.id not in change_confirmations:
            return False
        
        allowed_channels = self.server_stats.stats[interaction.guild.id]['allowed_channels']        
        #checks if the message was sent in another channel and if thats true it checks if the bot was mentioned.
        if allowed_channels:
            if interaction.channel.id not in allowed_channels: #checks if the channel wich the message was sent in is allowed.
                # if interaction.channel.name.lower() != 'admin':
                #     return False #trying to minimalize the use of preset channels for more customisabillity
                return False
        return True