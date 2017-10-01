import rethinkdb as r
from discord.ext import commands
import discord

settings = {'tele_channel': 'channel'}

class Settings:
    def __init__(self, bot):
        self.bot = bot
        self.conn = bot.conn

    def check_perm(self, ctx):
        return (ctx.author.permissions_in(ctx.channel).manage_guild) or ctx.author.id in self.bot.owner

    @commands.command(name='set', aliases=['settings', 'setup', 'setting'])
    async def _set(self, ctx, *args):
        settings_str = ', '.join(settings)
        if len(args) <= 0:
            return await ctx.send(':x: Please specify a value to set.')
        if not self.check_perm(ctx):
            return await ctx.send(':no_entry_sign: Invalid permissions.')
        thing_to_set = args[0]
        if thing_to_set not in settings.keys():
            return await ctx.send(f':x: Invalid value. Possible values are: `{settings_str}`')
        if not self.check_type(ctx, settings[thing_to_set], ' '.join(args[1:len(args)])):
            return await ctx.send(':x: This property is of type `{}`.'.format(settings[thing_to_set]))
        data = {'guild': str(ctx.guild.id)}
        setting = self.do_type(ctx, settings[thing_to_set], ' '.join(
            args[1:len(args)]).replace('"', "'"))
        if isinstance(setting, str):
            if setting.startswith('ERR'):
                stuff = setting.split('|')
                return await ctx.send(f':x: An error occurred. `{stuff[1]}`')
        data[thing_to_set] = setting
        exists = (lambda: list(r.table('settings').filter(
            lambda a: a['guild'] == str(ctx.guild.id)).run(self.conn)) != [])()
        if exists:
            r.table('settings').filter(lambda a: a['guild'] == str(
                ctx.guild.id)).update(data).run(self.conn)
        else:
            r.table('settings').insert(data, conflict='replace').run(self.conn)
        await ctx.send(':ok_hand:')

    @commands.command(aliases=['cfg'])
    async def view_config(self, ctx):
        exists = (lambda: list(r.table('settings').filter(
            lambda a: a['guild'] == str(ctx.guild.id)).run(self.conn)) != [])()
        if not exists:
            return await ctx.send(':x: This guild has no configuration.')
        meme = r.table('settings').filter(lambda a: a['guild'] == str(
            ctx.guild.id)).run(self.conn)
        meme = meme.next()
        await ctx.send(f'```{meme}```')

    @commands.command(aliases=['delcfg'])
    async def delete_config(self, ctx):
        if not self.check_perm(ctx):
            return await ctx.send(':no_entry_sign: Invalid permissions.')
        exists = (lambda: list(r.table('settings').filter(
            lambda a: a['guild'] == str(ctx.guild.id)).run(self.conn)) != [])()
        if not exists:
            return await ctx.send(':x: This guild has no configuration.')
        meme = r.table('settings').filter(lambda a: a['guild'] == str(
            ctx.guild.id)).delete().run(self.conn)
        await ctx.send(':ok_hand:')

    def check_type(self, ctx, thing, value):
        if thing == "channel":
            return hasattr(ctx.message, 'channel_mentions')
        elif thing == 'bool':
            return value.lower() in ['true', 'false']
        elif thing == ('rolelist'):
            try:
                shlex.split(value)
                return True
            except Exception:
                return False
        elif thing == 'role':
            if discord.utils.find(lambda a: a.name == value, ctx.guild.roles) is None:
                return False
            return True
        elif thing == 'string':
            return True

    def do_type(self, ctx, _type, value):
        print(value)
        if _type == "channel":
            return str(ctx.message.channel_mentions[0].id)
        elif _type == 'bool':
            if value.lower() in ['true', 'false']:
                return value.lower() == 'true'
        elif _type == 'rolelist':
            roles = self.do_list(ctx, value)
            if roles == False:
                return 'ERR|One or more roles not found. Make sure to use \' instead of ".'
            return [str(i.id) for i in roles]
        elif _type == 'role':
            role = discord.utils.find(lambda a: a.name == value, ctx.guild.roles)
            if role is None:
                return 'ERR|Role not found.'
            return str(role.id)
        elif _type == 'string':
            return value.strip('"').strip("'")

    def do_list(self, ctx, stuff):
        aaaa = shlex.split(stuff)
        roles = []
        for i in aaaa:
            role = discord.utils.find(lambda a: a.name == i, ctx.guild.roles)
            if role == None:
                return False
            roles.append(role)
        return roles


def setup(bot):
    bot.add_cog(Settings(bot))