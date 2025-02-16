import os
from flask import Flask, request, jsonify
import textstat
from mistralai.client import MistralClient

app = Flask(__name__)

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY is not set. Please configure it in your environment.")

client = MistralClient(api_key=MISTRAL_API_KEY)

def simplify_text_with_mistral(text):
    """Generate a simplified version of the input text using Mistral's model."""
    response = client.chat(
        model="mistral-tiny",  # Change to "mistral-medium" if needed
        messages=[
            {"role": "system", "content": "You simplify complex sentences into easier words while keeping the meaning."},
            {"role": "user", "content": f"Original: {text}\nSimplified:"}
        ]
    )
    
    return response.choices[0].message.content.strip()


@app.route('/simplify', methods=['POST'])
def simplify_text():
    try:
        data = request.json
        if not data or 'text' not in data:
            return jsonify({"error": "No text provided"}), 400

        original_text = data['text'].strip()
        if not original_text:
            return jsonify({"error": "Empty text provided"}), 400

        # Generate simplified text using Mistral
        simplified_text = simplify_text_with_mistral(original_text)

        # Calculate readability metrics
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
            "original": {
                "text": original_text,
                "metrics": original_metrics
            },
            "simplified": {
                "text": simplified_text,
                "metrics": simplified_metrics
            }
        })
    
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
