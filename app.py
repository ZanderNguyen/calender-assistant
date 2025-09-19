import os
from dotenv import load_dotenv
from flask import Flask, render_template, request
from utils.gemini import parse_prompt  # 👈 Your real Gemini parser

# Load environment variables
load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/schedule', methods=['POST'])
def schedule():
    prompt = request.form['prompt']
    
    try:
        parsed = parse_prompt(prompt)
        summary = parsed.get('summary', 'No summary provided')
        start = parsed.get('start_time', 'Unknown start time')
        end = parsed.get('end_time', 'Unknown end time')

        return f"""
            <h3>Parsed Prompt:</h3>
            <p><strong>Summary:</strong> {summary}</p>
            <p><strong>Start:</strong> {start}</p>
            <p><strong>End:</strong> {end}</p>
            <a href="/">Back</a>
        """
    except Exception as e:
        return f"""
            <h3>Error Parsing Prompt</h3>
            <p>{str(e)}</p>
            <a href="/">Try Again</a>
        """

if __name__ == '__main__':
    app.run(debug=True)