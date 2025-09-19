from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/schedule', methods=['POST'])
def schedule():
    prompt = request.form['prompt']
    # For now, just print the prompt to confirm it works
    print("User prompt:", prompt)
    return f"Received: {prompt}"

if __name__ == '__main__':
    app.run(debug=True)