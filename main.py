import os
import discord
from discord.ext import commands

# --- CONFIG ---
TOKEN = os.getenv("TOKEN")
MOD_LOG_CHANNEL_ID = 1470294904201678959
REPORT_CHANNEL_ID = 1470470688338084060

# ---------- THE MODAL ----------
class ReportModal(discord.ui.Modal, title="Submit a Report"):
    report_input = discord.ui.TextInput(
        label="What happened?",
        style=discord.TextStyle.paragraph,
        placeholder="Please provide as much detail as possible...",
        required=True,
        max_length=1000,
    )

    async def on_submit(self, interaction: discord.Interaction):
        mod_log = interaction.guild.get_channel(MOD_LOG_CHANNEL_ID)
        
        if not mod_log:
            return await interaction.response.send_message("❌ Mod log channel not found!", ephemeral=True)

        embed = discord.Embed(
            title="🚨 New Report Received",
            color=discord.Color.red(),
            timestamp=interaction.created_at
        )
        embed.add_field(name="Reporter", value=f"{interaction.user.mention} ({interaction.user.id})")
        embed.add_field(name="Issue", value=self.report_input.value, inline=False)
        
        await mod_log.send(embed=embed)
        await interaction.response.send_message("✅ Report sent to the staff team.", ephemeral=True)

# ---------- THE VIEW ----------
class ReportView(discord.ui.View):
    def __init__(self):
        # timeout=None is REQUIRED for persistent views
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🚨 Report", 
        style=discord.ButtonStyle.danger, 
        custom_id="persistent_report_btn_v2" # MUST HAVE A UNIQUE CUSTOM_ID
    )
    async def report_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ReportModal())

# ---------- THE BOT ----------
class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True # Fixes that warning in your logs
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        """This runs before the bot starts and makes the button work forever"""
        self.add_view(ReportView())

    async def on_ready(self):
        print(f"✅ Logged in as {self.user}")
        print(f"🚀 Persistence is active.")

bot = MyBot()

# ---------- COMMANDS ----------
@bot.command()
@commands.has_permissions(administrator=True)
async def setup_report(ctx):
    """Run !setup_report to send the button embed"""
    embed = discord.Embed(
        title="Server Report System",
        description="Click the button below to open a report modal and alert the staff.",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=ReportView())
    await ctx.message.delete()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to do that, bestie.", delete_after=5)

bot.run(TOKEN)
