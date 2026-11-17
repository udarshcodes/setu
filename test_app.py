import sys
import os
import pytest
from fastapi.testclient import TestClient
import tempfile

sys.path.insert(0, os.path.abspath('.'))

from app.main import app


client = TestClient(app)

class MockSegment:
    def __init__(self, text):
        self.text = text

class MockInfo:
    def __init__(self, language, prob):
        self.language = language
        self.language_probability = prob

class MockWhisper:
    def __init__(self, text, lang, prob):
        self.text = text
        self.lang = lang
        self.prob = prob
        
    def transcribe(self, path):
        return [MockSegment(self.text)], MockInfo(self.lang, self.prob)

# Mock query_gemma to just return the prompt we sent it so we can verify the routing
def mock_query_gemma(prompt=None, image_path=None, audio_path=None, tools=None, messages=None):
    if messages is None:
        messages = [{"role": "user", "content": prompt}]
    return {"role": "assistant", "content": f"MOCKED RESPONSE. Prompt was: {messages[0]['content']}"}

@pytest.fixture(autouse=True)
def setup_mocks(monkeypatch):
    import app.main as main_app
    monkeypatch.setattr(main_app, "query_gemma", mock_query_gemma)
    monkeypatch.setattr(main_app, "init_db", lambda: None)
    monkeypatch.setattr(main_app, "retrieve_context", lambda q: "MOCKED CONTEXT")

def test_text_routing_english():
    response = client.post("/chat", data={"text": "What is a tractor?"})
    assert response.status_code == 200
    assert "System: The following user input is in English." in response.json()["response"]

def test_text_routing_tamil():
    response = client.post("/chat", data={"text": "டிராக்டர் என்றால் என்ன?"})
    assert response.status_code == 200
    assert "System: The following user input is in pure Tamil." in response.json()["response"]

def test_text_routing_code_switched():
    response = client.post("/chat", data={"text": "டிராக்டர் cost என்ன?"})
    assert response.status_code == 200
    assert "System: The following user input is code-switched Tamil-English." in response.json()["response"]

def test_audio_routing(monkeypatch):
    import app.main as main_app
    monkeypatch.setattr(main_app, "get_whisper", lambda: MockWhisper("What is a tractor?", "en", 0.99))
    
    fd, path = tempfile.mkstemp(suffix=".wav")
    with os.fdopen(fd, 'wb') as f:
        f.write(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00")
        
    with open(path, "rb") as f:
        response = client.post("/chat", files={"audio": ("test.wav", f, "audio/wav")})
        
    assert response.status_code == 200
    assert "System: The following user input is in English." in response.json()["response"]
    os.remove(path)
