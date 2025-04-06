from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
import subprocess
import re
from flask_socketio import SocketIO
import json
import os
from flask_cors import CORS
import threading
import queue
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///codegenius.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure key

db = SQLAlchemy(app)

# Ensure static directory exists
os.makedirs('static/images', exist_ok=True)

# Global response cache
response_cache = {}
cache_timeout = 300  # 5 minutes

# Database Models
class UserActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    profession = db.Column(db.String(50), nullable=False)
    language = db.Column(db.String(50), nullable=False)
    query = db.Column(db.Text, nullable=False)
    ip_address = db.Column(db.String(50))

def run_model_with_timeout(command, timeout=45):
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        return "Response took too long. Please try a simpler query or break down your request into smaller parts."

def clean_code(output):
    # Remove markdown formatting
    output = re.sub(r"```[\w]*\n?", "", output)
    output = re.sub(r"`", "", output)
    
    # Split into lines and clean
    lines = output.split("\n")
    clean_lines = []
    
    for line in lines:
        if line.strip():
            clean_lines.append(line)

    return "\n".join(clean_lines).strip()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/profession')
def profession():
    return render_template('profession.html')

@app.route('/language')
def language():
    return render_template('language.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    question = data.get('question', '')
    language = data.get('language', '')
    profession = data.get('profession', '')

    # Track user activity
    activity = UserActivity(
        profession=profession,
        language=language,
        query=question,
        ip_address=request.remote_addr
    )
    db.session.add(activity)
    db.session.commit()

    # Check cache first
    cache_key = f"{question}_{language}_{profession}"
    if cache_key in response_cache:
        return jsonify(response_cache[cache_key])

    # Optimize prompts for faster responses
    profession_prompts = {
        "student": "Write simple, beginner code with basic comments.",
        "professor": "Write efficient code, academic focus.",
        "developer": "Write optimized production code."
    }

    # More concise prompt
    code_prompt = f"""Write short {language} code: {question}
    - {profession_prompts[profession]}
    - Include imports
    - Brief comments
    Code only:"""

    # Run model with increased timeout
    code_result = run_model_with_timeout(
        f'ollama run deepseek-coder:1.3b "{code_prompt}"',
        timeout=45
    )
    
    cleaned_code = clean_code(code_result)

    # Shorter explanation prompt
    explain_prompt = f"Explain briefly for {profession}: {cleaned_code}"

    # Get explanation with timeout
    explain_result = run_model_with_timeout(
        f'ollama run deepseek-coder:1.3b "{explain_prompt}"',
        timeout=30
    )

    # Clean explanation
    cleaned_explanation = explain_result.strip()
    cleaned_explanation = re.sub(r"```.*?```", "", cleaned_explanation, flags=re.DOTALL)
    cleaned_explanation = re.sub(r"`", "", cleaned_explanation)

    if not cleaned_code.strip():
        return jsonify({"error": "No valid code generated. Please try a simpler request."})

    response = {
        "code": cleaned_code,
        "explanation": cleaned_explanation
    }

    # Cache the response
    response_cache[cache_key] = response

    return jsonify(response)

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        message = data.get("message", "")
        
        # Check cache first
        cache_key = f"chat_{message}"
        if cache_key in response_cache:
            return jsonify({"response": response_cache[cache_key]})

        # Ultra-concise prompt
        chat_prompt = f"Answer briefly: {message}"

        # Get chat response with increased timeout
        chat_result = run_model_with_timeout(
            f'ollama run deepseek-r1:1.5b "{chat_prompt}"',
            timeout=20
        )

        # Clean and format response
        response = chat_result.strip()
        response = response.replace('\n\n', '<br>')
        response = response.replace('\n', ' ')
        
        # Cache the response
        response_cache[cache_key] = response

        return jsonify({"response": response})

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": "Sorry, I couldn't process that. Please try a simpler question."})

# Periodic cache cleanup
def cleanup_cache():
    while True:
        socketio.sleep(cache_timeout)
        response_cache.clear()

@socketio.on('connect')
def handle_connect():
    if not hasattr(app, 'cleanup_thread'):
        app.cleanup_thread = socketio.start_background_task(cleanup_cache)

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)
