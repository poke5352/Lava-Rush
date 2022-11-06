import nextcord
from nextcord.ext.commands import Bot

from config import TOKEN, SLASH_GUILDS, EMBED_COLOR, FOOTER, COGS

intents = nextcord.Intents.default()
intents.members = True
intents.messages = True
bot = Bot(intents=intents)

@bot.event
async def on_ready():
    print("Bot is ready!")


for extension in COGS:
    bot.load_extension(extension)
bot.run(TOKEN)

