
import discord
from discord.ext import commands
from discord.commands import slash_command, Option
import asyncio
from googlesearch import search
import requests
from bs4 import BeautifulSoup

class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="search", description="🔍 Cari informasi di Google dengan hasil terstruktur")
    async def search_google(self, ctx, *, query: Option(str, "Kata kunci pencarian")):
        """Pencarian Google dengan hasil yang diformat rapi untuk mobile"""
        
        # Send initial response
        embed = discord.Embed(
            title="🔍 Mencari...",
            description=f"Sedang mencari: **{query}**",
            color=0x4285F4
        )
        await ctx.respond(embed=embed)
        
        try:
            # Perform Google search
            search_results = []
            for url in search(query, num_results=5):
                try:
                    response = requests.get(url, timeout=3)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    title = soup.find('title')
                    description = soup.find('meta', attrs={'name': 'description'})
                    
                    if title:
                        title_text = title.get_text()[:100]
                    else:
                        title_text = "No title found"
                    
                    if description:
                        desc_text = description.get('content', '')[:200]
                    else:
                        desc_text = "No description available"
                    
                    search_results.append({
                        'title': title_text,
                        'description': desc_text,
                        'url': url
                    })
                except:
                    search_results.append({
                        'title': url.split('/')[-1][:50],
                        'description': "Could not fetch description",
                        'url': url
                    })
            
            # Create result embed
            embed = discord.Embed(
                title=f"🔍 Hasil Pencarian: {query}",
                description=f"Ditemukan {len(search_results)} hasil teratas",
                color=0x4285F4
            )
            
            for i, result in enumerate(search_results, 1):
                embed.add_field(
                    name=f"{i}. {result['title']}",
                    value=f"**Description:** {result['description']}\n**Link:** [🔗 Click here]({result['url']})",
                    inline=False
                )
            
            embed.set_footer(text="🔍 Powered by Google Search • Mobile optimized")
            await ctx.edit(embed=embed)
            
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Search Failed",
                description=f"An error occurred while searching: {str(e)}",
                color=0xFF0000
            )
            await ctx.edit(embed=error_embed)



def setup(bot):
    bot.add_cog(Search(bot))
    print("Google Search cog loaded")
