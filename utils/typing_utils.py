from __future__ import annotations
from discord.ext import commands
import typing
from datetime import datetime
import discord

if typing.TYPE_CHECKING:
    import discord

class GuildContext(commands.Context):
    guild: discord.Guild#type:ignore
    message: GuildMessage#type:ignore
    author: discord.Member#type:ignore
    channel: GuildMessageablee#type:ignore

class GuildMessage(discord.Message):
    guild: discord.Guild#type:ignore
    author: discord.Member#type:ignore
    channel:GuildMessageable#type:ignore

class GuildInteraction(discord.Interaction):
    guild: discord.Guild#type:ignore
    user: discord.Member#type:ignore
    channel:GuildMessageable#type:ignore

class Initialized_Bot(commands.Bot):
    user:discord.User#type:ignore

class GuildMessageable(discord.abc.Messageable):
    guild:discord.Guild
    name:str
    id:int




def enforce_guild_dec(func:typing.Callable):
    def param_editer(self,ctx:commands.Context | discord.Message,*args,**kwargs):
        ctx = enforce_guild(ctx)
        return func(self,ctx,*args,**kwargs)
    return param_editer

def funcs_enforce_guild_dec(func:typing.Callable):
    def param_editer(ctx:commands.Context | discord.Message,*args,**kwargs):
        ctx = enforce_guild(ctx)
        return func(ctx,*args,**kwargs)
    return param_editer

@typing.overload
def enforce_guild(ctx:commands.Context) -> GuildContext: ...

@typing.overload
def enforce_guild(ctx:discord.Message) -> GuildMessage: ...

def enforce_guild(ctx:commands.Context|discord.Message) -> GuildContext|GuildMessage:
    if ctx.guild is None:
        raise TypeError('The guild of the given ctx object cannot be None.')
    return typing.cast(GuildContext,ctx) if isinstance(ctx,commands.Context) else typing.cast(GuildMessage,ctx)


TEMP_LOGS_PATTERN = dict[int,dict[typing.Literal['guild_id']|datetime,int|list[str]]]
FULLS_LOGS_PATTERN = dict[int,dict[datetime,int|list[str]]]