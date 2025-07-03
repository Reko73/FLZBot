import discord
from discord.ext import commands
from discord import app_commands
import os
from keep_alive import keep_alive
from discord.ext import commands, tasks
from discord import app_commands, Embed, Colour
from dotenv import load_dotenv
import datetime
from PIL import Image, ImageDraw, ImageFont
import io

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)

CHANNEL_ANO = 1390325529906774096
LOGS_DISCORD = 1390325343335878786


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
    channel = bot.get_channel(CHANNEL_ANO)
    log_channel = bot.get_channel(LOGS_DISCORD)

    if not channel:
        await interaction.response.send_message("Erreur : salon introuvable.", ephemeral=True)
        return
    if not log_channel:
        await interaction.response.send_message("Erreur : salon de logs introuvable.", ephemeral=True)
        return

    if "@" in contenu:
        await interaction.response.send_message("⛔ Les mentions ne sont pas autorisées.", ephemeral=True)
        # Logs ici si tu veux
        return

    await interaction.response.defer(ephemeral=True)

    # Création de l'image post-it (exemple simplifié)
    from PIL import Image, ImageDraw, ImageFont
    import io
    import textwrap

    image_path = "Fond.png"
    try:
        img = Image.open(image_path).convert("RGBA")
    except Exception:
        await interaction.followup.send("Erreur : image de fond introuvable.", ephemeral=True)
        return

    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()

    wrapped_text = textwrap.fill(contenu, width=40)
    draw.text((40, 50), wrapped_text, fill=(40, 20, 0), font=font)

    with io.BytesIO() as image_binary:
        img.save(image_binary, "PNG")
        image_binary.seek(0)
        file = discord.File(fp=image_binary, filename="post_it.png")
        await channel.send(file=file)

    await interaction.followup.send("Ton post-it a été déposé 📜", ephemeral=True)

    # Log de l'envoi
    log_message = (
        f"📜 **Message anonyme envoyé**\n"
        f"**Auteur** : {interaction.user} ({interaction.user.id})\n"
        f"**Contenu** : {contenu}\n"
        f"**Salon** : #{channel.name}\n"
        f"**Heure** : {discord.utils.format_dt(discord.utils.utcnow(), style='F')}"
    )
    await log_channel.send(log_message)

    

keep_alive()
bot.run(TOKEN)
