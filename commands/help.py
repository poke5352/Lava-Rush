import nextcord

from nextcord import slash_command, SlashOption
from nextcord.ext.commands import Bot, Cog
from config import SLASH_GUILDS, EMBED_COLOR, FOOTER


class Help(Cog):
    def __init__(self, bot):
        self.bot = bot
    

    @slash_command(
    name="help",
    description="Help Command",
    guild_ids=SLASH_GUILDS
    )
    async def help(self, ctx):
        embed = nextcord.Embed(
            title = "Help Menu LavaBot",
            description = "```Thank you for choosing Lava Bot! Below is our simple command list and with what they do.```",
            color = EMBED_COLOR

        )
        embed.add_field(
            name = "help",
            value = "Shows this message",
            inline = False
        )
        embed.add_field(
            name = "start",
            value = "Starts the game",
            inline = False
        )
        embed.add_field(
            name = "endgame",
            value = "Administrators can end game forcefully",
            inline = False
        )

        embed.set_footer(text=FOOTER)

        await ctx.response.send_message(embed=embed)




def setup(bot: Bot) -> None:
    bot.add_cog(Help(bot))
