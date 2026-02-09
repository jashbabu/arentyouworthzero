import os
import discord
from discord.ext import commands

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
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
        super().__init__(timeout=None)

        self.add_item(
            discord.ui.Button(
                label="🚨 Report",
                style=discord.ButtonStyle.danger,
                custom_id="persistent_report_button",
            )
        )

    @discord.ui.button(custom_id="persistent_report_button")
    async def report_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        await interaction.response.send_modal(ReportModal())


# ---------- READY ----------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    # register persistent view
    bot.add_view(ReportView())

    channel = bot.get_channel(REPORT_CHANNEL_ID)
    if channel:
        await channel.send(
            "🚨 **Click below to submit a report**",
            view=ReportView()
        )


bot.run(TOKEN)
