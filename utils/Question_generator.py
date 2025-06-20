import nltk
from nltk.tokenize import sent_tokenize

nltk.download('punkt')

def semantic_chunker(text, max_tokens=500):
    """
    Chunk the text into semantically meaningful blocks based on sentence boundaries.
    """
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = ""
    token_count = 0

    for sentence in sentences:
        words = sentence.split()
        if token_count + len(words) <= max_tokens:
            current_chunk += " " + sentence
            token_count += len(words)
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
            token_count = len(words)

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def slide_chunker(text):
    """
    For slide-style documents, treat each line as a small chunk.
    """
    lines = text.split("\n")
    return [line.strip() for line in lines if len(line.strip()) > 20]

#Example usage
from file_handler import extract_text_from_pdf, detect_pdf_type
from preprocessor import semantic_chunker, slide_chunker

pdf_path = "your_file.pdf"
text = extract_text_from_pdf(pdf_path)
material_type = detect_pdf_type(text)

# Adaptive Chunking
if material_type == "slide_deck":
    chunks = slide_chunker(text)
else:
    chunks = semantic_chunker(text, max_tokens=500)

# Result
print(f"Total chunks: {len(chunks)}")
print(chunks[0][:300]) 

#Question generation
import requests
import time

# Insert your OpenRouter API key
OPENROUTER_API_KEY = "sk-..."  # Replace with your actual key
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}

def build_prompt(text):
    return f"""
You are a university professor designing a realistic exam.
Given the following lecture content, generate:
- 5 definition-based questions
- 5 application or explanation questions
- 5 conceptual understanding questions
- 1 Bonus Challenge Question

Lecture Content:
{text}
"""

def generate_questions_from_chunk(chunk, model="mistralai/mixtral-8x7b"):
    prompt = build_prompt(chunk)
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(OPENROUTER_API_URL, headers=HEADERS, json=data)
        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"]
        return reply
    except requests.exceptions.RequestException as e:
        print(f"Error generating questions: {e}")
        return None
#Example Usage
from file_handler import extract_text_from_pdf, detect_pdf_type
from preprocessor import semantic_chunker, slide_chunker
from question_generator import generate_questions_from_chunk

pdf_path = "your_file.pdf"
text = extract_text_from_pdf(pdf_path)
material_type = detect_pdf_type(text)

chunks = slide_chunker(text) if material_type == "slide_deck" else semantic_chunker(text)

# Generate questions for each chunk
for i, chunk in enumerate(chunks[:3]):  # You can limit how many you generate
    print(f"\n Chunk {i+1}:")
    questions = generate_questions_from_chunk(chunk)
    print(questions)
    time.sleep(2)  # Optional: throttle requests to avoid rate limit
