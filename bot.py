# CALLBOT
# v1.0

# by ry00001

import rethinkdb as r
import discord
from discord.ext import commands
import json
import sys
import glob
import os
import time
import math

switchboard = {}

class CallBot(commands.Bot):
    def __init__(self, **kwargs):
        self.switchboard = {}
        self.settings = {
            'plugins': []
        }
        with open('./config.json') as f:
            self.config = json.load(f)
            self.owners = self.config.get('owner')
            self.prefix = self.config.get('prefix')
        super().__init__(command_prefix=commands.when_mentioned_or(*self.prefix), **kwargs)
        self.rethink()

    def is_owner_check(self,ctx):
        return ctx.author.id in self.owners

    def owner_id_check(self,_id):
        return _id in self.owners

    async def on_message(self, msg):
        if msg.author.bot:
            return
        if msg.guild.id in bot.switchboard.keys():
            guild = discord.utils.find(lambda g: g.id == bot.switchboard[msg.guild.id], bot.guilds)
            gtele = r.table('settings').filter(lambda a: str(guild.id) == a['guild']).run(self.conn)
            try:
                gtele = gtele.next()
            except r.net.DefaultCursorEmpty:
                return # THIS SHOULD NEVER, EVER, EVER HAPPEN
            gtelech = discord.utils.find(lambda c: str(c.id) == gtele['tele_channel'], guild.channels)
            await gtelech.send(f':telephone_receiver: **{str(msg.author)}**: {msg.content}')
        else:
            await self.process_commands(msg)


    def owner(self):
        return commands.check(self.is_owner_check)

    def rethink(self):
        print('Attempting to connect to RethinkDB')
        tables = ['settings', 'numbers']
        dbc = self.config.get('db')
        try:
            self.conn = r.connect(host=dbc['host'], port=dbc['port'], db=dbc['db'], user=dbc['username'], password=dbc['password'])
            dbl = r.db_list().run(self.conn)
            if dbc['db'] not in dbl:
                print('Creating DB...')
                r.db_create(dbc['db']).run(self.conn)
            tab = r.table_list().run(self.conn)
            for i in tables:
                if i not in tab:
                    print(f'Table {i} not found. Now creating...')
                    r.table_create(i).run(self.conn)
        except Exception as e:
            print(f'DB connection failed! Exiting...\nError details:\n{type(e).__name__}: {e}')
            sys.exit(1)
        print('Connected successfully.')

bot = CallBot()

@bot.event
async def on_ready():
    print(f'CallBot ready - logged in as {str(bot.user)} ({bot.user.id})')

@bot.command()
async def ping(ctx):
    before = time.monotonic()
    msg = await ctx.send(':arrows_counterclockwise: Pinging...')
    after = time.monotonic()
    ms = (before - after) * 1000
    await msg.edit(content=f'Pong. {-math.floor(ms)}ms')

@bot.owner()
@bot.command(aliases=['restart', 'die'])
async def reboot(ctx):
    await ctx.send(':arrows_counterclockwise: Bot restarting.')
    sys.exit(0)

@bot.owner()
@bot.command(name='eval')
async def _eval(ctx, *, code : str):
    try:
        res = eval(code)
    except Exception as e:
        return await ctx.send(f':x: Error\n{type(e).__name__}: {e}')
    await ctx.send(res)

for ext in os.listdir('plugins'):
    if ext.endswith('.py'):
        try:
            bot.load_extension(f'plugins.{ext[:-3]}')
            bot.settings['plugins'].append(f'plugins.{ext[:-3]}')
        except Exception as e:
            print(f'Failed to load plugin {ext[:-3]}. Error details:\n{type(e).__name__}: {e}')

bot.run(bot.config.get('token'))