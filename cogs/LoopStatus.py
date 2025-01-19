import disnake
import random
import asyncio
from disnake.ext import commands

# Define the 'statuses' list
statuses = [
    ("/help | {num_servers} servers", 900)
]

class StatusRotation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.loop.create_task(self.rotate_status())

    async def rotate_status(self):
        while not self.bot.is_closed():
            # Get a random status-duration tuple from the list
            status, duration = random.choice(statuses)

            # Replace {num_servers} with the actual number of servers the bot is in
            if "{num_servers}" in status:
                num_servers = len(self.bot.guilds)
                status = status.replace("{num_servers}", str(num_servers))

            # Set the bot's presence status
            presence = disnake.Activity(type=disnake.ActivityType.watching, name=status)
            await self.bot.change_presence(activity=presence)

            # Wait for the specified duration before changing the status again
            await asyncio.sleep(duration)

def setup(bot):
    bot.add_cog(StatusRotation(bot))