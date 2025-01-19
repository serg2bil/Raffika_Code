import os
import disnake
from disnake.ext import commands
from Logs.Token import TOKEN


bot = commands.Bot(command_prefix="!", intents=disnake.Intents.all())



# Load cogs
bot.load_extension('cogs.ServerList')
bot.load_extension('cogs.HelloCreator')
bot.load_extension('cogs.LoopStatus')
bot.load_extension('cogs.Ready')
bot.load_extension('cogs.HelpCommand')
bot.load_extension("cogs.LoggingErrors")
bot.load_extension("cogs.SergList")
bot.load_extension("cogs.SergRemove")
bot.load_extension("cogs.SergSetting")
bot.load_extension("cogs.SergAdminComands")
bot.load_extension("cogs.RoleGive")
bot.load_extension("cogs.TopList")



# Run the bot
bot.run(TOKEN)