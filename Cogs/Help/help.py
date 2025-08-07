import discord
from discord.ext import commands
from discord.commands import slash_command

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="help", description="📚 Tampilkan bantuan dan daftar perintah bot")
    async def help_command(self, ctx):
        """Menampilkan bantuan lengkap bot dengan semua fitur yang tersedia"""

        embed = discord.Embed(
            title="🤖 DHansen Bot - Panduan Lengkap",
            description="Bot All-in-One dengan fitur lengkap untuk server Discord",
            color=0x4285F4
        )

        # Music Commands
        embed.add_field(
            name="🎵 **Musik**",
            value=(
                "`/play <lagu>` - Putar musik dari YouTube\n"
                "`/search <query>` - Cari musik dan pilih\n"
                "`/queue` - Lihat antrian musik\n"
                "`/skip` - Lewati lagu\n"
                "`/stop` - Hentikan musik\n"
                "`/volume <1-100>` - Atur volume\n"
                "`/pause` - Jeda musik\n"
                "`/resume` - Lanjutkan musik"
            ),
            inline=False
        )

        # Moderation Commands
        embed.add_field(
            name="🛡️ **Moderasi**",
            value=(
                "`/ban <user>` - Ban anggota\n"
                "`/kick <user>` - Kick anggota\n"
                "`/warn <user>` - Beri peringatan\n"
                "`/timeout <user>` - Timeout anggota\n"
                "`/clear <jumlah>` - Hapus pesan\n"
                "`/warnings <user>` - Lihat peringatan\n"
                "`/setjoin` - Set channel welcome"
            ),
            inline=False
        )

        # Role Commands
        embed.add_field(
            name="👥 **Role Management**",
            value=(
                "`/addrole <user> <role>` - Tambah role\n"
                "`/removerole <user> <role>` - Hapus role\n"
                "`/reactionrole` - Setup reaction role\n"
                "`/removereaction` - Hapus reaction role"
            ),
            inline=False
        )

        # Search Commands
        embed.add_field(
            name="🔍 **Pencarian**",
            value="`/search <query>` - Cari di Google",
            inline=False
        )

        embed.set_footer(
            text="🚀 Bot ini dioptimalkan untuk mobile • Semua fitur tersedia",
            icon_url=ctx.bot.user.avatar.url if ctx.bot.user.avatar else None
        )

        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Help(bot))
    print("✅ Help cog loaded successfully")