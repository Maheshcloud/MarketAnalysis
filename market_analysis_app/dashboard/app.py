# market_analysis_app/dashboard/app.py

from flask import Flask, render_template
import json

app = Flask(__name__)

@app.route('/')
def dashboard():
    # Read the latest analysis data from a file
    try:
        with open('dashboard_data.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"message": "No analysis data available yet."}

    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
