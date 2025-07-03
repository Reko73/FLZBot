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

    if not channel or not log_channel:
        await interaction.response.send_message("Erreur : salon introuvable.", ephemeral=True)
        return

    if "@" in contenu:
        await interaction.response.send_message("⛔ Les mentions ne sont pas autorisées.", ephemeral=True)
        # Log possible ici
        return

    await interaction.response.defer(ephemeral=True)

    def draw_text(draw, text, position, font, max_width, fill):
        lines = []
        words = text.split()
        while words:
            line = ''
            while words and draw.textsize(line + words[0], font=font)[0] <= max_width:
                line += (words.pop(0) + ' ')
            lines.append(line)
        x, y = position
        line_height = font.getsize('A')[1] + 4

        for line in lines:
            draw.text((x, y), line, font=font, fill=fill)
            y += line_height

    image_path = "Fond.png"
    try:
        img = Image.open(image_path).convert("RGBA")
    except Exception:
        await interaction.followup.send("Erreur : image de fond introuvable.", ephemeral=True)
        return

    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 22)
    except:
        font = ImageFont.load_default()

    draw_text(draw, contenu, (40, 50), font, max_width=700, fill=(40, 20, 0))

    with io.BytesIO() as image_binary:
        img.save(image_binary, "PNG")
        image_binary.seek(0)
        file = discord.File(fp=image_binary, filename="post_it.png")
        await channel.send(file=file)

    await interaction.followup.send("Ton post-it a été déposé 📜", ephemeral=True)

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
