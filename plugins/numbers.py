import discord
import rethinkdb as r
from discord.ext import commands

beginnings = {'4056': 'normal', '0800': 'special'}

class Numbers:
    def __init__(self, bot):
        self.conn = bot.conn
        self.bot = bot

    @commands.command()
    async def wizard(self, ctx):
        if not ctx.author.permissions_in(ctx.channel).manage_guild:
            return await ctx.send(':x: Invalid permissions. You need Manage Server.')
        norm = [i for i in beginnings.keys() if beginnings[i] == 'normal']
        normstr = ', '.join(norm)
        await ctx.send(f':telephone_receiver: Welcome to CallBot. Type in your number below. Numbers must be 11 digits in length and start with one of the following: `{normstr}`.')
        msg = await self.bot.wait_for('message', check=lambda a: a.author == ctx.author and a.channel == ctx.channel)
        try:
            number = int(msg.content)
        except Exception:
            await ctx.send('Invalid number. Please try again.')
            return
        if len(str(number)) != 11:
            await ctx.send('Number needs to be 11 digits. Please try again.')
            return
        if str(number)[0:4] not in norm:
            await ctx.send(f'Numbers must begin with `{normstr}`. For other prefixes, contact ry00001#3487.')

        exists = (lambda: list(r.table('numbers').filter(
            lambda a: a['guild'] == str(ctx.guild.id)).run(self.conn)) != [])()

        nexists = (lambda: list(r.table('numbers').filter(lambda a: a['number'] == str(number)).run(self.conn)) != [])()
        
        if nexists:
            return await ctx.send(':x: This number is taken.')

        if exists:
            return await ctx.send(':x: This guild already has a number.')
        else:
            obj = {'guild': str(ctx.guild.id), 'number': str(number)}
            r.table('numbers').insert(obj).run(self.conn)

        await ctx.send(':ok_hand: Your number has been successfully registered! Thank you for using CallBot!')

def setup(bot):
    bot.add_cog(Numbers(bot))