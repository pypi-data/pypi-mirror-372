# dearning/__init__.py
from .model import CustomAIModel, Dense, Activation, Dropout, DOtensor
from .utils import preprocess_data, evaluate_model, Optimizer
from .training import train

# === 🔄 Lazy Loader Util ===
import importlib, sys, builtins

# === 🛡️ Protection ===
builtins.__dafe_protect__ = True

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
_AI_tools = _LazyLoader("dearning.AI_tools", [
    "DLP", "TextToSpeech", "AImemory",
    "load_image", "flatten_image", "extract_mfcc"
])

_AI_core = _LazyLoader("dearning.AI_core", [
    "CodeTracker", "BinaryConverter", "ByteConverter"
])

_multymodel = _LazyLoader("dearning.multymodel", [
    "AImodel", "locAIer"
])

# === 🌐 Public API Expose ===
DLP = _AI_tools.DLP
TextToSpeech = _AI_tools.TextToSpeech
AImemory = _AI_tools.AImemory
load_image = _AI_tools.load_image
flatten_image = _AI_tools.flatten_image
extract_mfcc = _AI_tools.extract_mfcc

CodeTracker = _AI_core.CodeTracker
BinaryConverter = _AI_core.BinaryConverter
ByteConverter = _AI_core.ByteConverter

AImodel = _multymodel.AImodel
