import numpy as np
from PIL import Image
import io
import os
import ast
import pyttsx3
import wave
import contextlib
import logging
import struct
import networkx as nx
from geopy.geocoders import Nominatim
import serial
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

logging.basicConfig(level=logging.INFO)

# === 📖 NLP: Analisis ===
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

class DLP:
    def __init__(self, lang="en"):
        self.lang = lang

    def analyze_sentiment(self, text):
        blob = TextBlob(text)
        return {
            "polarity": blob.sentiment.polarity,
            "subjectivity": blob.sentiment.subjectivity,
            "label": "positive" if blob.sentiment.polarity > 0
                     else "negative" if blob.sentiment.polarity < 0
                     else "neutral"
        }

    def extract_nouns(self, text):
        blob = TextBlob(text)
        return list(blob.noun_phrases)

    def pos_tagging(self, text):
        blob = TextBlob(text)
        return blob.tags  # [('word', 'POS'), ...]

    def summarize(self, text, max_sentences=2):
        sentences = text.split(". ")
        return ". ".join(sentences[:max_sentences]) + ("." if len(sentences) > max_sentences else "")

    def process(self, text):
        result = {
            "sentiment": self.analyze_sentiment(text),
            "nouns": self.extract_nouns(text),
            "pos_tags": self.pos_tagging(text),
            "summary": self.summarize(text)
        }
        return result
        
 # === Reinforcement Learning Tools ===
try:
    from simple_rl.agents import QLearningAgent, RandomAgent
    from simple_rl.tasks import GridWorldMDP
    from simple_rl.run_experiments import run_agents_on_mdp

    class RLTools:
        def __init__(self):
            self.env = GridWorldMDP()
            self.agents = []

        def add_q_agent(self, name="q_agent", alpha=0.1, epsilon=0.1, gamma=0.9):
            agent = QLearningAgent(name=name, actions=self.env.get_actions(),
                                   alpha=alpha, epsilon=epsilon, gamma=gamma)
            self.agents.append(agent)
            return agent

        def add_random_agent(self, name="random"):
            agent = RandomAgent(name=name, actions=self.env.get_actions())
            self.agents.append(agent)
            return agent

        def run(self, episodes=100):
            if self.agents:
                run_agents_on_mdp(self.agents, self.env, instances=1, episodes=episodes)
            else:
                print("[⚠️] Tidak ada agen RL yang ditambahkan.")

except ImportError:
    class RLTools:
        def __init__(self):
            print("[❌] simple_rl belum terpasang. Gunakan: pip install simple_rl")

        def add_q_agent(self, *args, **kwargs): pass
        def add_random_agent(self, *args, **kwargs): pass
        def run(self, *args, **kwargs): pass

# === TEXT TO SPEECH ===
class TextToSpeech:
    def __init__(self, voice=None, rate=150, volume=1.0):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)
        if voice:
            self.set_voice(voice)

    def set_voice(self, voice_name):
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if voice_name.lower() in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

# === MEMORY MANAGEMENT ===
MEMORY_PATH = os.path.join(os.path.dirname(__file__), "..", "Memory", "DATAI.py")
MEMORY_VAR = "memory"

class AImemory:
    def __init__(self):
        self.memory = self._load_memory()

    def _load_memory(self):
        if not os.path.exists(MEMORY_PATH):
            with open(MEMORY_PATH, "w") as f:
                f.write(f"{MEMORY_VAR} = []\n")
            return []

        with open(MEMORY_PATH, "r") as f:
            try:
                content = f.read()
                parsed = ast.parse(content, mode='exec')
                for node in parsed.body:
                    if isinstance(node, ast.Assign) and node.targets[0].id == MEMORY_VAR:
                        return ast.literal_eval(ast.unparse(node.value))
            except Exception as e:
                print("❌ Gagal baca memori:", e)
        return []

    def _save_memory(self):
        with open(MEMORY_PATH, "w") as f:
            f.write(f"{MEMORY_VAR} = {repr(self.memory)}\n")

    def add(self, data):
        if data not in self.memory:
            self.memory.append(data)
            self._save_memory()

    def remove(self, data):
        if data in self.memory:
            self.memory.remove(data)
            self._save_memory()

    def clear(self):
        self.memory = []
        self._save_memory()

    def get_all(self):
        return self.memory

    def contains(self, query):
        return query in self.memory

