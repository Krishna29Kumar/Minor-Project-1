from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

client = OpenAI(api_key="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")

# Chat models removed to avoid heavy dependencies and runtime issues.
# (Fallback responses are used instead.)
chat_history_ids = None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_input = request.json.get("message")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a compassionate emotional support assistant. Respond with empathy, warmth, and helpful guidance."
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            temperature=0.7
        )

        reply = response.choices[0].message.content

        return jsonify({"reply": reply})

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"reply": "Server error occurred."}), 500

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

if __name__ == "__main__":
    app.run(debug=True)
