import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import PyPDF2
import re
import tempfile
from elevenlabs import play
from elevenlabs.client import ElevenLabs

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Set up ElevenLabs API key
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    raise ValueError("ELEVENLABS_API_KEY is not set in the .env file")

# Set the API key for ElevenLabs
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

def clean_extracted_text(text):
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_text(file_path):
    text = ""
    if file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
    elif file_path.endswith(".pdf"):
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text + " "
    return clean_extracted_text(text)

@app.route("/api/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    if file and (file.filename.endswith(".txt") or file.filename.endswith(".pdf")):
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        text = extract_text(file_path)
        return jsonify({"text": text})
    
    return jsonify({"error": "Invalid file type"}), 400

@app.route("/api/generate-speech", methods=["POST"])
def generate_speech():
    data = request.json
    text = data.get("text")
    
    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        audio_generator = client.generate(
            text=text,
            voice="Rachel",
            model="eleven_multilingual_v2"
        )
        
        # Consume the generator and concatenate the chunks
        audio_data = b''.join(chunk for chunk in audio_generator)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_file.write(audio_data)
            temp_file_path = temp_file.name

        return send_file(temp_file_path, mimetype="audio/mpeg", as_attachment=True, download_name="generated_speech.mp3")

    except Exception as e:
        return jsonify({"error": str(e), "message": "An error occurred while generating speech"}), 500

if __name__ == "__main__":
    app.run(debug=True)

