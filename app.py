from flask import Flask, render_template, request
from utils.gemini import parse_prompt  # 👈 Import your parser

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/schedule', methods=['POST'])
def schedule():
    prompt = request.form['prompt']
    parsed = parse_prompt(prompt)

    # Show parsed output for now
    return f"""
        <h3>Parsed Prompt:</h3>
        <p><strong>Summary:</strong> {parsed['summary']}</p>
        <p><strong>Start:</strong> {parsed['start_time']}</p>
        <p><strong>End:</strong> {parsed['end_time']}</p>
    """

if __name__ == '__main__':
    app.run(debug=True)