import logging
from datetime import datetime

import discord
from discord.ext import commands

from pyboss.controllers.member import MemberController
from pyboss.controllers.message import MessageController


class Events(commands.Cog):
    WELCOME_CHANNEL = "📢annonces"

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        When client is connected
        """
        print(f"\n{' READY ':>^80}\n")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        When a member join a guild, insert it in database or restore all its data
        """
        member_ctrl = MemberController(member)
        if member_ctrl.exists():
            await member.add_roles(
                member_ctrl.sub_roles | {member_ctrl.top_role},  # union
                reason="The user was already register, re-attribute the main role",
            )
        else:
            member_ctrl.register()
            default_role = member_ctrl.get_role_by_name("Non Vérifié")
            await member.add_roles(default_role, reason="User was not verified")

        text = f"{member.mention} a rejoint le serveur {member.guild.name}!"
        embed = discord.Embed(
            title="Arrivée d'un membre!",
            colour=0xFF22FF,
            description=text,
            timestamp=datetime.now(),
        )
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_author(name=member.name, url=member.avatar_url)
        embed.set_footer(text=f"{self.bot.user.name}")

        publish_channel = discord.utils.get(
            member.guild.channels, name=self.WELCOME_CHANNEL
        )
        await publish_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, ctx):
        """
        Log message in database for users
        """
        if ctx.author.id != self.bot.user.id:
            MessageController(ctx.message).insert()

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """
        Check if a member has updated roles and modifies them in the database
        """
        if before.roles == after.roles:
            return

        member_ctrl = MemberController(after)
        if member_ctrl.exists():
            sub_roles = set()
            for role in after.roles:
                if role.name in ("Prof", "Non Vérifié", "Élève G1", "Élève G2"):
                    member_ctrl.top_role = role
                elif role.name.startswith("Groupe"):
                    member_ctrl.group_role = role
                elif role.name != "@everyone":
                    sub_roles.add(role)

            member_ctrl.sub_roles = sub_roles
        else:
            logging.error(f"The user {after.name} was not found in members table")


def setup(bot):
    bot.add_cog(Events(bot))
