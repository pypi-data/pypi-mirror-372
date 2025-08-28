# Cog Stuff
import logging

from discord.colour import Color
from discord.embeds import Embed
from discord.ext import commands

# AA Contexts
from aadiscordbot.app_settings import get_site_url
from adieu_discordbot_cogs.helper import unload_cog

logger = logging.getLogger(__name__)


class Migrate(commands.Cog):
    """
    A Collection of Authentication Tools for Alliance Auth
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def migrate(self, ctx):
        """
        Returns a link to the AllianceAuth Install
        Used by many other Bots and is a common command that
        users will attempt to run.
        """
        await ctx.trigger_typing()

        embd = Embed(title="AllianceAuth")
        embd.set_thumbnail(
            url="https://assets.gitlab-static.net/uploads/-/system/project/avatar/6840712/Alliance_auth.png?width=128"
        )
        embd.colour = Color.blue()

        embd.description = "All Authentication functions for this Discord server are handled through our Alliance Auth install"

        url = get_site_url()

        embd.add_field(
            name="Auth Link", value=url, inline=False
        )

        return await ctx.send(embed=embd)

    @commands.slash_command(name='migrate')
    async def migrate_slash(self, ctx):
        """
        Returns a response about the Migration to Auth from SeAT.
        """
        if ctx.guild:
            embd = Embed(description="We have begun the process of decommissioning SeAT and have begun the migration to Alliance Auth. \n\n**You will need to log into here:**\nhttps://auth.black-rose.space\n\n**The Activate CharLink here:**\nhttps://auth.black-rose.space/charlink/\n\n**Then Activate the Discord Service here:**\nhttps://auth.black-rose.space/services/\n\n**Then apply for groups in here:**\nhttps://auth.black-rose.space/groups/\n\nIf you still need assistance please use:\n```\n/help\n```",
                      colour=0x00b0f4)

            embd.set_author(name="SeAT to Auth Migration!")

            return await ctx.respond(embed=embd)

        else:
            return await ctx.respond(
                "Sorry, this command cannot be used in DMs."
            )


def setup(bot):
    unload_cog(bot=bot, cog_name="Migrate")
    bot.add_cog(Migrate(bot))