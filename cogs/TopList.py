import disnake
import random
from disnake.ext import commands
import os 
import sys

from Data.GameList import Games
from Data.ServerData import server_data







class TopList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Top 10 command to show top players by playing time for a specific game
    @commands.slash_command(name="top10", description="Show the top 10 players by playing time for a specific game.")
    async def top10(ctx, game_name: str):
        server_id = ctx.guild.id
        data = server_data[server_id]
        is_vip = data["is_vip"]
        KNOWN_GAMES = data.get("KNOWN_GAMES", {})
        PLAYING_TIME = data.get("PLAYING_TIME", {})
        
        if server_id not in server_data:
            embed = disnake.Embed(title="Error", description="Server data not found. Please use this command in a server context.", color=disnake.Color.red())
            await ctx.send(embed=embed, ephemeral=True)
            return

        data = server_data[server_id]
        id_list = data.get("id_list", [])  # Get the 'id_list' for the server


        if ctx.channel.id not in id_list:
            embed = disnake.Embed(title="Sorry", description="This function is disabled on this channel.", color=disnake.Color.orange())
            await ctx.send(embed=embed, ephemeral=True)
            return



        if game_name not in KNOWN_GAMES:
            embed = disnake.Embed(title="Error", description=f"Game `{game_name}` is not in the list.", color=disnake.Color.red())
            await ctx.send(embed=embed, ephemeral=True)
            return

        # Fetch playing time data for the game from the PLAYING_TIME dictionary
        game_playing_time_data = {
            user_id: play_time_data['sum'] / 3600  # Convert seconds to minutes
            for (user_id, game), play_time_data in PLAYING_TIME.items() if game == game_name
        }

        # Sort users by playing time in descending order
        sorted_users = sorted(game_playing_time_data.items(), key=lambda x: x[1], reverse=True)

        # Get the top 10 users and their playing time
        top_10 = sorted_users[:10]

        if not top_10:
            embed = disnake.Embed(title="No Data", description="No playing time data found for this game.", color=disnake.Color.orange())
            await ctx.send(embed=embed, ephemeral=True)
            return

        # Prepare the result message
        embed = disnake.Embed(title=f"Top 10 Players for {game_name}", color=disnake.Color.green())
        for rank, (user_id, play_time) in enumerate(top_10, start=1):
            member = ctx.guild.get_member(user_id)
            if member:
                embed.add_field(name=f"{rank}. {member.display_name}", value=f"Playing Time: {play_time:.2f} hours", inline=False)
            else:
                embed.add_field(name=f"{rank}. User Not Found", value=f"Playing Time: {play_time:.2f} hours", inline=False)

        await ctx.send(embed=embed)

    # MyStats command to show user's own stats for all games
    @commands.slash_command(name="mystats", description="Show your stats for all games.")
    async def mystats(ctx):
        server_id = ctx.guild.id
        user_id = ctx.author.id
        data = server_data[server_id]
        is_vip = data["is_vip"]
        KNOWN_GAMES = data.get("KNOWN_GAMES", {})
        PLAYING_TIME = data.get("PLAYING_TIME", {})
        
        if server_id not in server_data:
            embed = disnake.Embed(title="Error", description="Server data not found. Please use this command in a server context.", color=disnake.Color.red())
            await ctx.send(embed=embed, ephemeral=True)
            return

        data = server_data[server_id]
        id_list = data.get("id_list", [])  # Get the 'id_list' for the server

        # Check if the current channel ID is in the allowed 'id_list' for this server
        if ctx.channel.id not in id_list:
            embed = disnake.Embed(title="Sorry", description="This function is disabled on this server.", color=disnake.Color.orange())
            await ctx.send(embed=embed, ephemeral=True)
            return



        # Prepare the result message
        embed = disnake.Embed(title=f"Your Stats for All Games", color=disnake.Color.blue())

        # Check if the user is currently playing any game from the list of known games
        has_stats = False
        for game_name in KNOWN_GAMES.keys():
            user_playing_time_data = PLAYING_TIME.get((user_id, game_name), None)
            if user_playing_time_data is not None:
                play_time = user_playing_time_data['sum'] / 3600  # Convert seconds to minutes
                embed.add_field(name=game_name, value=f"Playing Time: {play_time:.2f} hour", inline=False)
                has_stats = True

                # Calculate user's position in the top players' list for this game
                game_playing_time_data = {
                    uid: pdata.get('sum', 0) for (uid, gname), pdata in PLAYING_TIME.items() if gname == game_name
                }
                sorted_users = sorted(game_playing_time_data.items(), key=lambda x: x[1], reverse=True)
                user_position = next((i + 1 for i, (uid, _) in enumerate(sorted_users) if uid == user_id), None)
                if user_position:
                    embed.add_field(name="Your Position", value=f"{user_position} in top players list", inline=False)

        if not has_stats:
            embed = disnake.Embed(title="No Data", description="You are not currently playing any of games.", color=disnake.Color.orange())
            await ctx.send(embed=embed, ephemeral=True)
            return

        await ctx.send(embed=embed)

    # ResetIDList command to reset the 'id_list' to an empty list
    @commands.slash_command(name="resetidlist", description="Reset the list of allowed channels. (for admin).")
    @commands.has_permissions(administrator=True)
    async def reset_id_list(ctx):
        server_id = ctx.guild.id

        if server_id not in server_data:
            embed = disnake.Embed(title="Error", description="Server data not found. Please use this command in a server context.", color=disnake.Color.red())
            await ctx.send(embed=embed, ephemeral=True)
            return

        server_data[server_id]["id_list"] = []
        save_server_data()  # Save the updated data to the file

        embed = disnake.Embed(title="Reset Complete", description="The server's id_list has been reset to an empty list.", color=disnake.Color.green())
        await ctx.send(embed=embed, ephemeral=True)

    # New command to add a channel ID to the 'id_list' for a specific server
    @commands.slash_command(name="addchannel", description="Add a channel ID where users can view their activity. (for admin)")
    @commands.has_permissions(administrator=True)
    async def add_channel(ctx, channel_id: str):
        server_id = ctx.guild.id

        if server_id not in server_data:
            embed = disnake.Embed(title="Error", description="Server data not found. Please use this command in a server context.", color=disnake.Color.red())
            await ctx.send(embed=embed, ephemeral=True)
            return

        data = server_data[server_id]
        id_list = data.get("id_list", [])  # Initialize 'id_list' as an empty list if not present

        # Convert the channel ID from string to integer
        try:
            channel_id_int = int(channel_id)
        except ValueError:
            embed = disnake.Embed(title="Invalid Input", description="Invalid channel ID. Please enter a valid integer.", color=disnake.Color.red())
            await ctx.send(embed=embed, ephemeral=True)
            return

        # Check if the channel ID is already in the list
        if channel_id_int in id_list:
            embed = disnake.Embed(title="Duplicate Channel ID", description="The channel ID is already in the list.", color=disnake.Color.orange())
            await ctx.send(embed=embed, ephemeral=True)
            return

        id_list.append(channel_id_int)
        server_data[server_id]["id_list"] = id_list
        save_server_data()  # Save the updated data to the file

        embed = disnake.Embed(title="Channel ID Added", description=f"Channel ID {channel_id_int} has been added.", color=disnake.Color.green())
        await ctx.send(embed=embed, ephemeral=True)
        
        
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

def setup(bot):
    bot.add_cog(TopList(bot))

