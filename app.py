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
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok = True)

# AI configurations
#OpenAi
# openai.api_key = os.getenv('API_KEY')

#Azure openAI
client = openai.AzureOpenAI(
    api_key = os.getenv('API_KEYa'),
    api_version = os.getenv('API_VERSION'),
    azure_endpoint = os.getenv('API_BASE')

)


#Determine file type
def det_file_type(file_path):
    mime = magic.Magic(mime=True)
    file_type = mime.from_file(file_path)
    if 'pdf' in file_type:
        return 'pdf'
    elif 'wordprocessingml' in file_type:
        return 'docx'
    elif 'text/plain' in file_type:
        return 'txt'
    else:
        raise ValueError("Unsupported file type")
    
# Extract text from file  
def extract_pdf_text(file_path):
    reader = PdfReader(file_path)
    text = " ".join([page.extract_text() for page in reader.pages])
    return text

def extract_docx_text(file_path):
    document = Document(file_path)
    text = " ".join([paragraph.text for paragraph in document.paragraphs])
    return text

def extract_txt_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()
    
#Split the text into chunks  
def split_into_sent(text):
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents]

def chunk_it_up(text, max_size=500):
    #Split doc content into paragraphs
    paragraphs = [pgraph.strip() for pgraph in text.split('\n\n') if pgraph.strip()]
    chunks= []

    for paragraph in paragraphs:
        if len(paragraph) <= max_size:
            chunks.append(paragraph)
            continue

        #If paragraph is longer than max size split into sentences and group into chunks
        sentences = split_into_sent(paragraph)
        current_chunk = ""

        for sent in sentences:
             if len(current_chunk) + len(sent) + 1 > max_size:
                 if current_chunk:
                     chunks.append(current_chunk.strip())
                     current_chunk = "" 
             current_chunk += sent + " "   

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

    return chunks

#Simplify content
def simplify(content):
    response = client.chat.completions.create(
        model = 'gpt-35-turbo',
       
        messages = [
            {
                "role": "system",
                "content": "You are a friendly tutor for middle-school students. Explain this text in simple terms. Use examples, analogies, and step-by-step breakdowns. Highlight key terms.",
            },
            {"role": "user", "content": content},
        ],
    )  

    return response.choices[0].message.content

#File upload endpoint
@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # 1. Validate the upload
        # print(request.content_type)
        print("request.files keys:", list(request.files))
        if 'file' not in request.files:
            return make_response(jsonify({"error": "No file uploaded"}), 400)
            
        file = request.files['file']
        if file.filename == '':
            return make_response(jsonify({"error": "Empty filename"}), 400)

        # 2. Save temporarily
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # 3. Detect file type and extract text
        file_type = det_file_type(file_path)
        print("Degug statement1")
        try:
            if file_type == 'pdf':
                print("this is a pdf")
                text = extract_pdf_text(file_path)
                print("Successfully extracted")
            elif file_type == 'docx':
                text = extract_docx_text(file_path)
            elif file_type == 'txt':
                text = extract_txt_text(file_path)
            else:
                raise ValueError("Unsupported file type")
        except Exception as e:
            print("error", f"Text extraction failed: {str(e)}")
            return make_response(jsonify({"error": f"Text extraction failed: {str(e)}"}), 500)

        # 4. Process for students
        chunks = chunk_it_up(text, max_size=500)  
        
        simplified_chunks = []
        test_response = simplify("Test phrase")
        print(f"OpenAI test response: {test_response}")
        for chunk in chunks:
            try:
                # 5. Simplify with tutor-focused instructions
                simplified = simplify(chunk)  # Uses our tutor prompt
                simplified_chunks.append(simplified)
            except Exception as e:
                simplified_chunks.append(f"⚠️ Could not simplify this section: {chunk[:200]}...")

        # 6. Clean up and respond
        os.remove(file_path)  # Delete the temp file
        print("DEBUG: Preparing response")
        return make_response(
            jsonify({
            "original_filename": file.filename,
            "chunks": simplified_chunks,
            "word_count": len(text.split())
        })
        )

    except Exception as e:
        # Clean up if error occurred mid-process
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        return make_response(jsonify({
            "error": f"Processing failed: {str(e)}",
            "hint": "Supported files: PDF, DOCX, TXT (max 10MB)"
        }), 500) 

if __name__ == '__main__':
    app.run(port=5555, debug=True)       
