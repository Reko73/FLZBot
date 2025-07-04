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

BOOST_ANNOUNCE_CHANNELS = {
    1271212491568975944: 1278890511532298321,
}

ADMIN_ROLES = {
    1271212491568975944: [1389392610392670308, 1378463590239047834, 1383521854425268264, 1378463451474563123, 1378462539033346200, 1271212491568975952],
}

LOG_CHANNELS = {
    1271212491568975944: 1300630527178706965,
}

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)

CHANNEL_ANO = 1390325529906774096
LOGS_DISCORD = 1390325343335878786


async def set_bot_status():
    await bot.change_presence(
        status=discord.Status.dnd,
        activity=discord.Activity(type=discord.ActivityType.watching, name="🧟 | 𝗙𝗮𝗹𝗹𝗭𝗼𝗻𝗲")
    )

def user_is_admin(interaction):
    guild_id = interaction.guild.id
    allowed_role_ids = ADMIN_ROLES.get(guild_id, [])
    return any(role.id in allowed_role_ids for role in interaction.user.roles)


@bot.event
async def on_ready():
    await set_bot_status()
    print(f"Connecté en tant que {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"Commandes slash synchronisées : {len(synced)}")
    except Exception as e:
        print(f"Erreur lors de la synchronisation des commandes : {e}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if '@everyone' in message.content or '@here' in message.content:
        guild_id = message.guild.id
        allowed_role_ids = ADMIN_ROLES.get(guild_id, [])

        if not any(role.id in allowed_role_ids for role in message.author.roles):
            try:
                await message.delete()
            except discord.NotFound:
                pass
            await message.channel.send(
                "Ton message contenant 'everyone' ou 'here' a été supprimé car tu n'as pas les permissions.",
                delete_after=30
            )

            log_channel_id = LOG_CHANNELS.get(guild_id)
            log_channel = message.guild.get_channel(log_channel_id) if log_channel_id else None
            if log_channel:
                embed = Embed(
                    title="🔒 Message supprimé",
                    description=f"**Auteur :** {message.author.mention}\n"
                                f"**Contenu :**\n```{message.content}```",
                    color=0xFF0000
                )
                embed.set_footer(text=f"Salon : #{message.channel.name} • ID : {message.channel.id}")
                embed.timestamp = message.created_at
                await log_channel.send(embed=embed)

    await bot.process_commands(message)

@bot.event
async def on_member_update(before, after):
    if before.premium_since is None and after.premium_since is not None:
        guild_id = after.guild.id
        channel_id = BOOST_ANNOUNCE_CHANNELS.get(guild_id)

        if channel_id:
            channel = after.guild.get_channel(channel_id)
            if channel:
                embed = discord.Embed(
                    title="🚀 Merci pour le boost !",
                    description=f"{after.mention} vient de booster **{after.guild.name}** ! 💜",
                    color=discord.Color.purple()
                )
                embed.set_thumbnail(url=after.display_avatar.url)
                await channel.send(embed=embed)


# ===============================
# ======== COMMANDES RP =========
# ===============================


@bot.tree.command(name="anonyme", description="Envoie un message RP anonyme dans un salon.")
@app_commands.describe(contenu="Le message à envoyer anonymement")
async def anonyme(interaction: discord.Interaction, contenu: str):
    if not interaction.response.is_done():
        try:
            await interaction.response.defer(ephemeral=True)
        except discord.NotFound:
            return

    channel = bot.get_channel(CHANNEL_ANO)
    log_channel = bot.get_channel(LOGS_DISCORD)
    if not channel:
        await interaction.followup.send("Erreur : salon introuvable.", ephemeral=True)
        return
    if not log_channel:
        await interaction.followup.send("Erreur : salon de logs introuvable.", ephemeral=True)
        return

    if "@" in contenu:
        await interaction.followup.send("⛔ Les mentions ne sont pas autorisées dans ce message.", ephemeral=True)

        # Log de la tentative bloquée
        log_message = (
            f"🚫 **Tentative de mention bloquée**\n"
            f"**Auteur** : {interaction.user} ({interaction.user.id})\n"
            f"**Contenu tenté** : {contenu}\n"
            f"**Salon ciblé** : #{channel.name}\n"
            f"**Heure** : {discord.utils.format_dt(discord.utils.utcnow(), style='F')}"
        )
        await log_channel.send(log_message)
        return

    embed = Embed(
        title="📜 Un Post-it a été déposé...",
        description=f"\"{contenu}\"",
        color=Colour.from_rgb(180, 160, 100)
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


# ===============================
# ====== COMMANDES MODO =========
# ===============================

@bot.tree.command(name="purge", description="Supprime un nombre spécifié de messages.")
async def purge(interaction: discord.Interaction, number: int):
    if not user_is_admin(interaction):
        await interaction.response.send_message("Vous n'avez pas les permissions nécessaires pour utiliser cette commande.", ephemeral=True)
        return

    if number <= 0:
        await interaction.response.send_message("Veuillez spécifier un nombre positif de messages à supprimer.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=number)
    await interaction.followup.send(f"{len(deleted)} messages ont été supprimés.", ephemeral=True)
                
    

keep_alive()
bot.run(TOKEN)
