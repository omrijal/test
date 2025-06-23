# main.py
import discord
import pandas as pd
import os
import asyncio
from flask import Flask, render_template, request, redirect, flash
from threading import Thread

# ---- FLASK SETUP ----
app = Flask(__name__)
app.secret_key = 'secret'

EXCEL_FILE = 'availability.xlsx'
time_slots = ['5:30 AM', '7:30 AM', '9:45 PM', '10:45 PM']
avail_dates = ['April 9', 'April 10', 'April 11', 'April 12', 'April 13', 'April 14']

if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame('', index=time_slots, columns=avail_dates)
    df.to_excel(EXCEL_FILE)

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    email = request.form.get('email')
    job = request.form.get('job')
    date = request.form.get('date')
    time = request.form.get('time')
    availability = request.form.get('availability')
    hours = request.form.get('hours')
    start_from_15 = request.form.get('start')

    if not all([name, email, job, date, time, availability, hours, start_from_15]):
        flash("All fields are required.")
        return redirect('/')

    new_info = f"Name: {name} | Email: {email} | Job: {job} | Availability: {availability} | Hours: {hours} | Start from 15: {start_from_15}"

    try:
        df = pd.read_excel(EXCEL_FILE, index_col=0)
    except:
        df = pd.DataFrame('', index=time_slots, columns=avail_dates)

    existing_info = str(df.at[time, date]) if date in df.columns else ""
    if existing_info.strip() != "" and existing_info.strip().lower() != "nan":
        df.at[time, date] = existing_info + ",\n" + new_info
    else:
        df.at[time, date] = new_info

    df.to_excel(EXCEL_FILE)
    flash("Form submitted successfully!")
    return redirect('/')


# ---- DISCORD BOT SETUP ----
TOKEN = os.environ.get('DISCORD_TOKEN')
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
            await message.channel.send("⚠️ Excel file not found.")
            return

        try:
            df = pd.read_excel(EXCEL_FILE, index_col=0)
            response = f"📅 **Interviews on {excel_date}:**\n"

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


# ---- RUN BOTH TOGETHER ----
def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == '__main__':
    Thread(target=run_flask).start()
    client.run(TOKEN)
