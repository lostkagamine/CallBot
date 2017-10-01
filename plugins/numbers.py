import discord
import rethinkdb as r
from discord.ext import commands

class Numbers:
    def __init__(self, bot):
        self.conn = bot.conn
        self.bot = bot

def setup(bot):
    bot.add_cog(Numbers(bot))