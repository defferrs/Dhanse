
import discord
from discord.ext import commands
from discord.commands import slash_command, Option
import json
import os

class MemberJoin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings_file = "Cogs/Moderation/data/memberjoin_settings.json"
        self.ensure_settings_file()
    
    def ensure_settings_file(self):
        """Ensure settings file exists"""
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        if not os.path.exists(self.settings_file):
            with open(self.settings_file, 'w') as f:
                json.dump({}, f)
    
    def load_settings(self):
        """Load settings from file"""
        try:
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_settings(self, settings):
        """Save settings to file"""
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=2)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Handle member join events"""
        settings = self.load_settings()
        guild_id = str(member.guild.id)
        
        if guild_id not in settings:
            return
        
        guild_settings = settings[guild_id]
        
        # Welcome message
        if 'welcome_channel' in guild_settings and 'welcome_message' in guild_settings:
            try:
                channel = self.bot.get_channel(int(guild_settings['welcome_channel']))
                if channel:
                    message = guild_settings['welcome_message'].replace('{user}', member.mention).replace('{server}', member.guild.name)
                    
                    embed = discord.Embed(
                        title="🎉 Welcome!",
                        description=message,
                        color=0x00FF00
                    )
                    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
                    embed.set_footer(text=f"Member #{len(member.guild.members)}")
                    
                    await channel.send(embed=embed)
            except Exception as e:
                print(f"Error sending welcome message: {e}")
        
        # Auto role
        if 'auto_role' in guild_settings:
            try:
                role = member.guild.get_role(int(guild_settings['auto_role']))
                if role:
                    await member.add_roles(role, reason="Auto role on join")
            except Exception as e:
                print(f"Error adding auto role: {e}")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Handle member leave events"""
        settings = self.load_settings()
        guild_id = str(member.guild.id)
        
        if guild_id not in settings:
            return
        
        guild_settings = settings[guild_id]
        
        # Goodbye message
        if 'goodbye_channel' in guild_settings and 'goodbye_message' in guild_settings:
            try:
                channel = self.bot.get_channel(int(guild_settings['goodbye_channel']))
                if channel:
                    message = guild_settings['goodbye_message'].replace('{user}', member.name).replace('{server}', member.guild.name)
                    
                    embed = discord.Embed(
                        title="👋 Goodbye",
                        description=message,
                        color=0xFF0000
                    )
                    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
                    
                    await channel.send(embed=embed)
            except Exception as e:
                print(f"Error sending goodbye message: {e}")

    @slash_command(description="🎉 Set up welcome messages")
    async def welcome_setup(self, ctx, channel: discord.TextChannel, *, message: Option(str, "Welcome message (use {user} for mention, {server} for server name)")):
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.respond("❌ You don't have permission to manage server settings!", ephemeral=True)
            return
        
        settings = self.load_settings()
        guild_id = str(ctx.guild.id)
        
        if guild_id not in settings:
            settings[guild_id] = {}
        
        settings[guild_id]['welcome_channel'] = str(channel.id)
        settings[guild_id]['welcome_message'] = message
        self.save_settings(settings)
        
        embed = discord.Embed(
            title="🎉 Welcome Setup Complete",
            description="Welcome messages have been configured!",
            color=0x00FF00
        )
        embed.add_field(name="📝 Channel", value=channel.mention, inline=True)
        embed.add_field(name="💬 Message", value=message, inline=False)
        
        await ctx.respond(embed=embed)

    @slash_command(description="👋 Set up goodbye messages")
    async def goodbye_setup(self, ctx, channel: discord.TextChannel, *, message: Option(str, "Goodbye message (use {user} for name, {server} for server name)")):
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.respond("❌ You don't have permission to manage server settings!", ephemeral=True)
            return
        
        settings = self.load_settings()
        guild_id = str(ctx.guild.id)
        
        if guild_id not in settings:
            settings[guild_id] = {}
        
        settings[guild_id]['goodbye_channel'] = str(channel.id)
        settings[guild_id]['goodbye_message'] = message
        self.save_settings(settings)
        
        embed = discord.Embed(
            title="👋 Goodbye Setup Complete",
            description="Goodbye messages have been configured!",
            color=0x00FF00
        )
        embed.add_field(name="📝 Channel", value=channel.mention, inline=True)
        embed.add_field(name="💬 Message", value=message, inline=False)
        
        await ctx.respond(embed=embed)

    @slash_command(description="🎭 Set up auto role assignment")
    async def auto_role_setup(self, ctx, role: discord.Role):
        if not ctx.author.guild_permissions.manage_roles:
            await ctx.respond("❌ You don't have permission to manage roles!", ephemeral=True)
            return
        
        settings = self.load_settings()
        guild_id = str(ctx.guild.id)
        
        if guild_id not in settings:
            settings[guild_id] = {}
        
        settings[guild_id]['auto_role'] = str(role.id)
        self.save_settings(settings)
        
        embed = discord.Embed(
            title="🎭 Auto Role Setup Complete",
            description=f"New members will automatically receive the **{role.name}** role!",
            color=0x00FF00
        )
        
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(MemberJoin(bot))
    print("✅ Member Join cog loaded successfully")
