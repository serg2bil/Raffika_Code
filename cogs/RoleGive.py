import disnake
import random
import asyncio
import time
import os
from disnake.ext import commands
from Data.GameList import Games
from Data.ServerData import server_data


class RoleGive(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # Запуск проверки активности при запуске бота
        self.bot.loop.create_task(self.check_activity())

    async def check_activity(self):
        while not self.bot.is_closed():
            for guild in self.bot.guilds:
                await self.process_guild(guild)

            self.save_server_data()
            await asyncio.sleep(60)

    async def process_guild(self, guild):
        for member in guild.members:
            if member.bot:
                continue

            if member.activity and member.activity.type == disnake.ActivityType.playing:
                await self.handle_active_member(guild, member)
            else:
                await self.handle_inactive_member(guild, member)

    async def handle_active_member(self, guild, member):
        game_name = member.activity.name
        known_games = server_data.get(guild.id, {}).get("KNOWN_GAMES", {})

        if game_name in known_games:
            role_id = known_games[game_name]
            role = guild.get_role(role_id)

            if role and role not in member.roles:
                try:
                    await member.add_roles(role)
                    self.update_playing_time(guild.id, member.id, game_name, 0.0, int(time.time()))
                except disnake.errors.Forbidden as e:
                    print(f"Permission error while adding role: {e}")

    async def handle_inactive_member(self, guild, member):
        known_games = server_data.get(guild.id, {}).get("KNOWN_GAMES", {})

        for game_name, role_id in known_games.items():
            role = guild.get_role(role_id)
            if role and role in member.roles:
                try:
                    await member.remove_roles(role)
                    self.update_playing_time_on_exit(guild.id, member.id, game_name)
                except disnake.errors.Forbidden as e:
                    print(f"Permission error while removing role: {e}")

    def update_playing_time(self, server_id, user_id, game_name, play_time, last_online):
        server_data.setdefault(server_id, {
            'is_vip': False,
            'KNOWN_GAMES': {},
            'PLAYING_TIME': {},
            'id_list': []
        })

        server_data[server_id]['KNOWN_GAMES'].setdefault(game_name, None)

        if user_id not in server_data[server_id]['id_list']:
            server_data[server_id]['id_list'].append(user_id)

        playing_time = server_data[server_id]['PLAYING_TIME'].setdefault(
            (user_id, game_name),
            {'sum': 0.0, 'last_online': last_online}
        )
        playing_time['sum'] += play_time
        playing_time['last_online'] = last_online

    def update_playing_time_on_exit(self, server_id, user_id, game_name):
        current_time = int(time.time())
        play_time_data = server_data[server_id]['PLAYING_TIME'].get((user_id, game_name))

        if play_time_data:
            last_online = play_time_data['last_online']
            play_time_data['sum'] += current_time - last_online
            play_time_data['last_online'] = current_time

    def save_server_data(self):
        # Сохранение данных сервера в файл ServerData.py
        base_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_path, "..", "Data", "ServerData.py")

        with open(file_path, "w") as file:
            file.write("server_data = {\n")
            for server_id, data in server_data.items():
                file.write(f"    {server_id}: {{\n")
                file.write(f"        'is_vip': {data.get('is_vip', False)},\n")
                file.write(f"        'id_list': {data.get('id_list', [])},\n")
                file.write("        'KNOWN_GAMES': {\n")
                for game, role_id in data.get("KNOWN_GAMES", {}).items():
                    file.write(f"            '{game}': {role_id},\n")
                file.write("        },\n")
                file.write("        'PLAYING_TIME': {\n")
                for (user_id, game_name), play_time_data in data.get('PLAYING_TIME', {}).items():
                    file.write(f"            ({user_id}, '{game_name}'): {{'sum': {play_time_data['sum']}, 'last_online': {play_time_data['last_online']}}},\n")
                file.write("        },\n")
                file.write("    },\n")
            file.write("}\n")


def setup(bot):
    bot.add_cog(RoleGive(bot))
