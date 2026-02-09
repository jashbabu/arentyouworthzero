import os
import discord
from discord.ext import commands

TOKEN = os.getenv("TOKEN")

INTENTS = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=INTENTS)

MOD_LOG_CHANNEL_ID = 1470294904201678959  # 🔴 REPLACE with your mod-log channel ID
REPORT_CHANNEL_ID = 1470470688338084060   # 🔴 REPLACE with channel where button lives


# ---------- MODAL ----------
class ReportModal(discord.ui.Modal, title="Submit a Report"):
    reason = discord.ui.TextInput(
        label="What happened?",
        style=discord.TextStyle.paragraph,
        placeholder="Explain the situation in detail",
        required=True,
        max_length=1000,
    )

    async def on_submit(self, interaction: discord.Interaction):
        mod_log = interaction.guild.get_channel(MOD_LOG_CHANNEL_ID)

        embed = discord.Embed(
            title="🚨 New Report",
            color=discord.Color.red(),
        )
        embed.add_field(name="Reporter", value=interaction.user.mention, inline=False)
        embed.add_field(name="Report", value=self.reason.value, inline=False)
        embed.set_footer(text=f"User ID: {interaction.user.id}")

        await mod_log.send(embed=embed)

        await interaction.response.send_message(
            "✅ Report submitted. Mods will review it.",
            ephemeral=True
        )


# ---------- VIEW (BUTTON) ----------
class ReportView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🚨 Report",
        style=discord.ButtonStyle.danger,
        custom_id="persistent_report_button",
    )
    async def report_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        await interaction.response.send_modal(ReportModal())


# ---------- READY ----------
@bot.event
async def on_ready():
    bot.add_view(ReportView())
    print(f"Logged in as {bot.user}")

    channel = bot.get_channel(REPORT_CHANNEL_ID)
    if channel:
        await channel.send(
            "Click the button below to submit a report:",
            view=ReportView()
        )


bot.run(TOKEN)
