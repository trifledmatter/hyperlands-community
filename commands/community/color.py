import discord
from discord import app_commands
from discord.ext import commands

from typing import List

from dtypes.collections.profile import find_profile_by_id, CommunityProfile, update_profile_by_id
from dtypes.collections.colors import find_color_by_name, ProfileColors, save as saveNewColor, get_colors, remove_color_by_name
from dtypes.roles import Role

class ProfileColor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="add_color", description="Add a color to the server!"
    )
    @app_commands.describe(
        name="color_name",
        value="color_value"
    )
    @app_commands.checks.has_any_role(
        Role.ADMINISTRATORS.to_int(), Role.FOUNDER.to_int()
    )
    async def add_color(self, interaction: discord.Interaction, name: str, value: str):
        # add the role to the server first and then add to db
        try:
            await interaction.guild.create_role(
                name=name, 
                color=discord.Color.from_str(value=value.lower().title()), 
                reason=f"This role was automatically created by {interaction.user.name}")
        except Exception as e:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title=f"Could not create role \"{name}\"",
                    description="An error occured while creating the role in the guild.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
        
        color: ProfileColors = {
            "name": name.lower().title(),
            "value": value,
            "author": interaction.user.id
        }

        saveNewColor(color)

        return await interaction.response.send_message(
                embed=discord.Embed(
                    title=f"Created color \"{name}\"",
                    description=f"{name} with value {value} was successfully created by {interaction.user.name}!",
                    color=discord.Color.green()
                ),
                ephemeral=True
            )
    
    @app_commands.command(
            name="remove_color", description="Remove a color from the server!"
    )
    @app_commands.describe(
        color_name="The color name you want to remove"
    )
    @app_commands.checks.has_any_role(
        Role.ADMINISTRATORS.to_int(), Role.FOUNDER.to_int()
    )
    async def remove_color(self, interaction: discord.Interaction, color_name: str):
        colors = [color["name"].lower() for color in get_colors()]

        if color_name.lower() not in colors:
            return await interaction.response.send_message(
                embed=
                    discord.Embed(
                        title="This isn't a valid color!",
                        color=discord.Color.red(),
                        description=f"In order to remove a color, you must provide a valid color. I couldn't recognize {color_name}"
                    ),
                    ephemeral=True
                )
        
        # remove from the guild as well
        # check if the color is in the list of colors
        colors: List[ProfileColors] = get_colors()
        
        found_color: bool = False
        for profile_color in colors:
            if found_color:
                # if we already found the color, just skip.
                continue

            found_color = color_name.lower() in profile_color.get("name").lower() # otherwise check if the color was found elsewhere            

        if not found_color:
            return await interaction.response.send_message(
                embed=
                    discord.Embed(
                        title="This isn't a valid color!",
                        color=discord.Color.red(),
                        description=f"In order to remove this color, you must provide a valid color. I couldn't recognize {color_name}"
                    )
                )
        
        # get the role name
        all_guild_roles = [role for role in interaction.guild.roles]
        selected_role: Role = None

        for role in all_guild_roles:
            if role.name.lower().title() == color_name.lower().title():
                selected_role = role

        await interaction.guild._remove_role(selected_role)
        
        remove_color_by_name(color_name.lower())

        return await interaction.response.send_message(
            embed=
                discord.Embed(
                    title=f"Removed {color_name}!",
                    color=discord.Color.green(),
                ),
                ephemeral=True
            )
        

    @app_commands.command(
        name="change_color", description="Change your profile color in the server!"
    )
    @app_commands.describe(
        color="Choose from a preset of colors!"
    )
    async def color(self, interaction: discord.Interaction, color: str):
        user: CommunityProfile = find_profile_by_id(str(interaction.user.id))

        if user is None:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="You don't have a profile!",
                    color=discord.Color.red(),
                    description="In order to change your color, your profile must be registered with me. An error likely occured which is preventing me from looking up your profile."
                ),
                ephemeral=True
            )
        

        # check if the color is in the list of colors
        colors: List[ProfileColors] = get_colors()
        
        found_color: bool = False
        for profile_color in colors:
            if found_color:
                # if we already found the color, just skip.
                continue

            found_color = color.lower() in profile_color.get("name").lower() # otherwise check if the color was found elsewhere            

        if not found_color:
            return await interaction.response.send_message(
                embed=
                    discord.Embed(
                        title="This isn't a valid color!",
                        color=discord.Color.red(),
                        description=f"In order to change your color, you must provide a valid color. I couldn't recognize {color}"
                    ),
                    ephemeral=True
                )
        
        # get the role name
        all_guild_roles = [role for role in interaction.guild.roles]
        selected_role: Role = None

        for role in all_guild_roles:
            if role.name.lower() in color.lower():
                selected_role = role

        await interaction.user.add_roles(selected_role, reason=f"Role automatically added by {interaction.user.name}")

        # if we find any other colors aside from the color they chose, remove it.
        all_user_roles = [role for role in interaction.user.roles]
        
        if update_profile_by_id(interaction.user.id, "color", color.lower()):
            for role in all_user_roles:
                for profile_color in colors:
                    if role.name.lower() == profile_color.get("name").lower() and role.name.lower() != color.lower():
                        await interaction.user.remove_roles(role, reason=f"Removed by {interaction.user.name} due to color change")

            return await interaction.response.send_message(
                embed=discord.Embed(
                    title=f"Updated {user.get("name")}'s profile",
                    color=discord.Color.blue(),
                )
                .add_field(name="Old Color", value=f"{user.get("color").lower()}")
                .add_field(name="New Color", value=f"{color}"),
                ephemeral=True
            )
        else:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title=f"Error updating {user.get("name")}'s profile",
                    color=discord.Color.blue(),
                    description="Something happened that stopped us from updating your profile!"
                )
                .add_field(name="Old Color", value=f"{user.get("color").lower()}")
                .add_field(name="New Color", value=f"{color}"),
                ephemeral=True
            )
    
    @color.autocomplete("color")
    async def color_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> List[app_commands.Choice]:
        colors: List[ProfileColors] = get_colors()
        if len(colors) > 0:
            return [
                app_commands.Choice(name=profile_color, value=profile_color)
                for profile_color in [color["name"] for color in colors]
                if current.lower() in profile_color
            ]
        
        return [
            app_commands.Choice(name="Could not find any colors!", value="Could not find any colors!")
        ]

async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(ProfileColor(bot))
