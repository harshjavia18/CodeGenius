from flask import Flask, render_template, request, jsonify
import subprocess
import re

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/main")
def main_page():
    return render_template("main.html")

@app.route("/generate", methods=["POST"])
def generate_code():
    try:
        data = request.json
        question = data.get("question", "")
        language = data.get("language", "")

        # First prompt specifically for code only
        code_prompt = f"""Write a {language} function for: {question}
        STRICT REQUIREMENTS:
        1. Write ONLY pure code implementation
        2. NO comments, NO explanations
        3. NO text descriptions
        4. NO markdown
        5. Start directly with the code
        6. Include ONLY the function definition and its body
        7. NO additional text before or after the code"""

        # Get code response
        code_command = f'ollama run deepseek-coder:1.3b "{code_prompt}"'
        code_result = subprocess.run(code_command, shell=True, capture_output=True, text=True)
        
        def clean_code(output):
            # Remove markdown formatting
            output = re.sub(r"```[\w]*\n?", "", output)
            
            # Split into lines
            lines = output.split("\n")
            clean_lines = []
            
            for line in lines:
                # Skip if line is empty or contains only whitespace
                if not line.strip():
                    continue
                    
                # Skip comments and explanatory text
                if any(line.strip().startswith(x) for x in ['#', '//', '/*', '*', 'Note:', 'This', 'Here']):
                    continue
                    
                # Skip lines that look like explanations
                if re.match(r'^[A-Z][a-z]+.*[:.]$', line.strip()):
                    continue
                    
                # Keep only lines that look like code
                if re.match(r'^[\s{}\[\]()=+\-*/<>!@#$%^&*\w]', line):
                    clean_lines.append(line)

            # Join lines and clean up any remaining markdown
            code = "\n".join(clean_lines).strip()
            code = re.sub(r'[`\n]+$', '', code)  # Remove trailing backticks and newlines
            return code

        cleaned_code = clean_code(code_result.stdout)

        # Second prompt for explanation
        explain_prompt = f"""Explain this {language} code:
        {cleaned_code}
        Important instructions:
        1. Give ONLY the explanation of how the code works
        2. No code snippets or technical syntax
        3. No markdown formatting
        4. Explain the logic and purpose clearly
        5. Start directly with the explanation"""

        # Get explanation response
        explain_command = f'ollama run deepseek-coder:1.3b "{explain_prompt}"'
        explain_result = subprocess.run(explain_command, shell=True, capture_output=True, text=True)

        # Clean explanation
        cleaned_explanation = explain_result.stdout.strip()
        cleaned_explanation = re.sub(r"```.*?```", "", cleaned_explanation, flags=re.DOTALL)
        cleaned_explanation = re.sub(r"`.*?`", "", cleaned_explanation)

        if not cleaned_code.strip():
            return jsonify({"error": "No valid code generated"})

        return jsonify({
            "code": cleaned_code,
            "explanation": cleaned_explanation
        })

    except Exception as e:
        print("Error:", str(e))  # Add logging
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
