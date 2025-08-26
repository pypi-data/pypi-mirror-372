from dearning.model import CustomAIModel
from dearning.utils import preprocess_data, evaluate_model
import numpy as np
import matplotlib.pyplot as plt
import threading
import time
import logging
from PIL import Image
import os
from sklearn.datasets import make_classification, make_regression

# Autograd (opsional)
try:
    import autograd.numpy as anp
    from autograd import grad
    AUTOGRAD_AVAILABLE = True
except ImportError:
    AUTOGRAD_AVAILABLE = False

# === Data load ===
def load_dataset(task="classification", n_samples=500, n_features=4):
    if task == "classification":
        n_informative = max(2, min(n_features, n_features - 2))
        X, y = make_classification(
            n_samples=n_samples,
            n_features=n_features,
            n_informative=n_informative,
            n_redundant=0,
            n_repeated=0,
            n_classes=2,
            random_state=42
        )
        y = y.reshape(-1, 1)
    elif task == "regression":
        X, y = make_regression(n_samples=n_samples, n_features=n_features, noise=0.1)
        y = y.reshape(-1, 1)
    else:
        raise ValueError("Task harus 'classification' atau 'regression'")
    return X, y

def data_loader(X, y, batch_size=32, shuffle=True):
    n = X.shape[0]
    indices = np.arange(n)
    if shuffle:
        np.random.shuffle(indices)
    for start in range(0, n, batch_size):
        end = start + batch_size
        idx = indices[start:end]
        yield X[idx], y[idx]
        
def load_image_dataset(folder_path, size=(64, 64), label_type="folder"):
    """
    Load gambar dari folder menjadi dataset (X, y)
    label_type: "folder" = nama folder jadi label
    """
    X = []
    y = []
    class_map = {}
    class_idx = 0

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith((".jpg", ".png", ".jpeg")):
                path = os.path.join(root, file)
                img = Image.open(path).convert("RGB").resize(size)
                X.append(np.asarray(img) / 255.0)

                if label_type == "folder":
                    label_name = os.path.basename(os.path.dirname(path))
                    if label_name not in class_map:
                        class_map[label_name] = class_idx
                        class_idx += 1
                    y.append(class_map[label_name])

    X = np.array(X)
    y = np.array(y).reshape(-1, 1)
    print(f"📸 Loaded {len(X)} images from {folder_path}")
    return X, y

# === Training dengan Autograd ===
def train_with_autograd(model, X, y, epochs=100, lr=0.01, verbose=True):
    def loss_fn(weights_flattened):
        weights = weights_flattened.reshape(model.input_size, model.output_size)
        preds = anp.dot(X, weights)
        loss = anp.mean((preds - y) ** 2)
        return loss

    grad_fn = grad(loss_fn)
    weights = model.weights.copy().flatten()
    model.losses = []

    for epoch in range(epochs):
        grad_val = grad_fn(weights)
        weights -= lr * grad_val
        loss = loss_fn(weights)
        model.losses.append(loss)
        if verbose:
            print(f"[AutoGrad] Epoch {epoch+1}/{epochs} - Loss: {loss:.4f}")

    model.weights = weights.reshape(model.input_size, model.output_size)

# === Logging ===
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# === Evaluasi Komprehensif ===
def full_evaluation(model, X, y, task):
    result = evaluate_model(model, X, y, task)
    logging.info(f"📊 Evaluasi Model: {result}")
    return result

# === Training Utama ===
def train_model(model, task="classification", visualize=True,
                epochs=100, learning_rate=0.05, batch_size=32,
                use_autograd=False):

    n_features = model.layer_sizes[0]
    X, y = load_dataset(task=task, n_samples=500, n_features=n_features)
    X = preprocess_data(X)

    def training_thread():
        logging.info("🔧 Training dimulai...")
        if use_autograd and AUTOGRAD_AVAILABLE and hasattr(model, "weights"):
            train_with_autograd(model, X, y, epochs=epochs, lr=learning_rate)
        else:
            model.train(X, y, epochs=epochs, learning_rate=learning_rate, batch_size=batch_size)
        logging.info("✅ Training selesai.")

    start = time.time()
    thread = threading.Thread(target=training_thread)
    thread.start()
    thread.join()
    end = time.time()

    eval_result = full_evaluation(model, X, y, task)

    if visualize:
        try:
            plt.plot(model.losses)
            plt.title("Grafik Loss selama Training")
            plt.xlabel("Epoch")
            plt.ylabel("Loss")
            plt.grid(True)
            plt.show()
        except:
            logging.warning("Gagal visualisasi. Pastikan matplotlib terinstal.")

    print("📌 Waktu training: {:.2f} detik".format(end - start))
    print("🎯 Hasil evaluasi:", eval_result)
    return model, eval_result

# === Multi Model Training (opsional) ===
def train_multiple_models(n=3, input_size=4, output_size=1, task="classification"):
    models = []
    for i in range(n):
        print(f"🚀 Training model-{i+1}")
        model = CustomAIModel(
            layer_sizes=[input_size, 16, 8, output_size],
            activations=["relu", "tanh", "sigmoid"],
            loss="mse" if task == "regression" else "cross_entropy"
        )
        train_model(model, task=task)
        models.append(model)
    return models

# === Eksekusi Utama ===
if __name__ == "__main__":
    model = CustomAIModel(
        layer_sizes=[4, 16, 8, 1],
        activations=["relu", "tanh", "sigmoid"],
        loss="cross_entropy"
    )
    train_model(model, task="classification", use_autograd=False)