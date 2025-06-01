from flask import Flask, request, render_template, jsonify
import os
from dotenv import load_dotenv

try:
    import google.generativeai as genai
except ModuleNotFoundError as e:
    raise ImportError("google.generativeai is not installed. Please install it with 'pip install google-generativeai'") from e

# Load environment variables from .env
load_dotenv()

# Configure Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise EnvironmentError("GEMINI_API_KEY not set in environment variables.")

genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__)

# Route: Home page
@app.route("/")
def index():
    return render_template("index.html")

# Route: Generate Instagram caption
@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    prompt = data.get("prompt")
    niche = data.get("niche")

    if not prompt or not niche:
        return jsonify({"error": "Missing prompt or niche"}), 400

    try:
        # Create custom prompt
        custom_prompt = (
            f"You are an expert Instagram marketer. "
            f"Write a short, viral, engaging Instagram caption for the '{niche}' niche. "
            f"The topic is: '{prompt}'. "
            f"Use a human tone, include emojis, and avoid hashtags."
        )

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 50,
                "top_p": 0.95,
                "top_k": 40
            }
        )

        response = model.generate_content(custom_prompt)
        caption = response.text.strip() if hasattr(response, 'text') else "Error: Invalid response format"
        return jsonify({"caption": caption})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
