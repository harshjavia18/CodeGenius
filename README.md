# Code Generation Web App

## 🚀 Overview
This is a Flask-based web application that generates code functions based on user prompts using an AI model (e.g., `ollama deepseek-coder`). The app provides a frontend interface where users can input a programming question and receive a function implementation without explanations or extra text.

---

## 🛠️ Setup Instructions

### 1️⃣ Prerequisites
Make sure you have the following installed:
- Python 3.8+
- Flask
- Node.js (if additional frontend modifications are needed)
- [Ollama](https://ollama.com) installed with the `deepseek-coder` model

### 2️⃣ Clone the Repository
```sh
git clone <repository-url>
cd <project-folder>
```

### 3️⃣ Install Dependencies
```sh
pip install flask
```

### 4️⃣ Run the Application
```sh
python app.py
```

The Flask app will start, and you can access it in your browser at:
```
http://127.0.0.1:5000/
```

---

## 📂 Project Structure
```
📦 project-folder
│── 📜 app.py         # Flask backend
│── 📜 templates/
│   ├── index.html    # Home page
│   ├── main.html     # Main content page
│── 📜 static/
│   ├── script.js     # Handles frontend interactions
│   ├── styles.css    # UI styling (if any)
│── 📜 README.md      # Documentation
```

---

## 🎯 Features
✅ User inputs a programming-related question and selects a language
✅ AI model (`deepseek-coder`) generates a function implementation
✅ Ensures only function code is returned, without extra explanations
✅ Simple and interactive frontend

---

## 📌 API Endpoints
### 1️⃣ **Homepage**
```
GET /
```
Loads the main `index.html` page.

### 2️⃣ **Main Page**
```
GET /main
```
Loads `main.html`.

### 3️⃣ **Generate Code**
```
POST /generate
```
**Request Body (JSON):**
```json
{
  "question": "Find the first non-repeating character in a string",
  "language": "Python"
}
```

**Response (JSON):**
```json
{
  "answer": "def find_first_non_repeating(s): ..."
}
```

---

## 🛠️ How It Works
1️⃣ The frontend (`index.html` & `script.js`) takes user input and sends a request to `/generate`.
2️⃣ `app.py` processes the request and queries `ollama deepseek-coder`.
3️⃣ AI generates function code, and `app.py` cleans unnecessary text before returning it.
4️⃣ The cleaned function is displayed on the webpage.

---

## 🐞 Troubleshooting
- **No response from AI?** Ensure `ollama` and the model are correctly installed.
- **Flask app not running?** Check if another process is using port 5000 or try `flask run`.
- **Wrong output format?** Ensure `app.py` has the latest regex cleaning function.

---

## 🤝 Contributions
Feel free to submit issues or pull requests to improve this project!

---

## 📜 License
MIT License - Feel free to modify and use this project as needed!

---

Happy Coding! 🚀

