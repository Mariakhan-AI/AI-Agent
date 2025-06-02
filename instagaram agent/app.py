from flask import Flask, request, render_template, jsonify
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import google.generativeai as genai
except ModuleNotFoundError:
    raise ImportError("Install with: pip install google-generativeai")

# Set API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise EnvironmentError("GEMINI_API_KEY is not set in .env or Vercel dashboard.")

genai.configure(api_key=GEMINI_API_KEY)

# Create Flask app
app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    prompt = data.get("prompt")
    niche = data.get("niche")

    if not prompt or not niche:
        return jsonify({"error": "Missing prompt or niche"}), 400

    try:
        custom_prompt = (
            f"You are an expert Instagram marketer. "
            f"Write a short, viral, engaging Instagram caption for the '{niche}' niche. "
            f"Topic: '{prompt}'. Use emojis. Avoid hashtags."
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
        caption = response.text.strip() if hasattr(response, "text") else "❌ Invalid response"

        return jsonify({"caption": caption})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Required for Vercel
handler = app
