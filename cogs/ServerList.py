import disnake
import random
from disnake.ext import commands
from Logs.Variable import ALLOWED_USERS

class ServerList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def servers(self, ctx):

        if ctx.author.id not in ALLOWED_USERS:
            await ctx.message.reply("Sorry, you don't have permission to use this command.", delete_after=45, mention_author=False)
            return

        for guild in self.bot.guilds:
            server_info = f"Server ID: {guild.id}\nMember Count: {guild.member_count}"

            # Generate a random color for the embed
            color = disnake.Color(random.randint(0, 0xFFFFFF))

            # Create a new embed for each server
            embed = disnake.Embed(color=color)
            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url) 
             
            embed.add_field(name=guild.name, value=server_info, inline=False)

            # Send the embed for each server
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(ServerList(bot))
