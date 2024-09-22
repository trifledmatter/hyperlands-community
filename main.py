from typing import Coroutine, Any, List, Dict
from dtypes.collections.profile import (
    CommunityProfile,
    find_profile_by_id,
    save,
    update_profile_by_id,
)

import glob
import importlib.util
from datetime import datetime

import discord
from discord.ext import commands

from config import get_config_or_throw


class HyperLands(commands.AutoShardedBot):
    def __init__(self, shard_count: int = None, **kwargs) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        # intents.presences = True
        intents.members = True

        self.commands_directory = "./commands"
        self.commands_loaded = []

        # check in this list for loaded profiles before
        # querying the database to save on requests
        self.cached_profiles: List[CommunityProfile] = []

        super().__init__(
            command_prefix="hl!", intents=intents, shard_count=shard_count, **kwargs
        )

    async def setup_cogs(self) -> Coroutine[Any, Any, Coroutine]:
        commands = glob.glob(f"{self.commands_directory}/**/*.py", recursive=True)

        for command in commands:
            module_name = (
                command.replace("/", ".").replace("\\", ".").removesuffix(".py")
            )

            try:
                spec = importlib.util.spec_from_file_location(module_name, command)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)

                if hasattr(mod, "setup"):
                    await mod.setup(self)
                    self.commands_loaded.append(module_name.split(".")[-1])

            except Exception as e:
                print(f"Error loading command {module_name}: {e}")
                continue

    async def setup_hook(self) -> None:
        await self.setup_cogs()
        await self.tree.sync()
        print(self.commands_loaded)


if __name__ == "__main__":
    service = HyperLands(shard_count=2)

    @service.event
    async def on_message(message: discord.Message) -> None:
        # search for
        # print(message.author.id)

        if message.author.bot:
            return

        _user: CommunityProfile = None

        if len(service.cached_profiles) > 0:
            for profile in service.cached_profiles:
                if not profile.get("user_id") == str(
                    message.author.id
                ):  # couldn't find in cache

                    _user: CommunityProfile = find_profile_by_id(str(message.author.id))

                    if _user is not None and _user not in service.cached_profiles:
                        # we couldn't find the profile in cached profiles, but it exists in the database, so cache it
                        service.cached_profiles.append(_user)
                        print(
                            "database - profile found but isn't cached. Caching... [0]"
                        )
                        continue

                    # we could not find the profile in cached or database, so make a new profile
                    new_user: CommunityProfile = {
                        "user_id": str(message.author.id),
                        "color": "default",
                        "level": 0,
                        "name": str(message.author.name),
                        "nickname": str(message.author.global_name),
                        "timestamp": datetime.now(),
                    }

                    if not find_profile_by_id(str(message.author.id)):
                        save(new_user)
                        service.cached_profiles.append(new_user)
                        print("database - new profile found, saving... [1]")

                # the profile is in cached profiles,
                # which means they have a profile
                # don't do anything
                continue

        _user = find_profile_by_id(str(message.author.id))

        if _user is not None:
            print("database - profile found but isn't cached. Caching... [1]")
            service.cached_profiles.append(_user)
        else:
            # we could not find the profile in cached or database, so make a new profile
            new_user: CommunityProfile = {
                "user_id": str(message.author.id),
                "color": "default",
                "level": 0,
                "name": str(message.author.name),
                "nickname": str(message.author.global_name),
                "timestamp": datetime.now(),
            }

            save(new_user)
            service.cached_profiles.append(new_user)
            print("database - new profile found, saving... [0]")

        # leveling system
        # 5xp per message

        usr: CommunityProfile = find_profile_by_id(str(message.author.id))

        if usr:
            update_profile_by_id(
                str(message.author.id),
                "level",
                str(
                    usr.get("level") + 5
                    if not (usr.get("level") + 5 >= 1000)
                    else usr.get("level")
                )
                + "/1000",
            )

        return

    service.run(get_config_or_throw("token"))
