import discord
from discord.ext import commands, tasks
from datetime import datetime, timezone, time
import os

# ============================================================
#  KONFIGURATION – Railway Variables:
#  BOT_TOKEN    = dein Bot Token
#  MAIN_CHANNEL = ID des Hauptkanals
# ============================================================

TOKEN      = os.environ.get("BOT_TOKEN")
CHANNEL_ID = int(os.environ.get("MAIN_CHANNEL", "0"))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)

pinned_message_id = None


async def send_main_embed(channel):
    global pinned_message_id

    embed = discord.Embed(
        title="💬 Hauptchat",
        description=(
            "Hey ich bin **MyChat** – euer Hauptchat Bot! 🤖\n\n"
            "**Meine Fähigkeiten:**\n"
            "> 🗑️ Ich leere den Hauptchat jeden Tag um Mitternacht automatisch\n"
            "> 📌 Meine Nachricht bleibt immer erhalten\n"
            "> ✨ Ich halte den Chat sauber und übersichtlich\n\n"
            "Das ist der **Hauptchat** – hier könnt ihr euch frei unterhalten!\n"
            "Habt Spaß und seid nett zueinander! 🎉\n\n"
            "🛠️ Ich wurde gemacht von **Made.byMalik**"
        ),
        color=0x5865F2
    )

    embed.add_field(
        name="🕛 Automatische Reinigung",
        value="Dieser Kanal wird **täglich um Mitternacht** automatisch geleert.\nDiese Nachricht bleibt immer erhalten! 📌",
        inline=False
    )

    embed.set_footer(text="Made.byMalik • MyChat Bot")
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
#  DAILY CLEAR – jeden Tag um 00:00 UTC
# ════════════════════════════════════════════════════════════

@tasks.loop(time=time(hour=0, minute=0, second=0))
async def daily_clear():
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print("⚠️ Hauptkanal nicht gefunden!")
        return

    await channel.purge(limit=1000)
    await send_main_embed(channel)
    print("✅ Hauptkanal geleert.")


@daily_clear.before_loop
async def before_daily_clear():
    await bot.wait_until_ready()


# ════════════════════════════════════════════════════════════
#  COMMANDS
# ════════════════════════════════════════════════════════════

@bot.command(name="Main")
@commands.has_permissions(manage_messages=True)
async def main_cmd(ctx):
    await ctx.message.delete()
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        return await ctx.send("❌ Hauptkanal nicht gefunden! Bitte `MAIN_CHANNEL` Variable setzen.", delete_after=5)
    await send_main_embed(channel)
    await ctx.send(f"✅ Embed in {channel.mention} gesendet!", delete_after=3)


@bot.command(name="clear_now")
@commands.has_permissions(administrator=True)
async def clear_now(ctx):
    await ctx.message.delete()
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        return await ctx.send("❌ Hauptkanal nicht gefunden!", delete_after=5)
    await channel.purge(limit=1000)
    await send_main_embed(channel)
    await ctx.send("✅ Hauptkanal manuell geleert!", delete_after=3)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Du hast keine Berechtigung!", delete_after=5)
    elif isinstance(error, commands.CommandNotFound):
        pass


bot.run(TOKEN)
