from flask import Flask, jsonify
import openai
import os

app = Flask(__name__)

# Retrieve the API key from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/')
def home():
    return "Hello, World!"

@app.route('/test_openai')
def test_openai():
    try:
        response = openai.Completion.create(
            model="text-davinci-002",
            prompt="Translate the following English text to French: 'Hello, World!'",
            max_tokens=60
        )
        return jsonify(response.data)
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Important to bind to 0.0.0.0 to work on Replit
