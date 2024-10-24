import math
import numpy as np
from typing import List, Tuple

class XORNeuralNetwork:
    def __init__(self, learning_rate: float = 0.1):
        self.learning_rate = learning_rate

        # Initialize weights with Xavier/Glorot initialization
        scale = np.sqrt(2.0 / (2 + 2))  # sqrt(2 / (input_dim + output_dim))
        self.w_hidden_1 = np.random.uniform(-scale, scale, 3)
        self.w_hidden_2 = np.random.uniform(-scale, scale, 3)
        self.w_output = np.random.uniform(-scale, scale, 3)

        # Track metrics
        self.errors = []
        self.accuracies = []

    @staticmethod
    def sigmoid(x: float) -> float:
        """Sigmoid activation function with numerical stability."""
        return 1 / (1 + math.exp(-max(min(x, 709), -709)))

    def forward_pass(self, x_input: List[float]) -> Tuple[float, float, float, float, float]:
        
        # Perform forward pass through the network.

        # Hidden layer calculations
        y_hidden_1 = self.w_hidden_1[0] + x_input[0] * self.w_hidden_1[1] + x_input[1] * self.w_hidden_1[2]
        o_hidden_1 = self.sigmoid(y_hidden_1)

        y_hidden_2 = self.w_hidden_2[0] + x_input[0] * self.w_hidden_2[1] + x_input[1] * self.w_hidden_2[2]
        o_hidden_2 = self.sigmoid(y_hidden_2)

        # Output layer calculations
        y_output = self.w_output[0] + o_hidden_1 * self.w_output[1] + o_hidden_2 * self.w_output[2]
        o_output = self.sigmoid(y_output)

        return o_output, o_hidden_1, o_hidden_2, y_hidden_1, y_hidden_2

    def train_step(self, x_input: List[float], target: int, verbose: bool = False) -> float:
        
        # Perform one training step on a single input-target pair.

        # Forward pass
        o_output, o_hidden_1, o_hidden_2, y_hidden_1, y_hidden_2 = self.forward_pass(x_input)

        if verbose:
            print(f"Input: {x_input}, Target: {target}, Output: {o_output:.3f}")

        # Calculate errors
        error_output = target - o_output
        gradient_output = error_output * o_output * (1 - o_output)

        # Update output layer weights
        self.w_output[0] += self.learning_rate * gradient_output  # bias
        self.w_output[1] += self.learning_rate * gradient_output * o_hidden_1
        self.w_output[2] += self.learning_rate * gradient_output * o_hidden_2

        # Calculate hidden layer errors and gradients
        error_hidden_1 = gradient_output * self.w_output[1]
        error_hidden_2 = gradient_output * self.w_output[2]

        gradient_hidden_1 = error_hidden_1 * o_hidden_1 * (1 - o_hidden_1)
        gradient_hidden_2 = error_hidden_2 * o_hidden_2 * (1 - o_hidden_2)

        # Update hidden layer weights
        self.w_hidden_1[0] += self.learning_rate * gradient_hidden_1  # bias
        self.w_hidden_1[1] += self.learning_rate * gradient_hidden_1 * x_input[0]
        self.w_hidden_1[2] += self.learning_rate * gradient_hidden_1 * x_input[1]

        self.w_hidden_2[0] += self.learning_rate * gradient_hidden_2  # bias
        self.w_hidden_2[1] += self.learning_rate * gradient_hidden_2 * x_input[0]
        self.w_hidden_2[2] += self.learning_rate * gradient_hidden_2 * x_input[1]

        return error_output ** 2

    def train_epoch(self, verbose: bool = False) -> Tuple[float, float]:
        """
        Train the network for one complete epoch using XOR training data.

        Args:
            verbose: Whether to print training progress

        Returns:
            Tuple of (mean_squared_error, accuracy) for this epoch
        """
        # Training data for XOR gate
        training_data = [
            ([0, 0], 0),
            ([0, 1], 1),
            ([1, 0], 1),
            ([1, 1], 0)
        ]

        total_error = 0
        correct_predictions = 0

        for x_input, target in training_data:
            error = self.train_step(x_input, target, verbose)
            total_error += error

            # Check if prediction is correct
            prediction = 1 if self.forward_pass(x_input)[0] > 0.5 else 0
            if prediction == target:
                correct_predictions += 1

        accuracy = correct_predictions / len(training_data)
        return total_error / len(training_data), accuracy

    def train(self, epochs: int, early_stopping_threshold: float = 0.98) -> None:
        """
        Train the network for multiple epochs with early stopping.

        Args:
            epochs: Maximum number of epochs to train
            early_stopping_threshold: Stop training if accuracy reaches this threshold
        """
        for epoch in range(epochs):
            mse, accuracy = self.train_epoch(verbose=(epoch % 1000 == 0))
            self.errors.append(mse)
            self.accuracies.append(accuracy)

            # Early stopping if accuracy is good enough
            if accuracy >= early_stopping_threshold:
                print(f"\nReached {accuracy:.2%} accuracy at epoch {epoch + 1}. Stopping early.")
                break

            if epoch % 1000 == 0:
                print(f"Epoch {epoch + 1}: MSE = {mse:.4f}, Accuracy = {accuracy:.2%}")

    def evaluate(self) -> None:
        """Evaluate the network on all possible XOR inputs."""
        print("\nFinal Evaluation:")
        for x1, x2 in [(0,0), (0,1), (1,0), (1,1)]:
            output = self.forward_pass([x1, x2])[0]
            target = 1 if x1 != x2 else 0
            print(f"Input: [{x1}, {x2}], Target: {target}, Output: {output:.3f}")

def main():
    # Set random seed for reproducibility
    np.random.seed(42)

    # Create and train network
    nn = XORNeuralNetwork(learning_rate=0.1)
    nn.train(epochs=2000, early_stopping_threshold=0.98)

    # Final evaluation
    nn.evaluate()

if __name__ == "__main__":
    main()
