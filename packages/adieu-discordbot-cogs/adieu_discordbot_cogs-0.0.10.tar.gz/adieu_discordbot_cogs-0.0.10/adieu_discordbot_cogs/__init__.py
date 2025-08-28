"""
Application init
"""

# Third Party
import requests

__version__ = "0.0.10"
__title__ = "ADIEU Discordbot Cogs"

__package_name__ = "adieu-discordbot-cogs"
__package_name_verbose__ = "Black Rose Discordbot Cogs"
__package_name_useragent__ = "ADIEU-Discordbot-Cogs"
__app_name__ = "adieu_discordbot_cogs"
__github_url__ = f"https://github.com/blackrose-eve/{__package_name__}"
__user_agent__ = (
    f"{__package_name_useragent__}/{__version__} "
    f"(+{__github_url__}) requests/{requests.__version__}"
)
