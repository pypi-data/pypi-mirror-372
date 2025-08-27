import inspect, ast, binascii, sys, traceback, os, time, logging, subprocess

class CodeTracker:
    def __init__(self):
        self._logs = []

    def __call__(self, func):
        """Memungkinkan dekorator @tracker digunakan langsung."""
        return self._wrap(func)

    def log_function_call(self, func):
        """Memungkinkan dekorator @tracker.log_function_call."""
        return self._wrap(func)

    def _wrap(self, func):
        """Logik dekorator yang digunakan oleh __call__ dan log_function_call."""
        def wrapper(*args, **kwargs):
            self._logs.append(f"▶️ {func.__name__}() dipanggil.")
            result = func(*args, **kwargs)
            self._logs.append(f"✅ {func.__name__} selesai. → {result}")
            return result
        return wrapper

    def get(self):
        """Mengembalikan salinan log saat ini."""
        return self._logs.copy()

    def clear(self):
        """Menghapus semua log."""
        self._logs.clear()
 
               
class BinaryConverter:
    def __init__(self):
        pass

    def code_to_binary(self, code_str):
        """
        Mengonversi string kode Python ke biner (ASCII).
        """
        binary = ' '.join(format(ord(c), '08b') for c in code_str)
        return binary

    def file_to_binary(self, file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        return self.code_to_binary(content)

    def binary_to_code(self, binary_str):
        """
        Mengonversi biner ASCII ke string Python.
        """
        chars = binary_str.split()
        try:
            return ''.join([chr(int(b, 2)) for b in chars])
        except Exception as e:
            return f"❌ Error dalam mengonversi biner: {e}"


# === Pemakaian global (jika ingin akses dari luar) ===
tracker = CodeTracker()
binary_tool = BinaryConverter()


# === Contoh fungsi pengguna yang dipantau ===
@tracker.log_function_call
def contoh_fungsi(a, b):
    return a + b
  
      
class ByteConverter:
    SUFFIXES = ["B", "KB", "MB", "GB", "TB", "PB"]

    @classmethod
    def convert(cls, size_bytes, precision=2):
        """
        Mengubah ukuran byte menjadi string yang terbaca (KB, MB, dst.)
        :param size_bytes: int atau float, ukuran dalam byte
        :param precision: int, jumlah angka desimal
        :return: str
        """
        if size_bytes < 0:
            raise ValueError("Ukuran byte tidak boleh negatif.")
        idx = 0
        while size_bytes >= 1024 and idx < len(cls.SUFFIXES) - 1:
            size_bytes /= 1024.0
            idx += 1
        return f"{size_bytes:.{precision}f} {cls.SUFFIXES[idx]}"

    @classmethod
    def to_bytes(cls, value, unit):
        """
        Mengubah nilai dari unit tertentu (KB, MB, ...) ke byte.
        """
        unit = unit.upper()
        if unit not in cls.SUFFIXES:
            raise ValueError(f"Unit tidak dikenal: {unit}")
        idx = cls.SUFFIXES.index(unit)
        return int(value * (1024 ** idx))
        

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DAFE")

class DafeGuard:
    REQUIRED_LIBS = ["numpy", "pyttsx3", "networkx", "geopy", "librosa", "textblob", "simple_rl", "scipy", "scikit-learn", "matplotlib", "pandas", "pandas", "autograd", "pyserial", "Pillow", "arrayfire"]

    def __init__(self):
        self.logs = []
        self.errors = []
        self.scan_environment()

    def scan_environment(self):
        try:
            # Cek ukuran package
            base_path = os.path.dirname(__file__)
            total_size = self.get_directory_size(base_path)
            self.logs.append(f"[DAFE] 📦 Ukuran total dearning: {total_size / 1024:.2f} KB")

            # Cek Python version
            if sys.version_info < (3, 7):
                self.errors.append("❗ Python < 3.7 tidak didukung oleh dearning.")
            
            # Cek dependencies penting
            self.missing_libs = []
            for lib in self.REQUIRED_LIBS:
                try:
                    __import__(lib)
                except ImportError:
                    self.errors.append(f"❌ Dependency hilang: {lib}")
                    self.missing_libs.append(lib)

        except Exception as e:
            self.errors.append(f"[DAFE] Internal error: {str(e)}")

    def get_directory_size(self, path):
        total = 0
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.isfile(fp):
                    total += os.path.getsize(fp)
        return total

    def report(self):
        if self.errors:
            logger.warning("📋 DAFE menemukan masalah:")
            for e in self.errors:
                logger.warning(e)
        else:
            logger.info("✅ DAFE: Sistem aman.")
            for log in self.logs:
                logger.info(log)

dafe = DafeGuard()
dafe.report()