# dearning/__init__.py
from .model import CustomAIModel, Dense, Activation, Dropout, DOtensor
from .utils import preprocess_data, evaluate_model, Optimizer
from .training import train

# === 🔄 Lazy Loader Util ===
import importlib, sys, builtins

class _LazyLoader:
    def __init__(self, module_name, exports):
        self._module_name = module_name
        self._exports = exports
        self._module = None

    def _load(self):
        if self._module is None:
            self._module = importlib.import_module(self._module_name)
        return self._module

    def __getattr__(self, attr):
        if attr in self._exports:
            return getattr(self._load(), attr)
        raise AttributeError(f"'{self._module_name}' has no attribute '{attr}'")

# === 📦 Register Lazy Modules ===
_ai_tools = _LazyLoader("dearning.AI_tools", [
    "DLP", "TextToSpeech", "AImemory",
    "load_image", "flatten_image", "extract_mfcc"
])

_ai_core = _LazyLoader("dearning.AI_core", [
    "CodeTracker", "BinaryConverter", "ByteConverter"
])

_multymodel = _LazyLoader("dearning.multymodel", [
    "AImodel", "locAIer"
])

# === 🌐 Public API Expose ===
DLP = _ai_tools.DLP
TextToSpeech = _ai_tools.TextToSpeech
AImemory = _ai_tools.AImemory
load_image = _ai_tools.load_image
flatten_image = _ai_tools.flatten_image
extract_mfcc = _ai_tools.extract_mfcc

CodeTracker = _ai_core.CodeTracker
BinaryConverter = _ai_core.BinaryConverter
ByteConverter = _ai_core.ByteConverter

AImodel = _multymodel.AImodel

# === 🛡️ Protection ===
builtins.__dafe_protect__ = True
from .AI_core import _global_dafe, record_event