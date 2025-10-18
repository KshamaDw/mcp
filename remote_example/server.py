from mcp.server.fastmcp import FastMCP, Context
from mcp.types import SamplingMessage, TextContent
from collections import Counter
from pydantic import BaseModel, Field
import json
import re
import uvicorn
import os
import nltk
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

import logging
logging.basicConfig(level=logging.WARNING)

HOST = os.environ.get('HOST', '0.0.0.0')
PORT = os.environ.get('PORT', 8000)
    
server = FastMCP(name='vocabulary-server')
lemmatizer = nltk.stem.WordNetLemmatizer()

class VocabularyElicitationSchema(BaseModel):
    """Schema for eliciting user preference for lemmatization."""
    lemmatize: int = Field(description="Whether to lemmatize the words or not", default=1)

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

@server.tool()
async def get_keywords(ctx: Context) -> dict:
    """Extract keywords from input text by lemmatizing and counting occurrences."""
    def get_wordnet_pos(word):
        """Map POS tag to first character lemmatize() accepts"""
        tag = nltk.pos_tag([word])[0][1][0].upper()
        tag_dict = {"J": 'a', "N": 'n', "V": 'v', "R": 'r'}
        return tag_dict.get(tag, 'n')
    
    sampling_response = await ctx.session.create_message(
        messages=[SamplingMessage(
            role="user",
            content=TextContent(type='text',text="Enter your input for the get_keywords tool: "))],
        max_tokens=100,
    )

    text = sampling_response.content.text
    text = text.lower()
    text = text.replace('\n', ' ')
    text = text.strip()
    text = re.sub(r'[^\w\s]', '', text) # remove punctuation
    words = text.split()
    counts = {word: words.count(word) for word in set(words)}

    await ctx.log('info', f"Word Counts for input text: {counts}")

    elicit_response = await ctx.elicit(
        message='Enter your choice to lemmatize words (0: no, 1: yes): ', 
        schema=VocabularyElicitationSchema)
    
    if elicit_response.action == 'accept' and elicit_response.data:
        lemmatize_flag = bool(elicit_response.data.lemmatize)
    else:
        lemmatize_flag = True
    
    if lemmatize_flag:
        base_forms = {word: lemmatizer.lemmatize(word, get_wordnet_pos(word)) for word in counts.keys()}
        base_counts = {}
        for word in words:
            base_word = base_forms[word]
            if base_word in base_counts:
                base_counts[base_word] += counts[word]
            else:
                base_counts[base_word] = counts[word]
        base_counts = Counter(base_counts)
    else:
        base_counts = Counter(counts)
    return base_counts

@server.resource('file://stop_words.json')
def stop_words():
    """Returns a list of stop words in English."""
    file_path = os.path.join(os.path.dirname(__file__), 'stop_words.json')
    try:
        with open(file_path, 'r') as f:
            stop_words_list = json.load(f)
        return stop_words_list
    except Exception as e:
        logging.error(f"Error reading stop_words.json at {file_path}: {e}")
        return []
    
@server.resource('greeting://{name}')
def personalized_greet(name: str) -> str:
    """Return a personalized greeting message."""
    file_path = os.path.join(os.path.dirname(__file__), 'greeting.txt')
    try:
        with open(file_path, 'r') as f:
            greeting = f.read().strip()
        return f"Hello, {name}! {greeting}"
    except Exception as e:
        logging.error(f"Error reading greeting.txt at {file_path}: {e}")
        return ""

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
    uvicorn.run(server.streamable_http_app(), host=HOST, port=int(PORT))