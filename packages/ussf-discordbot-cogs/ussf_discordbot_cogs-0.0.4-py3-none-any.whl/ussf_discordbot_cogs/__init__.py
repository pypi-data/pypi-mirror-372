"""
Application init
"""

# Third Party
import requests

__version__ = "0.0.4"
__title__ = "US-SF Discordbot Cogs"

__package_name__ = "ussf-discordbot-cogs"
__package_name_verbose__ = "US Space Force Discordbot Cogs"
__package_name_useragent__ = "US-SF-Discordbot-Cogs"
__app_name__ = "ussf_discordbot_cogs"
__github_url__ = f"https://github.com/aevans1897/{__package_name__}"
__user_agent__ = (
    f"{__package_name_useragent__}/{__version__} "
    f"(+{__github_url__}) requests/{requests.__version__}"
)
