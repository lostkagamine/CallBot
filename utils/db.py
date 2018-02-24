import rethinkdb as r
import discord

def get_telech(conn, guild:discord.Guild):
    gtele = r.table('settings').filter(lambda a: str(guild.id) == a['guild']).run(conn)
    try:
        gtele = gtele.next()
    except r.net.DefaultCursorEmpty:
        return # THIS SHOULD NEVER, EVER, EVER HAPPEN
    return discord.utils.find(lambda c: str(c.id) == gtele['tele_channel'], guild.channels)
