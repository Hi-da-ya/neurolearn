from flask import Flask, request, jsonify, make_response
from PyPDF2 import PdfReader
from docx import Document
from dotenv import load_dotenv
from flask_cors import CORS
import magic
import openai
import os
import spacy

load_dotenv()
nlp = spacy.load("en_core_web_sm")
app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Azure OpenAI Config
client = openai.AzureOpenAI(
    api_key=os.getenv('API_KEY'),
    api_version=os.getenv('API_VERSION'),
    azure_endpoint=os.getenv('API_BASE')
)

# File Processing
def extract_text(file_path, file_type):
    if file_type == 'pdf':
        reader = PdfReader(file_path)
        return " ".join([page.extract_text() for page in reader.pages])
    elif file_type == 'docx':
        return " ".join([p.text for p in Document(file_path).paragraphs])
    elif file_type == 'txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    raise ValueError("Unsupported file type")

# Content simplification
def simplify(content, profile):
    PROMPTS = {
        "autistic": """Convert to numbered steps:
        1. Use concrete examples
        2. Avoid metaphors
        3. Max 5 steps""",
        
        "dyslexic": """Rewrite for dyslexia:
        - Short sentences
        - Phonetic breaks (e.g., pho-to-syn-the-sis)
        - Bold key terms""",
        
        "adhd": """Make engaging:
        - 3 bullet points max
        - Start with emojis
        - Add 1 quiz question"""
    }
    
    response = client.chat.completions.create(
        model='gpt-35-turbo',
        messages=[
            {"role": "system", "content": PROMPTS[profile]},
            {"role": "user", "content": content[:2000]}  # Limit input size
        ],
        max_tokens=300
    )
    return response.choices[0].message.content

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        file = request.files['file']
        profile = request.form.get('profile', 'autistic')
        
        # Save file temporarily
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        # Process content
        file_type = magic.from_file(file_path, mime=True)
        if 'pdf' in file_type:
            file_type = 'pdf'
        elif 'wordprocessingml' in file_type:
            file_type = 'docx'
        elif 'text/plain' in file_type:
            file_type = 'txt'
        else:
            raise ValueError("Unsupported file type")
        
        text = extract_text(file_path, file_type)
        simplified = simplify(text, profile)
        
        os.remove(file_path)
        return jsonify({
            "content": simplified,
            "profile": profile,
            "filename": file.filename
        })
        
    except Exception as e:
        if 'file_path' in locals(): os.remove(file_path)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5555, debug=True)