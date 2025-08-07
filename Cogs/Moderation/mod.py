import discord
from discord.ext import commands
import json
import datetime
from discord.commands import slash_command, Option
import os
import asyncio

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warnings_file = "Cogs/Moderation/warnings.json"
        self.ensure_warnings_file()

    def ensure_warnings_file(self):
        """Ensure warnings file exists"""
        if not os.path.exists(self.warnings_file):
            with open(self.warnings_file, 'w') as f:
                json.dump({}, f)

    def load_warnings(self):
        """Load warnings from file"""
        try:
            with open(self.warnings_file, 'r') as f:
                return json.load(f)
        except:
            return {}

    def save_warnings(self, warnings):
        """Save warnings to file"""
        with open(self.warnings_file, 'w') as f:
            json.dump(warnings, f, indent=2)

    @slash_command(description="🦶 Kick a member from the server")
    async def kick(self, ctx, member: discord.Member, *, reason: Option(str, "Reason for kick", default="No reason provided")):
        if not ctx.author.guild_permissions.kick_members:
            await ctx.respond("❌ You don't have permission to kick members!", ephemeral=True)
            return

        try:
            await member.kick(reason=reason)

            embed = discord.Embed(
                title="🦶 Member Kicked",
                description=f"**{member.mention} has been kicked**",
                color=0xFF9500
            )
            embed.add_field(name="👤 Member", value=f"{member.name}#{member.discriminator}", inline=True)
            embed.add_field(name="🛡️ Moderator", value=ctx.author.mention, inline=True)
            embed.add_field(name="📝 Reason", value=reason, inline=False)
            embed.set_footer(text=f"User ID: {member.id}")

            await ctx.respond(embed=embed)

        except Exception as e:
            await ctx.respond(f"❌ Failed to kick member: {str(e)}", ephemeral=True)

    @slash_command(description="🔨 Ban a member from the server")
    async def ban(self, ctx, member: discord.Member, *, reason: Option(str, "Reason for ban", default="No reason provided")):
        if not ctx.author.guild_permissions.ban_members:
            await ctx.respond("❌ You don't have permission to ban members!", ephemeral=True)
            return

        try:
            await member.ban(reason=reason)

            embed = discord.Embed(
                title="🔨 Member Banned",
                description=f"**{member.mention} has been banned**",
                color=0xFF0000
            )
            embed.add_field(name="👤 Member", value=f"{member.name}#{member.discriminator}", inline=True)
            embed.add_field(name="🛡️ Moderator", value=ctx.author.mention, inline=True)
            embed.add_field(name="📝 Reason", value=reason, inline=False)
            embed.set_footer(text=f"User ID: {member.id}")

            await ctx.respond(embed=embed)

        except Exception as e:
            await ctx.respond(f"❌ Failed to ban member: {str(e)}", ephemeral=True)

    @slash_command(description="🔓 Unban a user by their ID")
    async def unban(self, ctx, user_id: Option(str, "User ID to unban")):
        if not ctx.author.guild_permissions.ban_members:
            await ctx.respond("❌ You don't have permission to unban members!", ephemeral=True)
            return

        try:
            user_id = int(user_id)
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user)

            embed = discord.Embed(
                title="🔓 Member Unbanned",
                description=f"**{user.name}#{user.discriminator} has been unbanned**",
                color=0x00FF00
            )
            embed.add_field(name="🛡️ Moderator", value=ctx.author.mention, inline=True)
            embed.set_footer(text=f"User ID: {user.id}")

            await ctx.respond(embed=embed)

        except ValueError:
            await ctx.respond("❌ Invalid user ID format!", ephemeral=True)
        except Exception as e:
            await ctx.respond(f"❌ Failed to unban user: {str(e)}", ephemeral=True)

    @slash_command(description="⚠️ Warn a member")
    async def warn(self, ctx, member: discord.Member, *, reason: Option(str, "Reason for warning", default="No reason provided")):
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.respond("❌ You don't have permission to warn members!", ephemeral=True)
            return

        warnings = self.load_warnings()
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)

        if guild_id not in warnings:
            warnings[guild_id] = {}
        if user_id not in warnings[guild_id]:
            warnings[guild_id][user_id] = []

        warning = {
            "reason": reason,
            "moderator": str(ctx.author.id),
            "timestamp": datetime.datetime.now().isoformat()
        }

        warnings[guild_id][user_id].append(warning)
        self.save_warnings(warnings)

        warning_count = len(warnings[guild_id][user_id])

        embed = discord.Embed(
            title="⚠️ Member Warned",
            description=f"**{member.mention} has been warned**",
            color=0xFFFF00
        )
        embed.add_field(name="👤 Member", value=f"{member.name}#{member.discriminator}", inline=True)
        embed.add_field(name="🛡️ Moderator", value=ctx.author.mention, inline=True)
        embed.add_field(name="📝 Reason", value=reason, inline=False)
        embed.add_field(name="📊 Total Warnings", value=str(warning_count), inline=True)
        embed.set_footer(text=f"User ID: {member.id}")

        await ctx.respond(embed=embed)

    @slash_command(description="📊 View warnings for a member")
    async def warnings(self, ctx, member: discord.Member):
        warnings = self.load_warnings()
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)

        if guild_id not in warnings or user_id not in warnings[guild_id]:
            await ctx.respond(f"📊 {member.mention} has no warnings.", ephemeral=True)
            return

        user_warnings = warnings[guild_id][user_id]

        embed = discord.Embed(
            title=f"📊 Warnings for {member.name}#{member.discriminator}",
            color=0xFFFF00
        )

        for i, warning in enumerate(user_warnings[-5:], 1):  # Show last 5 warnings
            moderator = self.bot.get_user(int(warning['moderator']))
            moderator_name = moderator.name if moderator else "Unknown"
            timestamp = datetime.datetime.fromisoformat(warning['timestamp']).strftime("%Y-%m-%d %H:%M")

            embed.add_field(
                name=f"Warning #{len(user_warnings) - 5 + i}",
                value=f"**Reason:** {warning['reason']}\n**Moderator:** {moderator_name}\n**Date:** {timestamp}",
                inline=False
            )

        embed.set_footer(text=f"Total warnings: {len(user_warnings)} • User ID: {member.id}")

        await ctx.respond(embed=embed)

    @slash_command(description="🔇 Timeout a member")
    async def timeout(self, ctx, member: discord.Member, duration: Option(int, "Duration in minutes"), *, reason: Option(str, "Reason for timeout", default="No reason provided")):
        if not ctx.author.guild_permissions.moderate_members:
            await ctx.respond("❌ You don't have permission to timeout members!", ephemeral=True)
            return

        try:
            timeout_until = discord.utils.utcnow() + datetime.timedelta(minutes=duration)
            await member.timeout(timeout_until, reason=reason)

            embed = discord.Embed(
                title="🔇 Member Timed Out",
                description=f"**{member.mention} has been timed out**",
                color=0xFF6B00
            )
            embed.add_field(name="👤 Member", value=f"{member.name}#{member.discriminator}", inline=True)
            embed.add_field(name="🛡️ Moderator", value=ctx.author.mention, inline=True)
            embed.add_field(name="⏰ Duration", value=f"{duration} minutes", inline=True)
            embed.add_field(name="📝 Reason", value=reason, inline=False)
            embed.set_footer(text=f"User ID: {member.id}")

            await ctx.respond(embed=embed)

        except Exception as e:
            await ctx.respond(f"❌ Failed to timeout member: {str(e)}", ephemeral=True)

    @slash_command(description="🧹 Clear messages from the channel")
    async def clear(self, ctx, amount: Option(int, "Number of messages to delete (max 100)", min_value=1, max_value=100)):
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.respond("❌ You don't have permission to manage messages!", ephemeral=True)
            return

        try:
            deleted = await ctx.channel.purge(limit=amount)

            embed = discord.Embed(
                title="🧹 Messages Cleared",
                description=f"**{len(deleted)} messages have been deleted**",
                color=0x00FF00
            )
            embed.add_field(name="🛡️ Moderator", value=ctx.author.mention, inline=True)
            embed.add_field(name="📝 Channel", value=ctx.channel.mention, inline=True)

            await ctx.respond(embed=embed, delete_after=5)

        except Exception as e:
            await ctx.respond(f"❌ Failed to clear messages: {str(e)}", ephemeral=True)

def setup(bot):
    bot.add_cog(Moderation(bot))
    print("✅ Moderation cog loaded successfully")