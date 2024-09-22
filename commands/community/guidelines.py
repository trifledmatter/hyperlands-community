import discord
from discord import app_commands
from discord.ext import commands
from typing import List

from datetime import datetime

from dtypes.roles import Role

from dtypes.collections.rules import (
    Rules,
    find_rule_by_name,
    get_rules,
    remove_rule_by_name,
    save,
)


class Guidelines(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_rules_titles(self) -> List[str]:
        rules = get_rules()
        return [rule["name"] for rule in rules]
    
    @app_commands.command(
            name="rules", description="View all rules in the server!"
    )
    async def rules(self, interaction: discord.Interaction):
        rules: List[Rules] = get_rules()
        embed = discord.Embed(
            title="Community Rules",
            color=discord.Color.blue()
        )

        for rule in rules:
            embed.add_field(name=rule.get("title"), value=rule.get("description"), inline=True)
        
        if len(rules) > 0:
            return await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )
        
        return await interaction.response.send_message(
            embed=discord.Embed(
                title="Could not find any rules!",
                description="An error occured whilst fetching the server rules.",
                color=discord.Color.red()
            )
        )

    @app_commands.command(
        name="rule", description="Get information about a rule in the server!"
    )
    @app_commands.describe(rule_name="The name of the rule you want to know about")
    async def rule(self, interaction: discord.Interaction, rule_name: str):
        rule: Rules = find_rule_by_name(rule_name)
        if rule:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=rule["title"],
                    color=discord.Color.yellow(),
                    description=f"> {rule['description']}",
                ).set_author(name=f"Author: {rule['author']}").set_footer(text=f"Tags: {" ,".join(rule["tags"])}")
            )
        else:
            await interaction.response.send_message(
                f"Rule '{rule_name}' not found.", ephemeral=True
            )

    @rule.autocomplete("rule_name")
    async def rule_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> List[app_commands.Choice]:
        rules_titles = await self.get_rules_titles()
        if len(rules_titles) > 0:
            return [
                app_commands.Choice(name=rule_title, value=rule_title)
                for rule_title in rules_titles
                if current.lower() in rule_title.lower()
            ]
        
        return [
            app_commands.Choice(name="Could not find any rules!", value="Could not find any rules!")
        ]

    @app_commands.command(name="add_rule", description="Add a new rule to the server!")
    @app_commands.describe(
        name="What is the name of this rule?",
        title="What is the title for this rule?",
        description="Describe this rule to others.",
        tags="Space-separated list of tags.",
    )
    @app_commands.checks.has_any_role(
        Role.ADMINISTRATORS.to_int(), Role.FOUNDER.to_int()
    )
    async def add_rule(
        self,
        interaction: discord.Interaction,
        name: str,
        title: str,
        description: str,
        tags: str,
    ):
        name = name.replace(" ", "-").lower().strip()
        title = title.capitalize()
        tags = [tag.lower().replace(" ", "-").strip() for tag in tags.split(" ")]

        author = (
            (interaction.message.author.display_name or interaction.message.author.name)
            if interaction.message
            else (interaction.user.display_name or interaction.user.name)
        )
        timestamp = datetime.now()

        rule: Rules = {
            "name": name,
            "title": title,
            "author": author,
            "description": description,
            "tags": tags,
            "timestamp": timestamp,
        }

        save(rule)

        await interaction.response.send_message(
            embed=discord.Embed(
                title=f'Added rule: "{title}"',
                description=f'Rule "{title}" with identifier "{name}" is now available to the public.',
                color=discord.Color.green(),
            ),
            ephemeral=True,
        )

    @app_commands.command(
        name="delete_rule", description="Remove a rule from the server."
    )
    @app_commands.describe(
        name="Provide the name / identifier of the rule you want to remove"
    )
    @app_commands.checks.has_any_role(
        Role.ADMINISTRATORS.to_int(), Role.FOUNDER.to_int()
    )
    async def remove_rule(self, interaction: discord.Interaction, name: str):
        rule: Rules = remove_rule_by_name(name=name)

        if rule:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=f'Removed rule: "{rule["title"]}"',
                    description=f'Rule "{rule["title"]}" with identifier "{name}" is no longer available to the public.',
                    color=discord.Color.green(),
                ),
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=f'Could not find "{name}"',
                    description=f'There are no saved rules with name: {name}',
                    color=discord.Color.red(),
                ),
                ephemeral=True,
            )


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(Guidelines(bot))
