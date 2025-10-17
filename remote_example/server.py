from mcp.server.fastmcp import FastMCP
import json
import re
import uvicorn
import os

HOST = os.environ.get('HOST', '0.0.0.0')
PORT = os.environ.get('PORT', 8000)
    
server = FastMCP(name='vocabulary-server')

@server.tool()
def analyze_text(text: str) -> dict:
    """Analyze input text to compute character count, word count, number of unique words, 
    along with their occurence frequencies."""
    char_count = len(text)
    text = text.lower()
    text = text.replace('\n', ' ')
    text = text.strip()
    text = re.sub(r'[^\w\s]', '', text) # remove punctuation
    words = text.split()
    analysis = {
        'character_count': char_count,
        'word_count': len(words),
        'unique_words': list(set(words)),
        'word_frequency': {word: words.count(word) for word in set(words)}
    }
    return analysis

@server.resource('file://stop_words.json')
def stop_words():
    """Returns a list of stop words in English."""
    with open('stop_words.json', 'r') as f:
        stop_words_list = json.load(f)
    return stop_words_list
    
@server.resource('greeting://{name}')
def personalized_greet(name: str) -> str:
    """Return a personalized greeting message."""
    with open('greeting.txt', 'r') as f:
        greeting = f.read().strip()
    return f"Hello, {name}! {greeting}"

@server.prompt()
def vocabulary_prompt():
    """Prompt for an LLM to construct a vocabulary dictionary of words mapped to meanings."""
    prompt = (
        "You are an expert in text analysis. For the given text, "
        "construct a dictionary of words mapped to their meanings, ignoring any stop words. "
        "Output a JSON object mapping each word to its definition. "
    )
    return prompt

if __name__ == '__main__':
    uvicorn.run(server.streamable_http_app(), host=HOST, port=PORT)