"""
Hooking into the auth system
"""

# Alliance Auth
from allianceauth import hooks


@hooks.register("discord_cogs_hook")
def register_cogs():
    """
    Registering our discord cogs
    :return:
    :rtype:
    """

    return [
        #"adieu_discordbot_cogs.cogs.about",
        #"adieu_discordbot_cogs.cogs.admin",
        #"adieu_discordbot_cogs.cogs.auth",
        "adieu_discordbot_cogs.cogs.members",
        "adieu_discordbot_cogs.cogs.recruit_me",
        #"adieu_discordbot_cogs.cogs.welcome",
        "adieu_discordbot_cogs.cogs.migrate",
    ]