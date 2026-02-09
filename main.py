import os
import discord
from discord.ext import commands
from datetime import datetime

# --- CONFIG ---
TOKEN = os.getenv("TOKEN")
MOD_LOG_CHANNEL_ID = 1470294904201678959

# ---------- THE MODAL ----------
class ReportModal(discord.ui.Modal):
    def __init__(self, rule_broken: str):
        super().__init__(title="Submit Evidence")
        self.rule_broken = rule_broken

    target_user = discord.ui.TextInput(
        label="Username of person",
        placeholder="e.g. Wumpus#0001 or @username",
        style=discord.TextStyle.short,
        required=True
    )

    evidence = discord.ui.TextInput(
        label="Photo/clip using streamable",
        placeholder="https://streamable.com/...",
        style=discord.TextStyle.short,
        required=True,
        min_length=10
    )

    additional_info = discord.ui.TextInput(
        label="Extra Context",
        placeholder="Any other details the mods should know?",
        style=discord.TextStyle.paragraph,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        mod_log = interaction.guild.get_channel(MOD_LOG_CHANNEL_ID)
        
        if not mod_log:
            return await interaction.response.send_message("❌ Error: Mod log channel not found.", ephemeral=True)

        # Build the sleek mod-log embed
        embed = discord.Embed(
            title="🚨 New User Report",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        embed.add_field(name="👤 Reporter", value=f"{interaction.user.mention} (`{interaction.user.id}`)", inline=True)
        embed.add_field(name="🚫 Target User", value=f"**{self.target_user.value}**", inline=True)
        embed.add_field(name="⚖️ Rule Broken", value=f"`{self.rule_broken}`", inline=False)
        embed.add_field(name="🎬 Evidence", value=self.evidence.value, inline=False)
        
        if self.additional_info.value:
            embed.add_field(name="📝 Context", value=self.additional_info.value, inline=False)

        await mod_log.send(embed=embed)
        
        await interaction.response.send_message(
            "✅ **Report Submitted.** Our team will review the Streamable clip and take action.", 
            ephemeral=True
        )

# ---------- THE VIEW (With Dropdown) ----------
class ReportView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        custom_id="persistent_report_v3",
        placeholder="Which rule was broken?",
        options=[
            discord.SelectOption(label="Harassment / Toxicity", value="Harassment", emoji="🤬"),
            discord.SelectOption(label="Cheating / Exploiting", value="Cheating", emoji="🛡️"),
            discord.SelectOption(label="Chat Spam / Advertising", value="Spam", emoji="📢"),
            discord.SelectOption(label="Inappropriate Content", value="NSFW/Inappropriate", emoji="🔞"),
            discord.SelectOption(label="Other Rule Violation", value="Other", emoji="❓"),
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        # Passes the selected rule into the Modal
        await interaction.response.send_modal(ReportModal(select.values[0]))

# ---------- THE BOT ----------
class TheModBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True 
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Keep the view alive after restarts
        self.add_view(ReportView())

    async def on_ready(self):
        print(f"✅ {self.user} is locked and loaded.")
        print("💡 Use !setup_report to spawn the system.")

bot = TheModBot()

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_report(ctx):
    """Run this in the channel where you want the report system to live"""
    embed = discord.Embed(
        title="🛡️ Server Evidence Submission",
        description=(
            "To report a player, select the rule they broke from the dropdown below.\n\n"
            "**Requirements:**\n"
            "• Valid Username of the offender\n"
            "• Streamable link for video evidence"
        ),
        color=discord.Color.from_rgb(43, 45, 49) # Dark mode aesthetic
    )
    await ctx.send(embed=embed, view=ReportView())
    await ctx.message.delete()

bot.run(TOKEN)
