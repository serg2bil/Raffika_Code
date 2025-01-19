import disnake
import random
from disnake.ext import commands
import sys
import os 
from Data.GameList import Games
from Data.ServerData import server_data


from importlib import reload



user_selections = {}
MAX_GAMES_FOR_VIP = 3
MAX_GAMES_FOR_NON_VIP = 1


def get_game_options():


    unique_games = list(set(Games)) 

    game_options = [
        disnake.SelectOption(label=game, value=game)
        for game in unique_games
    ]
    return game_options

class SergSetting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.slash_command(name="setting", description="Set a game to a specific role. (for admin)")
    @commands.has_permissions(administrator=True)
    async def test_dropdown(ctx):
        roles = ctx.guild.roles
        
        if ctx.guild.id in server_data:
            is_vip = server_data[ctx.guild.id].get("is_vip", False)
            known_games = server_data[ctx.guild.id].get("KNOWN_GAMES", {})
        else:
            is_vip = False
            known_games = {}
        if is_vip:
            max_games = MAX_GAMES_FOR_VIP
        else:
            max_games = MAX_GAMES_FOR_NON_VIP
        if len(known_games) >= max_games:
            await ctx.send("Sorry, you have reached the game limit for this server.", ephemeral=True)
            return
        
        
        embed = disnake.Embed(title="Bot Configuration", description="Select a role from the list below and then choose a game", color=disnake.Color.blue())
        button = disnake.ui.Button(style=disnake.ButtonStyle.primary, label="Add Role to Game", custom_id="add_role_to_game")
        
        select_games = disnake.ui.Select(placeholder="Select a game...", options=get_game_options(), custom_id="select_games:option")
        
        role_lists = [roles[i:i + 25] for i in range(0, len(roles), 25)]
        action_rows = []

        for index, role_list in enumerate(role_lists):
            custom_id = f"select_roles:option{index+1}"
            select_options = [
                disnake.SelectOption(label=role.name, value=str(role.id))
                for role in role_list if not role.is_default()
            ]
            select = disnake.ui.Select(placeholder="Выберите роли", options=select_options, custom_id=custom_id)
            action_row = disnake.ui.ActionRow(select)
            action_rows.append(action_row)

        await ctx.send(embed=embed, components=action_rows + [select_games, button], ephemeral=True)




        


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

        if custom_id == "select_roles:option1":
            selected_role_id = inter.data["values"][0]
            selected_role = disnake.utils.get(inter.guild.roles, id=int(selected_role_id))
            if selected_role:
                user_id = inter.user.id
                user_selections[user_id] = {"role": selected_role, "game": None}
                if not is_vip and len(KNOWN_GAMES) >= MAX_GAMES_FOR_NON_VIP:
                    await inter.response.send_message(
                    embed = disnake.Embed(title="Sorry, you have reached the game limit for this server.", color=disnake.Color.yellow())
                    , ephemeral=True
                )
                    del user_selections[user_id]
                    return

            embed = disnake.Embed(title=f"You selected role: `{selected_role.name}`", color=disnake.Color.green())

            await inter.response.send_message(ephemeral=True, embed=embed)
        
        elif custom_id == "select_roles:option2":
            selected_role_id = inter.data["values"][0]
            selected_role = disnake.utils.get(inter.guild.roles, id=int(selected_role_id))
            if selected_role:
                user_id = inter.user.id
                user_selections[user_id] = {"role": selected_role, "game": None}
                if not is_vip and len(KNOWN_GAMES) >= MAX_GAMES_FOR_NON_VIP:
                    await inter.response.send_message(
                    embed = disnake.Embed(title="Sorry, you have reached the game limit for this server.", color=disnake.Color.yellow())
                    , ephemeral=True
                )
                    del user_selections[user_id]
                    return

            embed = disnake.Embed(title=f"You selected role: `{selected_role.name}`", color=disnake.Color.green())

            await inter.response.send_message(ephemeral=True, embed=embed)

        elif custom_id == "select_games:option":
            selected_game2 = inter.data["values"][0]
            user_id = inter.user.id
            if user_id in user_selections:
                user_selections[user_id]["game"] = selected_game2
                if not is_vip and len(KNOWN_GAMES) >= MAX_GAMES_FOR_NON_VIP:
                    await inter.response.send_message(
                        
                    embed = disnake.Embed(title="Sorry, you have reached the game limit for this server.", color=disnake.Color.yellow())
                    , ephemeral=True
                )
                    del user_selections[user_id]
                    return

            embed = disnake.Embed(title=f"You selected game: `{selected_game2}`.", color=disnake.Color.green())

            await inter.response.send_message(ephemeral=True, embed=embed)


        self.save_server_data()
        
    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        server_id = inter.guild.id

        if server_id not in server_data:
            server_data[server_id] = {
                "is_vip": False,  # Default to False if 'is_vip' not set previously
                "KNOWN_GAMES": {}
            }

        data = server_data[server_id]
        is_vip = data["is_vip"]
        KNOWN_GAMES = data["KNOWN_GAMES"]

        if inter.data["custom_id"] == "add_role_to_game":
            user_id = inter.user.id

            if user_id in user_selections:
                selected_role = user_selections[user_id]["role"]
                selected_game2 = user_selections[user_id]["game"]

                if not selected_role or not selected_game2:
                    await inter.response.send_message(
                        embed = disnake.Embed(title="Please select both a role and a game before clicking the button.", color=disnake.Color.red())
                        , ephemeral=True
                    )
                    return

                if not is_vip and len(KNOWN_GAMES) >= MAX_GAMES_FOR_NON_VIP:
                    await inter.response.send_message(
                        embed = disnake.Embed(title="Sorry, you have reached the game limit for this server.", color=disnake.Color.yellow())
                        , ephemeral=True
                    )
                    del user_selections[user_id]
                    return

                if selected_game2 in KNOWN_GAMES:
                    await inter.response.send_message(
                        embed = disnake.Embed(title=f"The game `{selected_game2}` is already associated with a role.", color=disnake.Color.red())
                        , ephemeral=True
                    )
                    return

                KNOWN_GAMES[selected_game2] = int(selected_role.id)
                    

                embed = disnake.Embed(title=f"You added role `{selected_role.name}` to game `{selected_game2}`.", color=disnake.Color.green())
                await inter.response.send_message(embed=embed, ephemeral=True)
                
                del user_selections[user_id]

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









def setup(bot):
    bot.add_cog(SergSetting(bot))