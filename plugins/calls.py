import rethinkdb as r
import discord 
from discord.ext import commands

class Calls:
    def __init__(self, bot):
        self.bot = bot
        self.conn = bot.conn

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
            self.bot.switchboard[ctx.guild.id] = gtelech.guild.id
            self.bot.switchboard[gtelech.guild.id] = ctx.guild.id
        elif msg.content == 'hangup':
            await ctx.send(':telephone: The other end hanged up.')
        


            

def setup(bot):
    bot.add_cog(Calls(bot))