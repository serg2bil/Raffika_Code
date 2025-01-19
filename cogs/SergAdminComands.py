import disnake
import random
from disnake.ext import commands
import sys
from Data.GameList import Games
from Data.ServerData import server_data
from importlib import reload
import os 

current_directory = os.path.dirname(os.path.abspath(__file__))
relative_path = os.path.join(current_directory, "..", "Data", "GameList.py")

def get_game_options():
    

    unique_games = list(set(Games)) 

    game_options = [
        disnake.SelectOption(label=game, value=game)
        for game in unique_games
    ]
    return game_options


Admins = (565132950019112960, 1006510342463037556)

MAX_GAMES_FOR_VIP = 3
MAX_GAMES_FOR_NON_VIP = 1

def save_server_data():
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




class SergAdminComands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



    @commands.slash_command(name="remove_game", description="For bot creators only.")
    async def remove_game(ctx):
        author_id = ctx.author.id

        if author_id not in Admins:
            await ctx.send("For bot creators only", ephemeral=True)
            return

        unique_games = list(set(Games))

        options1 = [
            disnake.SelectOption(label=game1, value=game1) for game1 in unique_games
        ]

        select_menu1 = disnake.ui.Select(placeholder="Select a game to remove", options=options1, custom_id="remove_game:select")
        await ctx.send("Select a game to remove:", components=[select_menu1])




    @commands.slash_command(name="add_game", description="For bot creators only.")
    async def add_game(ctx, *, game_name: str):

        author_id = ctx.author.id

        if author_id not in Admins:
            embed = disnake.Embed(title="Unauthorized", description="If you need to add a missing game, contact the administrators of this server https://discord.gg/qTWfEGSGHz", color=disnake.Color.red())
            await ctx.send(embed=embed, ephemeral=True)
            return


        with open(relative_path, "r") as file:
            file_contents = file.read()

        exec(file_contents)

        if game_name:
            Games.append(game_name)



            embed = disnake.Embed(title=f"Game `{game_name}` added to the list.", color=disnake.Color.green())
            await ctx.send(embed=embed)
            with open(relative_path, "w") as file:
                file.write(f"Games = {Games}")        

    @commands.slash_command(name="vip", description="For bot creators only.")
    async def set_vip_status(ctx, server_id: str, is_vip: bool):

        author_id = ctx.author.id

        if author_id not in Admins:
            embed = disnake.Embed(title="Have not primission", description="This command is only available for bot creators.", color=disnake.Color.red())
            await ctx.send(embed=embed, ephemeral=True)
            return

        if len(server_id) > 19 or not server_id.isdigit():
            embed = disnake.Embed(title="Invalid Server ID", description="Please enter a valid numeric server ID.", color=disnake.Color.red())
            await ctx.send(embed=embed)
            return

        server_id = int(server_id)

        if server_id in server_data:
            prev_vip_status = server_data[server_id].get("is_vip", False)
            server_data[server_id]["is_vip"] = is_vip
            save_server_data()

            vip_status_str = "enabled" if is_vip else "disabled"
            embed = disnake.Embed(title="VIP Status Changed", description=f"VIP status for server `{server_id}` has been {vip_status_str}.", color=disnake.Color.green())
            await ctx.send(embed=embed)

            if not is_vip and prev_vip_status:
                # Server lost VIP status, remove excess games beyond the non-VIP limit
                non_vip_limit = MAX_GAMES_FOR_NON_VIP
                known_games = server_data[server_id]["KNOWN_GAMES"]
                
                if len(known_games) > non_vip_limit:
                    excess_games = list(known_games.keys())[non_vip_limit:]
                    for game in excess_games:
                        del known_games[game]

                    embed = disnake.Embed(title="Excess Games Removed", description=f"Removed {len(excess_games)} excess games from the server.", color=disnake.Color.orange())
                    await ctx.send(embed=embed)
                    save_server_data()

        else:
            embed = disnake.Embed(title="Server Not Found", description=f"Server with ID `{server_id}` not found in the database.", color=disnake.Color.red())
            await ctx.send(embed=embed)
            
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

        if custom_id == "remove_game:select":
            selected_game1 = inter.data["values"][0]

            if selected_game1 is not None:
                Games.remove(selected_game1)

                with open(relative_path, "w") as file:
                    file.write(f"Games = {Games}")

                embed = disnake.Embed(title=f"Game `{selected_game1}` removed from the list.", color=disnake.Color.red())
                await inter.response.send_message(ephemeral=True, embed=embed)
            else:
                embed = disnake.Embed(title=f"Game `{selected_game1}` not found in the list.", color=disnake.Color.red())
                await inter.response.send_message(ephemeral=True, embed=embed)






def setup(bot):
    bot.add_cog(SergAdminComands(bot))