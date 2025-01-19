import disnake
from disnake.ext import commands

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description='Displays bot commands and usage information.')
    async def help(self, ctx):
        embed = disnake.Embed(title="Available bot commands:", color=disnake.Color.blurple())

        embed.add_field(name="`/setting`", value="Set a game to a specific role. (*for admin*)", inline=False)
        embed.add_field(name="`/list`", value="Display a list of games and their associated roles. (*for admin*)", inline=False)
        embed.add_field(name="`/remove`", value="Remove a game. (*for admin*)", inline=False)
        embed.add_field(name="`/resetidlist`", value="Reset the list of allowed channels. (*for admin*)", inline=False)
        embed.add_field(name="`/addchannel`", value="Add a channel ID to the list of allowed channels. (*for admin*)", inline=False)
        embed.add_field(name="`/top10`", value="Show the top 10 players by playing time for a specific game.", inline=False)
        embed.add_field(name="`/mystats`", value="Show your stats for all games.", inline=False)

        embed.set_footer(text="raffy.exe //     serg2")
        embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/1071866332569673858/a677b425cc3be6a96ebb1ad4de68d2c1.webp")

        embed1 = disnake.Embed(title="Important Note:", color=disnake.Color.red())
        embed1.add_field(name="Channel Restrictions:",
                        value="When you use the `/addchannel` command to set a channel ID, only the specified channel "
                            "will be able to use the `/top10` and `/mystats` commands.\n"
                            "In other channels, game roles will still be assigned or removed as usual.\n \n"
                            "`P.s.` We recommend setting a time limit for command usage in the channel where you use `/addchannel`, "
                            "to avoid unnecessary spam of role assignments.",
                        inline=False)

        embed1.add_field(name="The **`bot role`** should not be **`lower`** than the **`game role`**, "
                        "otherwise the role will not be assigned correctly.", value="", inline=False)

        embed1.set_image(url="https://cdn.discordapp.com/attachments/1135206657459228682/1135207921999953961/435c9242bfeb7dcb.png")

        await ctx.send(embed=embed, ephemeral=True)
        await ctx.send(embed=embed1, ephemeral=True)

def setup(bot):
    bot.add_cog(HelpCommand(bot))
