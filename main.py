import discord
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")
MOD_LOG_CHANNEL_ID = 1470294904201678959  # mod-log channel ID

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ---------- MODAL ----------
class ReportModal(discord.ui.Modal):
    def __init__(self, rule_selected: str):
        super().__init__(title="Report Details")
        self.rule_selected = rule_selected

        self.details = discord.ui.TextInput(
            label="Explain what happened",
            style=discord.TextStyle.paragraph,
            placeholder="Give full details in your own words",
            required=True,
            max_length=800
        )

        self.proof = discord.ui.TextInput(
            label="Proof (optional)",
            placeholder="Message link / image link",
            required=False
        )

        self.add_item(self.details)
        self.add_item(self.proof)

    async def on_submit(self, interaction: discord.Interaction):
        channel = bot.get_channel(MOD_LOG_CHANNEL_ID)

        embed = discord.Embed(
            title="📩 New Report",
            color=discord.Color.red()
        )
        embed.add_field(name="Reporter", value=interaction.user.mention, inline=False)
        embed.add_field(name="Rule Selected", value=self.rule_selected, inline=False)
        embed.add_field(name="Details", value=self.details.value, inline=False)
        embed.add_field(name="Proof", value=self.proof.value or "None", inline=False)

        await channel.send(embed=embed)
        await interaction.response.send_message(
            "✅ Report submitted successfully.",
            ephemeral=True
        )

# ---------- DROPDOWN ----------
class RuleSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Harassment / Insults", emoji="🗯️"),
            discord.SelectOption(label="Threats / Violence", emoji="⚠️"),
            discord.SelectOption(label="Hate Speech", emoji="🚫"),
            discord.SelectOption(label="Spam / Scam", emoji="🧨"),
            discord.SelectOption(label="Other", emoji="❓")
        ]
        super().__init__(
            placeholder="Select the rule that was broken",
            options=options,
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction: discord.Interaction):
        selected = self.values[0]
        await interaction.response.send_modal(ReportModal(selected))

# ---------- VIEW ----------
class ReportView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RuleSelect())

# ---------- READY ----------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    bot.add_view(ReportView())

# ---------- PANEL COMMAND ----------
@bot.command()
@commands.has_permissions(administrator=True)
async def reportpanel(ctx):
    embed = discord.Embed(
        title="📩 Report a Member",
        description="Select the rule broken, then fill in the details.\nFalse reports will be punished.",
        color=discord.Color.orange()
    )
    await ctx.send(embed=embed, view=ReportView())

bot.run(TOKEN)
