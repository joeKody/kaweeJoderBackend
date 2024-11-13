from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

from pythainlp.tokenize import syllable_tokenize, word_tokenize
from pythainlp.util import isthai
from pythainlp.corpus import thai_words
from pythainlp.khavee import KhaveeVerifier

from fastapi.middleware.cors import CORSMiddleware

# PythaiNLP setup
kv = KhaveeVerifier()
all_thai_words = list(thai_words())
one_syllable_dict = [i for i in all_thai_words if len(syllable_tokenize(i))==1]

# FastAPI setup
app = FastAPI()

app.add_middleware( CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'], )

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.put('/all_rhymes/{text}')
def all_rhymes(text: str):
    if not isthai(text):
        return {"error": "Input text is not Thai."}
    
    # words = word_tokenize(text)
    syllables = list(syllable_tokenize(text))
    last_syllable = syllables[-1]
    rhymes = []

    for i in one_syllable_dict:
        try:
            if kv.is_sumpus(last_syllable, i) and i != last_syllable:
                rhymes.append(i)
        except:
            pass
    return {"rhymes": rhymes}

@app.put('/one_syllable_rhymes/{word}')
def one_syllable_rhymes(word: str):
    if not isthai(word):
        return {"error": "Input word is not Thai."}
    
    rhymes = []

    for i in one_syllable_dict:
        try:
            if kv.is_sumpus(word, i) and i != word:
                rhymes.append(i)
        except:
            pass
    return {"rhymes": rhymes}
    

@app.put('/is_sumpus/{word_1}/{word_2}')
def rhymes(word_1: str, word_2: str):
    if not isthai(word_1):
        return {"error": "Input word is not Thai."}
    if not isthai(word_2):
        return {"error": "Input word is not Thai."}
    
    if kv.is_sumpus(word_1, word_2):
        return {"rhymes": True}

class Klon(BaseModel):
    text: str
    klon_type: str

@app.put('/check_klon/{klon_type}')
def check_klon(klon: Klon):
    return {"result": kv.check_klon(klon.text, klon.klon_type)}