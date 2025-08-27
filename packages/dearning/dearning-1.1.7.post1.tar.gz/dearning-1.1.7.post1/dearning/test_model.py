import unittest
import numpy as np
from dearning.model import CustomAIModel

class TestCustomAIModel(unittest.TestCase):
    def setUp(self):
        # Inisialisasi model multi-layer untuk semua tes
        self.model = CustomAIModel(
            layer_sizes=[4, 8, 1],
            activations=['relu', 'sigmoid']
        )
        self.X = np.random.rand(100, 4)
        self.y_class = (np.sum(self.X, axis=1, keepdims=True) > 2).astype(float)
        self.y_reg = np.sum(self.X, axis=1, keepdims=True)

    def test_model_initialization(self):
        self.assertEqual(len(self.model.weights), 2)
        self.assertEqual(self.model.weights[0].shape, (4, 8))
        self.assertEqual(self.model.weights[1].shape, (8, 1))

    def test_forward_output_shape(self):
        output = self.model.forward(self.X[:10])
        self.assertEqual(output.shape, (10, 1))

    def test_forward_output_range(self):
        output = self.model.forward(self.X[:10])
        self.assertTrue(np.all((output >= 0) & (output <= 1)), "Output di luar rentang sigmoid")

    def test_train_reduces_loss(self):
        # Hitung loss sebelum dan sesudah training
        y = self.y_class
        loss_before = self.model.compute_loss(self.model.forward(self.X), y)
        self.model.train(self.X, y, epochs=10, learning_rate=0.05, batch_size=16, verbose=False)
        loss_after = self.model.compute_loss(self.model.forward(self.X), y)
        self.assertLess(loss_after, loss_before, "Loss tidak berkurang setelah training")

    def test_train_no_crash(self):
        try:
            self.model.train(self.X, self.y_class, epochs=5, batch_size=20, verbose=False)
        except Exception as e:
            self.fail(f"Training crash: {e}")

if __name__ == '__main__':
    unittest.main()