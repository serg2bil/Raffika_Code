import disnake
from disnake.ext import commands
from datetime import datetime, timezone, timedelta
from Logs.Variable import LOG_CHANNEL_ID

class LoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def log_to_channel(self, message):
        log_channel = self.bot.get_channel(LOG_CHANNEL_ID)
        if log_channel and log_channel.permissions_for(log_channel.guild.me).send_messages:
            now_utc = datetime.now(timezone.utc)
            timestamp = (now_utc + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S')
            await log_channel.send(f":information_source: [{timestamp}] {message}")

    @commands.Cog.listener()
    async def on_ready(self):
        await self.log_to_channel("Bot is now online and ready! :white_check_mark:")

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        error_message = args[0]
        await self.log_to_channel(f"An error occurred in event {event}: :warning:\n```\n{error_message}\n```")

def setup(bot):
    bot.add_cog(LoggingCog(bot))
