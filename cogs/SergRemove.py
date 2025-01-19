import disnake
import random
from disnake.ext import commands
import os 
import sys

from Data.ServerData import server_data







class SergRemove(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.slash_command(name="remove", description="Remove a game. (for admin)")
    @commands.has_permissions(administrator=True)
    async def remove_game(self, ctx):
        server_id = ctx.guild.id

        if server_id not in server_data:
            server_data[server_id] = {
                "KNOWN_GAMES": {}
            }

        data = server_data[server_id]
        KNOWN_GAMES = data["KNOWN_GAMES"]

        game_options = [
            disnake.SelectOption(label=game, value=game)
            for game in KNOWN_GAMES.keys()
        ]

        if not game_options:
            
            await ctx.send(embed = disnake.Embed(title="list is empty.", description="", color=disnake.Color.red()), ephemeral=True)
            return

        select_game = disnake.ui.Select(placeholder="Select a game to remove...", options=game_options, custom_id="select_game:option")
        embed = disnake.Embed(title="Remove Game", description="Select a game from the list to remove.", color=disnake.Color.red())

        await ctx.send(embed=embed, components=[select_game], ephemeral=True)

    @commands.Cog.listener()
    async def on_dropdown(self, inter: disnake.MessageInteraction):
        server_id = inter.guild.id

        if server_id not in server_data:
            server_data[server_id] = {
                "is_vip": False,
                "KNOWN_GAMES": {}
            }

        data = server_data[server_id]
        is_vip = data["is_vip"]
        KNOWN_GAMES = data["KNOWN_GAMES"]
        custom_id = inter.data["custom_id"]

        if custom_id == "select_game:option":
            selected_game = inter.data["values"][0]
            KNOWN_GAMES = server_data[server_id]["KNOWN_GAMES"]

            if selected_game in KNOWN_GAMES:
                del KNOWN_GAMES[selected_game]
                embed = disnake.Embed(title=f"Game removed: `{selected_game}`",  color=disnake.Color.red())

                await inter.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = disnake.Embed(title=f"`{selected_game}` game not found in the list.", color=disnake.Color.red())

                await inter.response.send_message(embed=embed, ephemeral=True)


        self.save_server_data()

    def save_server_data(self):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        relative_path = os.path.join(current_directory, "..", "Data", "ServerData.py")



        with open(relative_path, "w") as file:
            file.write("server_data = {\n")
            for server_id, data in server_data.items():
                file.write(f"    {server_id}: {{\n")
                file.write(f"        'is_vip': {data.get('is_vip', False)},\n")
                file.write(f"        'id_list': {data.get('id_list', [])},\n")
                file.write("        'KNOWN_GAMES': {\n")
                for game, role_id in data["KNOWN_GAMES"].items():
                    file.write(f"            '{game}': {role_id},\n")
                file.write("        },\n")
                file.write("        'PLAYING_TIME': {\n")
                for (user_id, game_name), play_time_data in data.get('PLAYING_TIME', {}).items():
                    play_time, last_online = play_time_data["sum"], play_time_data["last_online"]
                    file.write(f"            ({user_id}, '{game_name}'): {{'sum': {play_time}, 'last_online': {last_online}}},\n")
                file.write("        },\n")
                file.write("    },\n")
            file.write("}")



user_selections = {}
MAX_GAMES_FOR_VIP = 3
MAX_GAMES_FOR_NON_VIP = 1


def setup(bot):
    bot.add_cog(SergRemove(bot))