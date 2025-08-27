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
        "ussf_discordbot_cogs.cogs.about",
        #"ussf_discordbot_cogs.cogs.admin",
        "ussf_discordbot_cogs.cogs.auth",
        "ussf_discordbot_cogs.cogs.recruit_me",
        #"ussf_discordbot_cogs.cogs.welcome",
    ]