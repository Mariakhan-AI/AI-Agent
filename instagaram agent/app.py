from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import os
from flask_cors import CORS
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)


# Configure Gemini API
GEMINI_API_KEY = "AIzaSyD-j-sfs-pQKm2o-Abeboh5gM2NY6vweFM"
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/')
def home():
    # If you want to use a separate HTML file, create templates/index.html
    # and use: return render_template('index.html')
    # For now, we'll serve the embedded template
    return render_template('index.html')

@app.route('/generate_caption', methods=['POST'])
def generate_caption():
    try:
        if not GEMINI_API_KEY:
            return jsonify({
                'success': False,
                'error': 'Gemini API key not configured. Please set GEMINI_API_KEY environment variable.'
            })
        
        data = request.json
        description = data.get('description', '')
        tone = data.get('tone', 'casual')
        hashtags = data.get('hashtags', 'yes')
        keywords = data.get('keywords', '')
        
        if not description:
            return jsonify({
                'success': False,
                'error': 'Please provide a description for your post.'
            })
        
        # Create the prompt for Gemini
        prompt = f"""
        Create 3 engaging Instagram captions for a post about: {description}
        Requirements:
        - Tone: {tone}
        - Hashtags: {hashtags}
        - Keywords to include: {keywords if keywords else 'None'}
        
        Guidelines:
        - Make each caption unique and engaging
        - Include emojis where appropriate
        - Keep captions concise but compelling
        - If hashtags are requested, include 5-15 relevant hashtags
        - Make sure captions encourage engagement (likes, comments, shares)
        - Consider current Instagram trends and best practices
        
        """
        
        # Generate content using Gemini
        response = model.generate_content(prompt)
        generated_text = response.text
        
        # Split the response into individual captions
        captions = []
        if generated_text:
            # Split by common separators and clean up
            raw_captions = generated_text.split('\n\n')
            for caption in raw_captions:
                caption = caption.strip()
                if caption and len(caption) > 20:  # Filter out very short responses
                    # Remove any numbering or prefixes
                    caption = caption.replace('Caption 1:', '').replace('Caption 2:', '').replace('Caption 3:', '')
                    caption = caption.replace('Option 1:', '').replace('Option 2:', '').replace('Option 3:', '')
                    caption = caption.strip()
                    if caption:
                        captions.append(caption)
        
        # Ensure we have at least 3 captions
        if len(captions) < 3:
            # If we don't have enough captions, generate more
            additional_prompt = f"Create {3 - len(captions)} more Instagram captions for: {description}. Tone: {tone}. Make them different from previous ones."
            additional_response = model.generate_content(additional_prompt)
            if additional_response.text:
                additional_captions = additional_response.text.split('\n\n')
                for caption in additional_captions:
                    caption = caption.strip()
                    if caption and len(caption) > 20:
                        captions.append(caption)
                    if len(captions) >= 3:
                        break
        
        # Take only the first 3 captions
        captions = captions[:3]
        
        if not captions:
            return jsonify({
                'success': False,
                'error': 'Failed to generate captions. Please try again with a different description.'
            })
        
        return jsonify({
            'success': True,
            'captions': captions
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        })

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Instagram Caption Craft AI is running!'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7860))
    app.run(host='0.0.0.0', port=port)