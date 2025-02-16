from flask import Flask, render_template, request, send_file
import os
import PyPDF2
import re

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_AUDIO = "static/output.mp3"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def clean_extracted_text(text):
    """Fixes spacing issues from PyPDF2 extraction."""
    text = re.sub(r'\n+', ' ', text)  # Replace multiple newlines with space
    text = re.sub(r'\s+', ' ', text).strip()  # Remove excessive spaces
    return text

def extract_text(file_path):
    """Extracts text from .txt or .pdf files, fixing spacing issues."""
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

@app.route("/", methods=["GET", "POST"])
def index():
    text = ""

    if request.method == "POST":
        if "file" in request.files:
            file = request.files["file"]
            if file and (file.filename.endswith(".txt") or file.filename.endswith(".pdf")):
                file_path = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(file_path)
                text = extract_text(file_path)

        elif "text_input" in request.form:
            text = request.form["text_input"]

    return render_template("index.html", text=text)


if __name__ == "__main__":
    app.run(debug=True)