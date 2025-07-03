import discord
from discord.ext import commands
from discord import app_commands
import os
from keep_alive import keep_alive
from discord.ext import commands, tasks
from discord import app_commands, Embed, Colour
from dotenv import load_dotenv
import datetime

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)

CHANNEL_ANO = 1390321557980708986
LOGS_DISCORD = 1376186169485951082


async def set_bot_status():
    await bot.change_presence(
        status=discord.Status.dnd,
        activity=discord.Activity(type=discord.ActivityType.watching, name="🧟 | 𝗙𝗮𝗹𝗹𝗭𝗼𝗻𝗲")
    )
    
@bot.event
async def on_ready():
    await set_bot_status()
    print(f"Connecté en tant que {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"Commandes slash synchronisées : {len(synced)}")
    except Exception as e:
        print(f"Erreur lors de la synchronisation des commandes : {e}")


@bot.tree.command(name="anonyme", description="Envoie un message RP anonyme dans un salon.")
@app_commands.describe(contenu="Le message à envoyer anonymement")
async def anonyme(interaction: discord.Interaction, contenu: str):
    await interaction.response.defer(ephemeral=True)  # Prévenir Discord qu'on va répondre

    channel = bot.get_channel(CHANNEL_ANO)
    log_channel = bot.get_channel(LOGS_DISCORD)
    if not channel:
        await interaction.followup.send("Erreur : salon introuvable.", ephemeral=True)
        return
    if not log_channel:
        await interaction.followup.send("Erreur : salon de logs introuvable.", ephemeral=True)
        return

    embed = Embed(
        title="📜 Un Post-it a été déposé...",
        description=f"\"{contenu}\"",
        color=Colour.dark_grey()
    )
    embed.set_footer(text="Personne ne sait qui l’a écrit.")

    await channel.send(embed=embed)
    await interaction.followup.send("Ton message anonyme a été envoyé.", ephemeral=True)

    log_message = (
        f"📝 **Message anonyme envoyé**\n"
        f"**Auteur** : {interaction.user} ({interaction.user.id})\n"
        f"**Contenu** : {contenu}\n"
        f"**Salon** : #{channel.name}\n"
        f"**Heure** : {discord.utils.format_dt(discord.utils.utcnow(), style='F')}"
    )
    await log_channel.send(log_message)

keep_alive()
bot.run(TOKEN)
