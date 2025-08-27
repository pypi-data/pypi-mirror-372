# Cog Stuff
import logging

import discord
# AA-Discordbot
from discord.embeds import Embed
from discord.ext import commands

# AA Contexts
from django.conf import settings
from django.utils import timezone
from adieu_discordbot_cogs.helper import unload_cog

from aadiscordbot import app_settings

logger = logging.getLogger(__name__)


class RecruitMe(commands.Cog):
    """
    Thread Tools for recruiting!
    """

    def __init__(self, bot):
        self.bot = bot

    async def open_ticket(
        self,
        ctx: discord.Interaction,
        member: discord.Member
    ):
        sup_channel = settings.RECRUIT_CHANNEL_ID
        ch = ctx.guild.get_channel(sup_channel)
        th = await ch.create_thread(
            name=f"{member.display_name} | {timezone.now().strftime('%Y-%m-%d %H:%M')}",
            auto_archive_duration=10080,
            type=discord.ChannelType.private_thread,
            reason=None
        )
        msg = (f"<@{member.id}> is hunting for a recruiter!\n\n"
               f"Someone from our <@&{settings.RECRUITER_GROUP_ID}> team will get in touch soon!")
        embd = Embed(title="Black Rose Recruitment",
                            description="Welcome! We're glad you're interested in joining us!\n\nIn order to proceed, you will need to set up authentication for all your characters that you will use with our Alliance. Once that's done, we'll finalize the recruitment process with a voice interview with one of our recruiters!\n\nFollow the links below to get started:\n\n> **Sign into our Alliance Authentication service:**\nhttps://auth.black-rose.space/dashboard/\n\n> **After logging in, click on the Login button on this page in the Char Link box:**\nhttps://auth.black-rose.space/charlink/\n\n> **Link your discord account here:**\nhttps://auth.black-rose.space/services/\n\n**Disclaimer**\nThese services **DO NOT** obtain private account information such as username and passwords. We utilize these services to ensure safety within our sovereignty, and provide pilots with information.",
                            colour=0x00b0f4)

        embd.set_thumbnail(url="https://images.evetech.net/alliances/99012770/logo")

        embd.set_footer(text="Crafted for Black Rose, based on AA Discordbot")
        await th.send(msg, embed=embd)
        await ctx.response.send_message(content="Recruitment thread created!", view=None, ephemeral=True)

    @commands.slash_command(
        name='recruit_me',
        guild_ids=app_settings.get_all_servers()
    )
    async def slash_halp(
        self,
        ctx,
    ):
        """
            Get hold of a recruiter
        """
        await self.open_ticket(ctx, ctx.user)

    @commands.message_command(
        name="Create Recruitment Thread",
        guild_ids=app_settings.get_all_servers()
    )
    async def reverse_recruit_msg_context(
        self,
        ctx,
        message
    ):
        """
            Help a new guy get recruiter
        """
        await self.open_ticket(ctx, message.author)

    @commands.user_command(
        name="Recruit Member",
        guild_ids=app_settings.get_all_servers()
    )
    async def reverse_recruit_user_context(
        self, ctx, user
    ):
        """
            Help a new guy get recruiter
        """
        await self.open_ticket(ctx, user)


def setup(bot):
    #unload_cog(bot=bot, cog_name="RecruitMe")
    bot.add_cog(RecruitMe(bot))