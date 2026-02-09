import os
import discord
from discord.ext import commands
from datetime import datetime

# --- CONFIG (Change these IDs) ---
TOKEN = os.getenv("TOKEN")
MOD_LOG_CHANNEL_ID = 1470294904201678959
REPORT_CHANNEL_ID = 1470470688338084060

# --- THE MODAL ---
class ReportModal(discord.ui.Modal, title="📝 Submit a Server Report"):
    # This is the text box users see
    reason = discord.ui.TextInput(
        label="What's the tea?",
        placeholder="Describe the issue/user in detail...",
        style=discord.TextStyle.paragraph,
        min_length=10,
        max_length=1000,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Find the channel to send the report to
        log_channel = interaction.guild.get_channel(MOD_LOG_CHANNEL_ID)
        
        if not log_channel:
            return await interaction.response.send_message("❌ Error: Log channel not found. Tell an Admin!", ephemeral=True)

        # Create a sleek embed for the mods
        embed = discord.Embed(
            title="🚨 New Report Received",
            color=discord.Color.from_rgb(255, 60, 60), # Neon red vibes
            timestamp=datetime.now()
        )
        embed.add_field(name="👤 Reporter", value=f"{interaction.user.mention} (`{interaction.user.id}`)", inline=False)
        embed.add_field(name="📄 Details", value=self.reason.value, inline=False)
        embed.set_footer(text=f"Report System • {interaction.guild.name}")

        await log_channel.send(embed=embed)
        
        # Confirm to the user (ephemeral = only they see it)
        await interaction.response.send_message("✅ Report sent. The mods are on it!", ephemeral=True)

# --- THE PERSISTENT VIEW ---
class PersistentReportView(discord.ui.View):
    def __init__(self):
        # timeout=None makes the button work even after the bot restarts
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Report User", 
        style=discord.ButtonStyle.danger, 
        custom_id="report_button_v1", # This ID is the key to persistence
        emoji="🚨"
    )
    async def report_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Open the modal when they click the button
        await interaction.response.send_modal(ReportModal())

# --- THE BOT SETUP ---
class TheModBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True  # Required for prefix commands
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        # This is where we tell the bot to "listen" for the button constantly
        self.add_view(PersistentReportView())

    async def on_ready(self):
        print(f"✅ Main character energy: {self.user} is online")
        print(f"🔗 Log Channel: {MOD_LOG_CHANNEL_ID}")

# Init the bot
bot = TheModBot()

# --- COMMANDS ---
@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    """Sends the initial report message with the button"""
    embed = discord.Embed(
        title="🛡️ Server Safety",
        description=(
            "Notice something breaking the rules? Use the button below to report it.\n\n"
            "**Note:** False reporting can lead to a ban. Be real with us."
        ),
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=PersistentReportView())
    await ctx.message.delete() # Clean up the command message

# Run it
if __name__ == "__main__":
    bot.run(TOKEN)
