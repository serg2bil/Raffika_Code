import disnake
from disnake.ext import commands
from Logs.Variable import ALLOWED_USERS

class HelloCreator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hello(self, ctx):
        if ctx.author.id in ALLOWED_USERS:
            await ctx.send("Greetings, creator! ❤️")

def setup(bot):
    bot.add_cog(HelloCreator(bot))