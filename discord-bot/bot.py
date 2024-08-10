import os

import discord
from discord import app_commands
from discord.ext import commands

# Intents
intents = discord.Intents.default()
intents.message_content = True

# Set up the bot
bot = commands.Bot(command_prefix="/", intents=intents)

# Channel ID where the bot listens for the /register command
SPECIFIC_CHANNEL_ID = 1271580738692579469  # Replace with your channel ID


class RegistrationModal(discord.ui.Modal, title="Registration"):
    match_code = discord.ui.TextInput(
        label="Match Code",
        style=discord.TextStyle.short,
        placeholder="Enter your match code",
    )
    auth_code = discord.ui.TextInput(
        label="Authentication Code",
        style=discord.TextStyle.short,
        placeholder="Enter your authentication code",
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Handle the user's input
        await interaction.response.send_message(
            f"Thank you! Your match code is `{self.match_code}` and your authentication code is `{self.auth_code}`.",
            ephemeral=True,
        )


@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")


@bot.command()
async def register(ctx):
    if ctx.channel.id != SPECIFIC_CHANNEL_ID:
        await ctx.send("Please use the correct channel to register.", ephemeral=True)
        return

    # Create and send the modal
    modal = RegistrationModal()
    await ctx.interaction.response.send_modal(modal)


# Run the bot
bot.run(os.environ.get("DISCORD_TOKEN"))
