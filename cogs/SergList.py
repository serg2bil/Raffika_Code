import disnake
from disnake.ext import commands
from Data.ServerData import server_data  # Assuming server_data is correctly imported

class SergList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="list", description="Display a list of games and their associated roles. (for admin)")
    @commands.has_permissions(administrator=True)
    async def list_games(self, ctx):  # Added self as first argument to match class method
        server_id = ctx.guild.id

        # Ensure server_id exists in server_data
        if server_id not in server_data:
            server_data[server_id] = {
                "KNOWN_GAMES": {}
            }

        # Now server_id should exist in server_data, proceed to fetch data
        data = server_data[server_id]
        KNOWN_GAMES = data["KNOWN_GAMES"]

        embed = disnake.Embed(title="Role List:", color=disnake.Color.blue())
        embed1 = disnake.Embed(title="List is empty", color=disnake.Color.blue())

        for game, role_id in KNOWN_GAMES.items():
            role = ctx.guild.get_role(role_id)
            if role:
                embed.add_field(name=game, value=f"<@&{role.id}>", inline=False)
            else:
                embed.add_field(name=game, value="Role not found", inline=False)

        if len(embed.fields) > 0:
            await ctx.send(embed=embed, ephemeral=True)
        else:
            await ctx.send(embed=embed1, ephemeral=True)

def setup(bot):
    bot.add_cog(SergList(bot))
