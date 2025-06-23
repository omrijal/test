from flask import Flask, render_template, request, redirect, flash
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'secret'

# Save Excel in current directory for compatibility with Render
EXCEL_FILE = 'availability.xlsx'

# Time slots and dates mapping
time_slots = ['5:30 AM', '7:30 AM', '9:45 PM', '10:45 PM']
avail_dates = ['April 9', 'April 10', 'April 11', 'April 12', 'April 13', 'April 14']

# Create Excel file only once
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
    except Exception:
        df = pd.DataFrame('', index=time_slots, columns=avail_dates)

    # Append or insert info
    existing_info = str(df.at[time, date]) if date in df.columns else ""
    if existing_info.strip() != "" and existing_info.strip().lower() != "nan":
        df.at[time, date] = existing_info + ",\n" + new_info
    else:
        df.at[time, date] = new_info

    df.to_excel(EXCEL_FILE)

    flash("Form submitted successfully!")
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
