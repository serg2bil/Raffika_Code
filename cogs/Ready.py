import disnake
from disnake.ext import commands
from Data.ServerData import server_data
import os 


class ReadyListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Logged in as')
        print(self.bot.user.id)
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        if guild.id in server_data:
            del server_data[guild.id]
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
    bot.add_cog(ReadyListener(bot))