import discord
from discord import app_commands
from discord.ext import commands
from typing import List

from datetime import datetime

from dtypes.collections.profile import find_profile_by_id, CommunityProfile


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="profile", description="View information about your profile!"
    )
    async def profile(self, interaction: discord.Interaction):
        user: CommunityProfile = find_profile_by_id(str(interaction.user.id))

        if user is None:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="You don't have a profile!",
                    color=discord.Color.red(),
                    description="An error occured, which is stopping us from fetching your profile!"
                )
            )

        return await interaction.response.send_message(
            embed=discord.Embed(
                title=f"{user.get("name")}'s profile",
                color=discord.Color.blue(),
            )
            .add_field(name="Nickname", value=f"{user.get("nickname")}")
            .add_field(name="Level", value=f"{user.get("level")}")
            .add_field(name="Color", value=f"{user.get("color")}")
        )
    
    

async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(Profile(bot))
