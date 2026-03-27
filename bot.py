import discord
from discord.ext import commands, tasks
from datetime import datetime, timezone, time
import os

# ============================================================
#  KONFIGURATION – Railway Variables:
#  BOT_TOKEN    = dein Bot Token
#  MAIN_CHANNEL = ID des Hauptkanals (Rechtsklick auf Kanal → ID kopieren)
# ============================================================

TOKEN       = os.environ.get("BOT_TOKEN")
CHANNEL_ID  = int(os.environ.get("MAIN_CHANNEL", "0"))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)

# Gespeicherte Message-ID des Pinned Embeds
pinned_message_id = None


async def send_main_embed(channel):
    """Sendet das Haupt-Embed in den Kanal."""
    global pinned_message_id

    embed = discord.Embed(
        title="💬 Willkommen im Hauptkanal!",
        description=(
            "Hier ist der Ort für **allgemeine Unterhaltung** auf unserem Server.\n"
            "Chatte, lache und lerne andere Mitglieder kennen! 🎉"
        ),
        color=0x5865F2
    )

    embed.add_field(
        name="📌 Was ist dieser Kanal?",
        value=(
            "Der **Hauptkanal** ist der zentrale Treffpunkt des Servers.\n"
            "Hier kannst du über alles reden – von Gaming bis zum Alltag."
        ),
        inline=False
    )

    embed.add_field(
        name="✅ Erlaubt",
        value=(
            "> 💬 Allgemeine Gespräche\n"
            "> 😄 Memes & Humor\n"
            "> 🤝 Neue Mitglieder begrüßen\n"
            "> 🎮 Gaming-Talk"
        ),
        inline=True
    )

    embed.add_field(
        name="❌ Nicht erlaubt",
        value=(
            "> 🚫 Spam & Flooding\n"
            "> 🔞 NSFW Inhalte\n"
            "> 💢 Beleidigungen\n"
            "> 📢 Werbung"
        ),
        inline=True
    )

    embed.add_field(
        name="🕛 Automatische Reinigung",
        value="Dieser Kanal wird **täglich um Mitternacht** automatisch geleert.\nDiese Nachricht bleibt immer erhalten! 📌",
        inline=False
    )

    embed.set_footer(text="Made.byMalik • Hauptkanal Bot")
    embed.timestamp = datetime.now(timezone.utc)

    msg = await channel.send(embed=embed)
    pinned_message_id = msg.id

    try:
        await msg.pin()
    except Exception:
        pass

    return msg


# ════════════════════════════════════════════════════════════
#  EVENTS
# ════════════════════════════════════════════════════════════

@bot.event
async def on_ready():
    print(f"✅ Bot ist online als {bot.user}")
    daily_clear.start()


# ════════════════════════════════════════════════════════════
#  DAILY CLEAR TASK – jeden Tag um 00:00 UTC
# ════════════════════════════════════════════════════════════

@tasks.loop(time=time(hour=0, minute=0, second=0))
async def daily_clear():
    global pinned_message_id

    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print("⚠️ Hauptkanal nicht gefunden!")
        return

    print(f"🗑️ Leere Hauptkanal: #{channel.name}")

    # Alle Nachrichten löschen
    await channel.purge(limit=1000)

    # Neues Embed senden
    await send_main_embed(channel)
    print("✅ Hauptkanal geleert und Embed neu gesendet.")


@daily_clear.before_loop
async def before_daily_clear():
    await bot.wait_until_ready()


# ════════════════════════════════════════════════════════════
#  COMMANDS
# ════════════════════════════════════════════════════════════

@bot.command(name="Main")
@commands.has_permissions(manage_messages=True)
async def main_cmd(ctx):
    """Sendet das Haupt-Embed manuell."""
    await ctx.message.delete()

    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        return await ctx.send("❌ Hauptkanal nicht gefunden! Bitte `MAIN_CHANNEL` Variable setzen.", delete_after=5)

    await send_main_embed(channel)
    await ctx.send(f"✅ Embed in {channel.mention} gesendet!", delete_after=3)


@bot.command(name="clear_now")
@commands.has_permissions(administrator=True)
async def clear_now(ctx):
    """Leert den Hauptkanal sofort manuell."""
    await ctx.message.delete()

    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        return await ctx.send("❌ Hauptkanal nicht gefunden!", delete_after=5)

    await channel.purge(limit=1000)
    await send_main_embed(channel)
    await ctx.send(f"✅ Hauptkanal manuell geleert!", delete_after=3)


# ── Error Handler ────────────────────────────────────────────
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Du hast keine Berechtigung!", delete_after=5)
    elif isinstance(error, commands.CommandNotFound):
        pass


bot.run(TOKEN)
