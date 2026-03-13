"""
FitSmart AI - Personal Fitness Plan Generator
Backend powered by Flask + Groq API (free, no card needed)
"""

import os
import requests
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Get Groq API key from .env
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found. Please add it to your .env file.")


@app.route("/", methods=["GET"])
def index():
    """Display the main input form page."""
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    """
    Receive user fitness details, build a prompt,
    call Groq API, and return the plan as JSON.
    """
    try:
        # Get form data sent as JSON from the frontend
        data = request.get_json()

        # Extract individual fields
        age        = data.get("age", "").strip()
        gender     = data.get("gender", "").strip()
        goal       = data.get("goal", "").strip()
        preference = data.get("preference", "").strip()
        time       = data.get("time", "").strip()

        # Basic server-side validation
        if not all([age, gender, goal, preference, time]):
            return jsonify({"error": "All fields are required."}), 400

        # Construct the prompt
        prompt = (
            f"Create a beginner-friendly weekly fitness plan for a {age}-year-old {gender} "
            f"whose goal is {goal}. They prefer {preference} workouts and can exercise {time} "
            f"minutes per day. Include a weekly workout schedule, exercises, safety tips, and "
            f"lifestyle advice. Keep it simple and suitable for beginners."
        )

        # Call Groq API (free, ultra-fast)
        response = requests.post(
            url="https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful, friendly personal fitness coach specializing in beginner-safe workout plans."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 1500
            }
        )

        # Parse the response
        result = response.json()

        # Check for API-level errors
        if "error" in result:
            return jsonify({"error": result["error"].get("message", "Unknown API error")}), 500

        # Extract the generated text
        fitness_plan = result["choices"][0]["message"]["content"]

        # Return the fitness plan as JSON
        return jsonify({"plan": fitness_plan})

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


# Run the Flask development server
if __name__ == "__main__":
    app.run(debug=True)