"""
Helper functions for the TNNT Discord bot.
"""

# Third Party
from discord.ext import commands


def unload_cog(bot: commands.Bot, cog_name: str) -> None:
    """
    Unloads a cog from the bot.

    :param bot: The bot instance.
    :type bot: discord.ext.commands.Bot
    :param cog_name: The name of the cog to unload.
    :type cog_name: str
    """

    try:
        bot.remove_cog(name=cog_name)

        print(f"Unloaded {cog_name} successfully.")
    except Exception as e:
        print(f"Failed to unload {cog_name}: {e}")