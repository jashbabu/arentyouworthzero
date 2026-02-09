import os
import discord
from discord.ext import commands

# 1. Grab your token from env
TOKEN = os.getenv("TOKEN")

# 2. Fix: Added message_content intent so your prefix commands actually work
intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)

MOD_LOG_CHANNEL_ID = 1470294904201678959
REPORT_CHANNEL_ID = 1470470688338084060

# ---------- MODAL ----------
class ReportModal(discord.ui.Modal, title="Submit a Report"):
    report = discord.ui.TextInput(
        label="What happened?",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000,
    )

    async def on_submit(self, interaction: discord.Interaction):
        mod_log = interaction.guild.get_channel(MOD_LOG_CHANNEL_ID)

        if not mod_log:
            return await interaction.response.send_message("Error: Mod log channel not found.", ephemeral=True)

        embed = discord.Embed(
            title="🚨 New Report",
            color=discord.Color.red(),
        )
        embed.add_field(
            name="Reporter",
            value=f"{interaction.user.mention} (`{interaction.user.id}`)",
            inline=False
        )
        embed.add_field(
            name="Report",
            value=self.report.value,
            inline=False
        )

        await mod_log.send(embed=embed)

        await interaction.response.send_message(
            "✅ Report sent to moderators.",
            ephemeral=True
        )

# ---------- VIEW ----------
class ReportView(discord.ui.View):
    def __init__(self):
        # timeout=None is mandatory for persistent views
        super().__init__(timeout=None)

    # Fix: Use the decorator to define the button properly. 
    # Having add_item AND the decorator was causing the crash.
    @discord.ui.button(
        label="🚨 Report", 
        style=discord.ButtonStyle.danger, 
        custom_id="persistent_report_button"
    )
    async def report_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ReportModal())

# ---------- READY ----------
@bot.event
async def on_ready():
    # This registers the view so it works even after a bot restart
    bot.add_view(ReportView())
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

# ---------- COMMANDS ----------
@bot.command()
@commands.has_permissions(administrator=True)
async def setup_report(ctx):
    """Run this command once to send the report button to the channel"""
    await ctx.send(
        "🚨 **Click below to submit a report**\nOur moderation team will review it shortly.",
        view=ReportView()
    )

bot.run(TOKEN)
