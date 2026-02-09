import os
import discord
from discord.ext import commands
from datetime import datetime
from aiohttp import web # Railway needs this to stay alive

# --- CONFIG ---
TOKEN = os.getenv("TOKEN")
MOD_LOG_CHANNEL_ID = 1470335672215797843
PORT = os.getenv("PORT", 8080) # Railway provides this automatically

# ---------- THE MODAL ----------
class ReportModal(discord.ui.Modal):
    def __init__(self, rule_broken: str):
        super().__init__(title="Submit Evidence")
        self.rule_broken = rule_broken

    target_user = discord.ui.TextInput(
        label="Username of person",
        placeholder="e.g. Wumpus#0001",
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
        placeholder="Any other details?",
        style=discord.TextStyle.paragraph,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        mod_log = interaction.guild.get_channel(MOD_LOG_CHANNEL_ID)
        if not mod_log:
            return await interaction.response.send_message("❌ Log channel missing.", ephemeral=True)

        embed = discord.Embed(
            title="🚨 New User Report",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        embed.add_field(name="👤 Reporter", value=interaction.user.mention, inline=True)
        embed.add_field(name="🚫 Target User", value=f"**{self.target_user.value}**", inline=True)
        embed.add_field(name="⚖️ Rule Broken", value=f"`{self.rule_broken}`", inline=False)
        embed.add_field(name="🎬 Evidence", value=self.evidence.value, inline=False)
        
        if self.additional_info.value:
            embed.add_field(name="📝 Context", value=self.additional_info.value, inline=False)

        await mod_log.send(embed=embed)
        await interaction.response.send_message("✅ Report Submitted.", ephemeral=True)

# ---------- THE VIEW ----------
class ReportView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        custom_id="persistent_report_v3",
        placeholder="Which rule was broken?",
        options=[
            discord.SelectOption(label="Harassment", value="Harassment", emoji="🤬"),
            discord.SelectOption(label="Cheating", value="Cheating", emoji="🛡️"),
            discord.SelectOption(label="Spam", value="Spam", emoji="📢"),
            discord.SelectOption(label="Other", value="Other", emoji="❓"),
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        await interaction.response.send_modal(ReportModal(select.values[0]))

# ---------- THE BOT ----------
class TheModBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True 
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.add_view(ReportView())
        # Start a tiny web server so Railway stays happy
        app = web.Application()
        app.router.add_get("/", lambda r: web.Response(text="Bot is running!"))
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", PORT)
        await site.start()

    async def on_ready(self):
        print(f"✅ {self.user} is live on Railway.")

bot = TheModBot()

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_report(ctx):
    embed = discord.Embed(
        title="🛡️ Server Evidence Submission",
        description="Select a rule below to report a user. Evidence is required.",
        color=discord.Color.dark_grey()
    )
    await ctx.send(embed=embed, view=ReportView())
    await ctx.message.delete()

bot.run(TOKEN)