# === 📷 Gambar ===

def load_image(path, target_size=(64, 64), grayscale=False):
    """
    Membaca dan resize gambar, lalu normalisasi + auto-contrast + clipping.
    """
    mode = "L" if grayscale else "RGB"
    img = Image.open(path).convert(mode).resize(target_size)
    arr = np.asarray(img).astype(np.float32)

    # Normalisasi 0-1 + kontras adaptif
    arr -= arr.min()
    if arr.max() > 0:
        arr /= arr.max()

    arr = np.clip(arr, 0.0, 1.0)
    return arr

def flatten_image(img_array):
    """
    Ubah gambar ke vektor 1D (flatten).
    """
    return img_array.flatten()

# === 🎧 Audio ===

def load_audio(path, sr=22050):
    """
    Membaca file audio WAV/MP3 dan mengembalikan waveform + sample rate.
    """
    if not LIBROSA_AVAILABLE:
        raise ImportError("Librosa belum terinstal. Gunakan pip install librosa")

    y, sr = librosa.load(path, sr=sr)
    return y, sr

def extract_mfcc(path, n_mfcc=13):
    """
    Ekstrak MFCC (fitur audio) untuk input model.
    """
    y, sr = load_audio(path)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    return mfcc.T  # Transpose: time x feature

def get_audio_duration(path):
    """
    Mendapatkan durasi audio WAV secara cepat tanpa dependencies berat.
    """
    with contextlib.closing(wave.open(path, 'r')) as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        duration = frames / float(rate)
        return duration

# === 🎥 Video (GIF Frames) ===

def extract_frames_from_gif(path, max_frames=10):
    """
    Ekstrak beberapa frame dari GIF sebagai array numpy, dengan preprocessing.
    """
    img = Image.open(path)
    frames = []
    try:
        for i in range(max_frames):
            img.seek(i)
            frame = img.convert("RGB")
            arr = np.array(frame).astype(np.float32)

            # Tingkatkan akurasi visual
            arr -= arr.mean()
            std = arr.std() + 1e-5
            arr /= std
            arr = np.clip((arr + 0.5), 0.0, 1.0)  # Dinormalisasi kembali ke 0–1

            frames.append(arr)
    except EOFError:
        pass  # End of GIF

    return np.array(frames)

# === 📈 Booster (Optimisasi array/data) ===

def normalize_array(arr):
    """
    Normalisasi array ke [0, 1]
    """
    arr = np.asarray(arr)
    return (arr - np.min(arr)) / (np.max(arr) - np.min(arr) + 1e-8)

def one_hot_encode(labels, num_classes=None):
    """
    Ubah label integer menjadi one-hot encoding.
    """
    labels = np.array(labels).astype(int)
    if num_classes is None:
        num_classes = np.max(labels) + 1
    one_hot = np.zeros((labels.size, num_classes))
    one_hot[np.arange(labels.size), labels] = 1
    return one_hot

def softmax(x):
    """
    Fungsi softmax untuk output klasifikasi.
    """
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=-1, keepdims=True)

# === 🧠 Pemahaman cepat (analisis ringan) ===

def top_k_probs(preds, k=3):
    """
    Ambil top-k prediksi dari hasil softmax.
    """
    sorted_idx = np.argsort(preds)[::-1]
    top_k = [(int(i), float(preds[i])) for i in sorted_idx[:k]]
    return top_k

def summarize_array(arr):
    """
    Ringkasan array (min, max, mean, shape)
    """
    return {
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "mean": float(np.mean(arr)),
        "shape": arr.shape
    }