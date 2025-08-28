# Core PyTorch libraries for deep learning
import torch

# Dataset handling and preprocessing
from torch.utils.data.dataloader import DataLoader

# Neural network components and optimization
from torch import nn as nn
from torch import optim

def train_step(input_dataloader: DataLoader, input_model: nn.Module, loss_function: nn.Module, optimizer: optim.Optimizer,
               current_device: torch.device, acc_fun=None) -> None:
    """
    Perform one training epoch over the entire Caltech-256 dataset.

    This function handles the complete training loop for one epoch, processing
    ~24,485 training images in batches of 32. For Caltech-256's 256 classes,
    the model must learn to distinguish between highly diverse object categories.

    Args:
        input_dataloader (DataLoader): DataLoader containing Caltech-256 training data
        input_model (nn.Module): VGG16-style CNN model to train
        loss_function (nn.Module): CrossEntropyLoss for 256-class classification
        optimizer (optim.Optimizer): SGD optimizer for parameter updates
        current_device (torch.device): Device to run computations on (preferably GPU)
        acc_fun (callable): Function to calculate accuracy percentage

    Returns:
        None: Prints training loss and accuracy for the epoch

    Note:
        With 256 classes, random accuracy would be ~0.39%. Any accuracy above
        5-10% indicates the model is learning meaningful visual patterns.
    """
    train_loss, train_acc = 0, 0
    # Move model to specified device (GPU recommended for large models)
    input_model = input_model.to(current_device)

    # Iterate through all batches in the training dataset (~765 batches)
    for batch, (X, y) in enumerate(input_dataloader):
        # Set model to training mode (enables dropout, batch norm updates)
        input_model.train()

        # Move batch data to the same device as model (critical for GPU training)
        X, y = X.to(current_device), y.to(current_device)

        # Forward pass: compute model predictions for 256 classes
        model_outputs = input_model(X)  # Shape: [batch_size, 256]

        # Calculate cross-entropy loss for multi-class classification
        current_loss = loss_function(model_outputs, y)

        # Accumulate loss and accuracy for this batch
        train_loss += current_loss.item()
        if acc_fun is not None:
            train_acc += acc_fun(y_true=y, y_pred=torch.argmax(model_outputs, dim=1))

        # Backward pass: compute gradients for ~135M parameters
        optimizer.zero_grad()  # Clear previous gradients
        current_loss.backward()  # Compute gradients via backpropagation
        optimizer.step()  # Update model parameters

        # Print progress every 100 batches (more frequent for large datasets)
        if batch % 100 == 0:
            print(f"Looked at {batch * len(X):,}/{len(input_dataloader.dataset):,} samples")

    # Calculate average loss and accuracy over all batches
    train_loss /= len(input_dataloader)
    print(f"\nTrain loss: {train_loss:.5f}")
    if acc_fun is not None:
        train_acc /= len(input_dataloader)
        print(f"Train accuracy: {train_acc:.2f}%")


def test_step(input_dataloader: DataLoader, input_model: nn.Module, loss_function: nn.Module,
              current_device: torch.device, acc_fun=None) -> None:
    """
    Evaluate VGG16 model performance on Caltech-256 test dataset.

    This function processes ~6,122 test images to evaluate how well the model
    generalizes to unseen data. For Caltech-256, achieving >20% accuracy
    indicates good performance, while >40% would be excellent.

    Args:
        input_dataloader (DataLoader): DataLoader containing Caltech-256 test data
        input_model (nn.Module): Trained VGG16-style CNN model to evaluate
        loss_function (nn.Module): CrossEntropyLoss for 256-class classification
        current_device (torch.device): Device to run computations on (preferably GPU)
        acc_fun (callable): Function to calculate accuracy percentage

    Returns:
        None: Prints test loss and accuracy

    Note:
        Test accuracy is the key metric for model performance. With 256 classes,
        even 10-15% accuracy represents significant learning beyond random chance.
    """
    test_loss, test_acc = 0, 0
    # Move model to specified device
    input_model = input_model.to(current_device)
    # Set model to evaluation mode (disables dropout, fixes batch norm)
    input_model.eval()

    # Disable gradient computation for faster inference and memory efficiency
    with torch.inference_mode():
        for batch, (X, y) in enumerate(input_dataloader):
            # Move batch data to the same device as model
            X, y = X.to(current_device), y.to(current_device)

            # Forward pass: compute model predictions for 256 classes
            model_outputs = input_model(X)  # Shape: [batch_size, 256]

            # Calculate cross-entropy loss for evaluation
            current_loss = loss_function(model_outputs, y)

            # Accumulate loss and accuracy for this batch
            test_loss += current_loss.item()
            if acc_fun is not None:
                test_acc += acc_fun(y_true=y, y_pred=torch.argmax(model_outputs, dim=1))

        # Calculate average loss and accuracy over all test batches (~192 batches)
        test_loss /= len(input_dataloader)
        print(f"Test loss: {test_loss:.5f}")

        if acc_fun is not None:
            test_acc /= len(input_dataloader)
            print(f"Test accuracy: {test_acc:.2f}%")


def softmax_prediction_step(input_data: torch.Tensor, input_model: nn.Module, current_device: torch.device) -> torch.types.Number:
    """
    Make a prediction on a single Caltech-256 image using the trained VGG16 model.

    This function processes a single 224x224 RGB image and returns the predicted
    class among the 256 possible categories. The model outputs probabilities for
    all classes, and we select the one with the highest confidence.

    Args:
        input_data (torch.Tensor): Input image tensor, shape [1, 3, 224, 224]
        input_model (nn.Module): Trained VGG16-style CNN model
        current_device (torch.device): Device to run computations on (CPU/GPU)

    Returns:
        int: Predicted class index (0-255 for Caltech-256)

    Example:
        >>> image = torch.randn(1, 3, 224, 224)  # Single Caltech-256 image
        >>> predicted_class = prediction_step(image, model, device)
        >>> print(f"Predicted class: {classes[predicted_class]}")
        >>> # Output: "Predicted class: 042.coffin" (for example)
    """
    # Move model to specified device and set to evaluation mode
    input_model = input_model.to(current_device)
    input_model = input_model.eval()

    max_classes_idx = -1
    # Disable gradient computation for faster inference
    with torch.inference_mode():
        # Move input data to the same device as model
        input_data = input_data.to(current_device)

        # Forward pass: get model predictions (logits for 256 classes)
        model_outputs = input_model(input_data)  # Shape: [1, 256]

        # Apply softmax to convert logits to probabilities
        softmax_output = torch.softmax(input=model_outputs, dim=1)

        # Get the class with highest probability (most confident prediction)
        max_object = torch.argmax(input=softmax_output, dim=1)
        max_classes_idx = max_object

    # Return as Python integer (single prediction index 0-255)
    return max_classes_idx.item()