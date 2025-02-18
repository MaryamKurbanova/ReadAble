import os
import re
import tempfile
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import PyPDF2
import textstat
from elevenlabs.client import ElevenLabs
from mistralai.client import MistralClient

# Load environment variables
load_dotenv()

app = Flask(
    __name__,
    template_folder=os.path.join(os.getcwd(), "templates"),
    static_folder=os.path.join(os.getcwd(), "static"),
)
CORS(app, resources={r"/*": {"origins": "*"}})

# API Keys
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

if not ELEVENLABS_API_KEY:
    raise ValueError("ELEVENLABS_API_KEY is not set in the .env file")
if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY is not set in the .env file")

client_elevenlabs = ElevenLabs(api_key=ELEVENLABS_API_KEY)
client_mistral = MistralClient(api_key=MISTRAL_API_KEY)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def clean_extracted_text(text):
    text = re.sub(r"\n+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
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
        audio_generator = client_elevenlabs.generate(
            text=text,
            voice="Rachel",
            model="eleven_multilingual_v2"
        )
        
        audio_data = b''.join(chunk for chunk in audio_generator)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_file.write(audio_data)
            temp_file_path = temp_file.name

        return send_file(temp_file_path, mimetype="audio/mpeg", as_attachment=True, download_name="generated_speech.mp3")
    
    except Exception as e:
        return jsonify({"error": str(e), "message": "An error occurred while generating speech"}), 500

@app.route("/simplify", methods=["POST"])
def simplify_text():
    try:
        data = request.json
        if not data or "text" not in data:
            return jsonify({"error": "No text provided"}), 400

        original_text = data["text"].strip()
        if not original_text:
            return jsonify({"error": "Empty text provided"}), 400

        response = client_mistral.chat(
            model="mistral-tiny",
            messages=[
                {"role": "system", "content": "You simplify complex sentences into easier words while keeping the meaning."},
                {"role": "user", "content": f"Original: {original_text}\nSimplified:"}
            ]
        )
        simplified_text = response.choices[0].message.content.strip()

        original_metrics = {
            "flesch_kincaid_grade": textstat.flesch_kincaid_grade(original_text),
            "flesch_reading_ease": textstat.flesch_reading_ease(original_text),
            "syllable_count": textstat.syllable_count(original_text),
            "difficult_words": len(textstat.difficult_words_list(original_text))
        }

        simplified_metrics = {
            "flesch_kincaid_grade": textstat.flesch_kincaid_grade(simplified_text),
            "flesch_reading_ease": textstat.flesch_reading_ease(simplified_text),
            "syllable_count": textstat.syllable_count(simplified_text),
            "difficult_words": len(textstat.difficult_words_list(simplified_text))
        }

        return jsonify({
            "original": {"text": original_text, "metrics": original_metrics},
            "simplified": {"text": simplified_text, "metrics": simplified_metrics}
        })
    
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/simplify')
def simplify():
    return render_template('simplify.html')


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)