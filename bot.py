# bot.py
import discord
import pandas as pd
import os
import asyncio

TOKEN = os.environ.get('DISCORD_TOKEN') # Secure token storage for Render
EXCEL_FILE = 'availability.xlsx'

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

date_map = {
    '9 april': 'April 9',
    '10 april': 'April 10',
    '11 april': 'April 11',
    '12 april': 'April 12',
    '13 april': 'April 13',
    '14 april': 'April 14'
}

time_slots = ['5:30 AM', '7:30 AM', '9:45 PM', '10:45 PM']

@client.event
async def on_ready():
    print(f'Bot connected as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    content = message.content.strip().lower()

    if content.startswith("iv"):
        query = content.replace("iv", "").strip()
        excel_date = date_map.get(query)

        if not excel_date:
            await message.channel.send("❌ Date not recognized. Try formats like 'Iv 9 April'")
            return

        if not os.path.exists(EXCEL_FILE):
            await message.channel.send("⚠️ Excel file not found. No interviews saved yet.")
            return

        try:
            df = pd.read_excel(EXCEL_FILE, index_col=0)
            response = f" **Interviews on {excel_date}:**\n"

            for time in time_slots:
                response += f"\n\n**🕒 {time}**"
                entry = df.at[time, excel_date] if excel_date in df.columns else ""
                if pd.isna(entry) or entry.strip() == "":
                    response += "\nNo one scheduled"
                else:
                    candidates = [c.strip() for c in entry.strip().split(',\n') if c.strip().lower() != 'nan']
                    for idx, candidate in enumerate(candidates, start=1):
                        lines = candidate.split('|')
                        formatted = f"\n\n**👨‍💼Candidate {idx}**"
                        for field in lines:
                            key_val = field.strip().split(':', 1)
                            if len(key_val) == 2:
                                formatted += f"\n{key_val[0].strip()}: {key_val[1].strip()}"
                        response += formatted

            await message.channel.send(response)

        except Exception as e:
            await message.channel.send(f"⚠️ Error reading data: {str(e)}")

client.run(TOKEN)
