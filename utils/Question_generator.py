#import necessary libraries
import re
import openai
from transformers import pipeline

#chunking to process information one at a time to avoid generating vague/broad questions
def chunk_text(text, max_tokens=500):
    # Split text into sentences using regex
    sentences = re.split(r'(?<=[.!?]) +', text)

    chunks = []
    current_chunk = ""
    current_len = 0

    for sentence in sentences:
        word_count = len(sentence.split())
        if current_len + word_count <= max_tokens:
            current_chunk += " " + sentence
            current_len += word_count
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
            current_len = word_count

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


# Load summarizer model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_chunks(chunks):
    summaries = []
    for chunk in chunks:
        summary = summarizer(chunk, max_length=1000, min_length=30, do_sample=False)[0]['summary_text']
        summaries.append(summary)
    return summaries

# Chunk → Summarize → Generate Questions
#we need to connect this pdf part to our user uploaded pdf
chunks = chunk_text(pdf)
summaries = summarize_chunks(chunks)

for summary in summaries:
    questions = generate_questions_from_text(summary)
    print("📄 Summary:", summary)
    print("❓ Questions:", questions)