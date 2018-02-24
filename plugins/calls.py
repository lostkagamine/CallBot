import rethinkdb as r
import discord 
from discord.ext import commands

from utils import db

class Calls:
    def __init__(self, bot):
        self.bot = bot
        self.conn = bot.conn

    async def on_message(self, msg):
        if msg.author.bot:
            return
        if msg.guild.id in self.bot.switchboard.keys():
            guild = discord.utils.find(lambda g: g.id == self.bot.switchboard[msg.guild.id], self.bot.guilds)
            gtelech = db.get_telech(self.conn, guild)
            if msg.content.startswith(tuple(self.bot.prefix)):
                return
            await gtelech.send(f':telephone_receiver: **{str(msg.author)}**: {msg.content}')

    @commands.command(aliases='hup')
    async def hangup(self, ctx):
        if ctx.guild.id in self.bot.switchboard.keys():
            ogid = self.bot.switchboard[ctx.guild.id]
            guild = discord.utils.find(lambda g: ogid == self.bot.switchboard[ctx.guild.id], self.bot.guilds)
            telech = db.get_telech(self.conn, guild)
            del self.bot.switchboard[ctx.guild.id]
            del self.bot.switchboard[guild.id]
            await telech.send(':telephone: The other end hung up.')
            await ctx.send(':telephone: You hung up.')
        else:
            await ctx.send('Damn son, you\'re not in a call!')

    @commands.command(aliases=['dial'])
    async def call(self, ctx, number : int = None):
        if number is None:
            return await ctx.send('Damn son, you forgot the number!')
        
        nexists = (lambda: list(r.table('numbers').filter(lambda a: a['number'] == str(number)).run(self.conn)) != [])()

        if not nexists:
            return await ctx.send(':x: This number doesn\'t exist.')
    
        guildid = r.table('numbers').filter(lambda a: a['number'] == str(number)).run(self.conn).next()['guild']
        guild = discord.utils.find(lambda g: str(g.id) == guildid, self.bot.guilds)
        gtele = r.table('settings').filter(lambda a: guildid == a['guild']).run(self.conn)
        if guild == ctx.guild:
            return await ctx.send(':x: Why call yourself?')
        try:
            gtele = gtele.next()
        except r.net.DefaultCursorEmpty:
            return await ctx.send(':x: This guild hasn\'t set up CallBot yet.')
        if 'tele_channel' not in gtele.keys():
            return await ctx.send(':x: This guild hasn\'t set up CallBot yet.')
        gtelech = discord.utils.find(lambda c: str(c.id) == gtele['tele_channel'], guild.channels)

        await ctx.send('Calling...')
        await gtelech.send(':telephone: Ring!\nType `pickup` to pick up or `hangup` to ignore.')
        msg = await self.bot.wait_for('message', check=lambda m: m.content in ['pickup', 'hangup'] and m.channel == gtelech)
        if msg.content == 'pickup':
            await ctx.send('Call has been picked up!!')
            await gtelech.send(':telephone: Call picked up.')
            self.bot.switchboard[ctx.guild.id] = gtelech.guild.id
            self.bot.switchboard[gtelech.guild.id] = ctx.guild.id
        elif msg.content == 'hangup':
            await ctx.send(':telephone: The other end hung up.')
            await gtelech.send(':telephone: Hung up.')
        


            

def setup(bot):
    bot.add_cog(Calls(bot))