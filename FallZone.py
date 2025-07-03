import discord
from discord.ext import commands
from discord import app_commands
import os
from keep_alive import keep_alive
from discord.ext import commands, tasks
from discord import app_commands, Embed, Colour
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)

CHANNEL_ANO = 1376186168953016428

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"Commandes slash synchronisées : {len(synced)}")
    except Exception as e:
        print(f"Erreur lors de la synchronisation des commandes : {e}")

async def set_bot_status():
    # Définir l'activité et le statut du bot
    await bot.change_presence(
        status=discord.Status.dnd,  # Définir en mode "ne pas déranger"
        activity=discord.Activity(type=discord.ActivityType.watching, name="🧟 | 𝗙𝗮𝗹𝗹𝗭𝗼𝗻𝗲")
    )


@bot.tree.command(name="anonyme", description="Envoie un message RP anonyme dans un salon.")
@app_commands.describe(contenu="Le message à envoyer anonymement")
async def anonyme(interaction: discord.Interaction, contenu: str):
    await interaction.response.defer(ephemeral=True)  # Prévenir Discord qu'on va répondre

    channel = bot.get_channel(CHANNEL_ANO)
    if not channel:
        await interaction.followup.send("Erreur : salon introuvable.", ephemeral=True)
        return

    embed = Embed(
        title="📜 Un message anonyme a été trouvé...",
        description=f"\"{contenu}\"",
        color=Colour.dark_grey()
    )
    embed.set_footer(text="Personne ne sait qui l’a écrit.")

    await channel.send(embed=embed)
    await interaction.followup.send("Ton message anonyme a été envoyé.", ephemeral=True)

keep_alive()
bot.run(TOKEN)
