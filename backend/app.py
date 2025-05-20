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
    BASE_PROMPT = """Summarize the entire document by:
    1. **Identifying major sections** (use original headings or group logically)
    2. For each section:
       - {profile_prompts}  # Placeholder for cognitive adaptations
       - Include: Purpose, Key Points (3-5), Connection to other sections
    3. Format with Markdown headings (###) and bullet points."""

    PROFILE_PROMPTS = {
        "autistic": """You are a patient science tutor teaching a middle school autistic student. 
        Explain this concept in 3 steps:
        1. Start with a concrete definition (avoid metaphors)
        2. Give a real-world example they encounter daily
        3. End with a practice question ("Let's check: What would happen if...?")

        Content: {content}""",

        "dyslexic": """You're a reading specialist simplifying text for dyslexic students:
        - Short sentences (max 10 words)
        - Bold key terms (**photosynthesis**)
        - Add phonetic breaks (pho-to-syn-the-sis)
        - End with "Remember: [1-sentence summary]"

        Original: {content}""",

        "adhd": """You're an energetic tutor making science exciting for distractible minds:
        [emoji] Start with a surprising fun fact 
        [emoji] Explain in 3 bullet points
        [emoji] Add a quick interactive element ("Point to something green around you!")

        Topic: {content}"""
    }
    
    system_prompt = BASE_PROMPT.replace(
        "{profile_prompts}", 
        PROFILE_PROMPTS[profile]
    )

    sections = content.split('\n\n')  # Simple split by double newlines (adapt as needed)
    
    summaries = []
    for section in sections:
        # 2. Process each section individually
        if len(section) < 10:  # Skip tiny sections
            continue
        response = client.chat.completions.create(
            model='gpt-35-turbo',
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content[:16000]}  # Limit input size
            ],
            max_tokens=500,
            temperature=0.7 if profile == "adhd" else 0.3,
            top_p=0.9,  
            frequency_penalty=0.5,  
            presence_penalty=0.5 
        )
        summaries.append(response.choices[0].message.content)
    return "\n\n".join(summaries)

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