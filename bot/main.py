import discord
from discord.ext import commands
import requests
import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!')

@bot.event()
async def on_ready():
    print(f'{bot.user} is now online!')

@bot.command()
async def update(ctx, target, timing):
    valid_targets = ['all', 'project', 'group']
    if target not in valid_targets:
        await ctx.send(f"Invalid target. Use: {', '.join(valid_targets)}")
        return
    
    if timing == 'now':
        delay = 0
    else:
        try:
            delay = int(timing)
        except ValueError:
            await ctx.send("Invalid timing. Use 'now' or number of hours")
            return
    
    webhook_url = os.getenv("WEBHOOK_URL")
    payload = {
        "target": target,
        "delay": delay,
        "discord_webhook": os.getenv("DC_WEBHOOK_URL")
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            if delay == 0:
                await ctx.send(f"✅ Update started for: **{target}**\nLogs will be posted here when complete.")
            else:
                await ctx.send(f"⏰ Update scheduled for **{target}** in {delay} hours\nLogs will be posted here when complete.")
        else:
            await ctx.send(f"❌ Failed to trigger update: {response.status_code}")
    
    except Exception as e:
        await ctx.send(f"❌ Error connecting to server: {str(e)}")

bot.run(os.getenv('TOKEN'))
