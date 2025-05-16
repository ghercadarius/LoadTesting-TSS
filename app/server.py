from datetime import datetime

from transformers import pipeline
from flask import Flask, request, jsonify, render_template_string, render_template
import os
import torch

portNumber = int(os.environ.get("PORT_NUMBER"))

app = Flask(__name__)

requests_served = 0

class Summarizer:
    def __init__(self):
        self.summarizer = pipeline("summarization", model="t5-base", tokenizer="t5-base", framework="pt")

    def summarize(self, text):
        print("Summarizing text..." + text)
        maxLen = max(int(len(text.split(" ")) * 0.6), 2)
        return self.summarizer(text, max_length=maxLen, min_length=1, do_sample=False)[0]["summary_text"]

chatBot = Summarizer()
print("Starting server...")
@app.route("/", methods=["GET"])
def home():
    global requests_served
    requests_served += 1
    return render_template_string('''
    <!DOCTYPE html>
<html>
<head>
    <title>Summarizer Home</title>
</head>
<body>
    <h1>Welcome to the Text Summarizer</h1>
    <p>Click below to summarize your text. Project made by Gherca Darius for the Cloud Computing Tehnologies for ML Workloads class</p>
    <a href="/summarize">Go to Summarizer</a>
    <a href="/requests-counter">See number of served requests</a> 
</body>
</html>

    ''')

@app.route("/summarize", methods=["GET", "POST"])
def summarize():
    global requests_served
    if request.method == "GET":
        requests_served += 1
        return render_template_string('''
        <!DOCTYPE html>
<html>
<head>
    <title>Generate Summary</title>
</head>
<body>
    <h1>Text Summarizer</h1>
    <form method="POST" action="/summarize">
        <label for="text">Enter your text:</label><br>
        <textarea id="text" name="text" rows="10" cols="50" required></textarea><br><br>
        <button type="submit">Summarize</button>
    </form>
</body>
</html>
''')
    else:
        requests_served += 1
        text = request.form.get("text")
        summary = chatBot.summarize(text)
        return render_template_string(f'''
        <!DOCTYPE html>
<html>
<head>
    <title>Summary Result</title>
</head>
<body>
    <h1>Summary Result</h1>
    <h2>Original Text:</h2>
    <p>{text}</p>
    <h2>Summary:</h2>
    <p>{summary}</p>
    <a href="/summarize">Summarize Another Text</a>
</body>
</html>
        ''')
    
@app.route("/requests-counter", methods=["GET"])
def health_check():
    global requests_served
    return render_template_string(f'''
    <!DOCTYPE html>
<html>
<head>
    <title>Number of requests served</title>
</head>
<body>
    <p>{requests_served}</p>
    <a href="/reset">Reset counter</a>
</body>
</html>
    ''')

@app.route("/reset", methods=["GET"])
def reset():
    global requests_served
    requests_served = 0
    return render_template_string(f'''
    <!DOCTYPE html>
<html>
<head>
    <title>Number of requests served</title>
</head>
<body>
    <p>Reset counter of served requests to 0</p>
    <a href="/requests-counter">See number of served requests</a>
</body>
</html>
    ''')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=portNumber)
