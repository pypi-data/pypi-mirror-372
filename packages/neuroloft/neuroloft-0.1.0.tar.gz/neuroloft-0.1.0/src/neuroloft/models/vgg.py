import torch

from torch import nn as nn


class VGG16(nn.Module):
    """
    VGG16-inspired Convolutional Neural Network for Caltech-256 classification.

    This architecture follows the VGG16 design principles with deep convolutional
    layers using small 3x3 kernels. The network progressively increases feature
    map depth while reducing spatial dimensions, allowing it to learn hierarchical
    visual representations from simple edges to complex object patterns.

    Architecture Overview:
    =====================
    Input: [batch, 3, 224, 224] RGB images

    Conv Block 1: 3 → 64 channels, 224×224 → 112×112
    - Conv2d(3→64, 3×3) + ReLU
    - Conv2d(64→64, 3×3) + ReLU
    - MaxPool2d(2×2) → 112×112

    Conv Block 2: 64 → 128 channels, 112×112 → 56×56
    - Conv2d(64→128, 3×3) + ReLU
    - Conv2d(128→128, 3×3) + ReLU
    - MaxPool2d(2×2) → 56×56

    Conv Block 3: 128 → 256 channels, 56×56 → 28×28
    - Conv2d(128→256, 3×3) + ReLU
    - Conv2d(256→256, 3×3) + ReLU
    - Conv2d(256→256, 3×3) + ReLU (deeper feature extraction)
    - MaxPool2d(2×2) → 28×28

    Conv Block 4: 256 → 512 channels, 28×28 → 14×14
    - Conv2d(256→512, 3×3) + ReLU
    - Conv2d(512→512, 3×3) + ReLU
    - Conv2d(512→512, 3×3) + ReLU
    - MaxPool2d(2×2) → 14×14

    Conv Block 5: 512 → 512 channels, 14×14 → 7×7
    - Conv2d(512→512, 3×3) + ReLU
    - Conv2d(512→512, 3×3) + ReLU
    - Conv2d(512→512, 3×3) + ReLU
    - MaxPool2d(2×2) → 7×7

    Classifier: Dense layers for final classification
    - Flatten: 512×7×7 = 25,088 features
    - Linear: 25,088 → 4,096 + ReLU (implicit)
    - Linear: 4,096 → 4,096 + ReLU (implicit)
    - Linear: 4,096 → 256 classes (output logits)

    Total Parameters: ~135M (significantly larger than simple CNNs)

    Args:
        input_channels (int): Number of input channels (3 for RGB images)
        output_classes (int): Number of output classes (256 for Caltech-256)
    """

    def __init__(self, input_channels: int, output_classes: int):
        super().__init__()

        # Block 1: Initial feature extraction (3→64 channels)
        # Learns basic features like edges, corners, simple textures
        self.conv_block_1 = nn.Sequential(
            nn.Conv2d(in_channels=input_channels, out_channels=64,
                     kernel_size=3, stride=1, padding=1),  # Maintain spatial size
            nn.ReLU(inplace=True),  # Non-linear activation
            nn.Conv2d(in_channels=64, out_channels=64,
                     kernel_size=3, stride=1, padding=1),  # Deeper feature extraction
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2)  # Downsample: 224×224 → 112×112
        )

        # Block 2: Mid-level feature extraction (64→128 channels)
        # Learns more complex patterns and shapes
        self.conv_block_2 = nn.Sequential(
            nn.Conv2d(in_channels=64, out_channels=128,
                     kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=128, out_channels=128,
                     kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2)  # Downsample: 112×112 → 56×56
        )

        # Block 3: High-level feature extraction (128→256 channels)
        # Learns object parts and more abstract patterns
        self.conv_block_3 = nn.Sequential(
            nn.Conv2d(in_channels=128, out_channels=256,
                     kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=256, out_channels=256,
                     kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=256, out_channels=256,
                     kernel_size=3, stride=1, padding=1),  # Third conv for deeper learning
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2)  # Downsample: 56×56 → 28×28
        )

        # Block 4: Deep feature extraction (256→512 channels)
        # Learns complex object representations and semantic features
        self.conv_block_4 = nn.Sequential(
            nn.Conv2d(in_channels=256, out_channels=512,
                     kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=512, out_channels=512,
                     kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=512, out_channels=512,
                     kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2)  # Downsample: 28×28 → 14×14
        )

        # Block 5: Deepest feature extraction (512→512 channels)
        # Learns the most abstract and discriminative features
        self.conv_block_5 = nn.Sequential(
            nn.Conv2d(in_channels=512, out_channels=512,
                     kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=512, out_channels=512,
                     kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=512, out_channels=512,
                     kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2)  # Final downsample: 14×14 → 7×7
        )

        # Classification head: Convert feature maps to class predictions
        # Dense layers aggregate spatial information for final decision
        self.classifier = nn.Sequential(
            nn.Flatten(),  # Flatten feature maps: [batch, 512, 7, 7] → [batch, 25088]
            nn.Linear(in_features=512*7*7, out_features=4096),  # First dense layer
            nn.ReLU(),
            nn.Linear(in_features=4096, out_features=4096),     # Second dense layer
            nn.ReLU(),
            nn.Linear(in_features=4096, out_features=output_classes)  # Output layer: 256 classes
        )

    def forward(self, input_data):
        """
        Forward pass through the VGG16 network.

        Args:
            input_data (torch.Tensor): Input images, shape [batch_size, 3, 224, 224]

        Returns:
            torch.Tensor: Raw logits for 256 classes, shape [batch_size, 256]
        """
        # Progressive feature extraction through convolutional blocks
        x = self.conv_block_1(input_data)  # [batch, 3, 224, 224] → [batch, 64, 112, 112]
        x = self.conv_block_2(x)           # [batch, 64, 112, 112] → [batch, 128, 56, 56]
        x = self.conv_block_3(x)           # [batch, 128, 56, 56] → [batch, 256, 28, 28]
        x = self.conv_block_4(x)           # [batch, 256, 28, 28] → [batch, 512, 14, 14]
        x = self.conv_block_5(x)           # [batch, 512, 14, 14] → [batch, 512, 7, 7]

        # Classification based on extracted features
        return self.classifier(x)          # [batch, 512, 7, 7] → [batch, 256]


class VGG19(nn.Module):
    """
    VGG19-inspired Convolutional Neural Network for Caltech-256 classification.

    This architecture follows the VGG19 design principles with deeper convolutional
    layers using small 3x3 kernels. Compared to VGG16, VGG19 has additional
    convolutional layers in blocks 3, 4, and 5, providing more representational
    capacity for complex visual pattern recognition.

    Architecture Overview:
    =====================
    Input: [batch, 3, 224, 224] RGB images

    Conv Block 1: 3 → 64 channels, 224×224 → 112×112
    - Conv2d(3→64, 3×3) + ReLU
    - Conv2d(64→64, 3×3) + ReLU
    - MaxPool2d(2×2) → 112×112

    Conv Block 2: 64 → 128 channels, 112×112 → 56×56
    - Conv2d(64→128, 3×3) + ReLU
    - Conv2d(128→128, 3×3) + ReLU
    - MaxPool2d(2×2) → 56×56

    Conv Block 3: 128 → 256 channels, 56×56 → 28×28
    - Conv2d(128→256, 3×3) + ReLU
    - Conv2d(256→256, 3×3) + ReLU
    - Conv2d(256→256, 3×3) + ReLU
    - Conv2d(256→256, 3×3) + ReLU (4th layer - VGG19 addition)
    - MaxPool2d(2×2) → 28×28

    Conv Block 4: 256 → 512 channels, 28×28 → 14×14
    - Conv2d(256→512, 3×3) + ReLU
    - Conv2d(512→512, 3×3) + ReLU
    - Conv2d(512→512, 3×3) + ReLU
    - Conv2d(512→512, 3×3) + ReLU (4th layer - VGG19 addition)
    - MaxPool2d(2×2) → 14×14

    Conv Block 5: 512 → 512 channels, 14×14 → 7×7
    - Conv2d(512→512, 3×3) + ReLU
    - Conv2d(512→512, 3×3) + ReLU
    - Conv2d(512→512, 3×3) + ReLU
    - Conv2d(512→512, 3×3) + ReLU (4th layer - VGG19 addition)
    - MaxPool2d(2×2) → 7×7

    Classifier: Dense layers for final classification
    - Flatten: 512×7×7 = 25,088 features
    - Linear: 25,088 → 4,096 + ReLU (implicit)
    - Linear: 4,096 → 4,096 + ReLU (implicit)
    - Linear: 4,096 → 256 classes (output logits)

    Total Parameters: ~144M (larger than VGG16 due to additional conv layers)

    Key Differences from VGG16:
    - Blocks 3, 4, and 5 each have 4 convolutional layers instead of 3
    - Additional 3 convolutional layers increase model capacity
    - More parameters allow for learning more complex feature representations
    - Deeper architecture may capture more nuanced visual patterns

    Args:
        input_channels (int): Number of input channels (3 for RGB images)
        output_classes (int): Number of output classes (256 for Caltech-256)
    """

    def __init__(self, input_channels: int, output_classes: int):
        super().__init__()

        # Block 1: Initial feature extraction (3→64 channels)
        # Same as VGG16 - learns basic features like edges, corners, simple textures
        self.conv_block_1 = nn.Sequential(
            nn.Conv2d(in_channels=input_channels, out_channels=64,
                     kernel_size=3, stride=1, padding=1),  # Maintain spatial size
            nn.ReLU(inplace=True),  # Non-linear activation
            nn.Conv2d(in_channels=64, out_channels=64,
                     kernel_size=3, stride=1, padding=1),  # Deeper feature extraction
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2)  # Downsample: 224×224 → 112×112
        )

        # Block 2: Mid-level feature extraction (64→128 channels)
        # Same as VGG16 - learns more complex patterns and shapes
        self.conv_block_2 = nn.Sequential(
            nn.Conv2d(in_channels=64, out_channels=128,
                     kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=128, out_channels=128,
                     kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2)  # Downsample: 112×112 → 56×56
        )

        # Block 3: High-level feature extraction (128→256 channels)
        # VGG19: 4 conv layers (vs 3 in VGG16) - deeper object part learning
        self.conv_block_3 = nn.Sequential(
            nn.Conv2d(in_channels=128, out_channels=256,
                     kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=256, out_channels=256,
                     kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=256, out_channels=256,
                     kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=256, out_channels=256,
                     kernel_size=3, stride=1, padding=1),  # 4th conv layer - VGG19 addition
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2)  # Downsample: 56×56 → 28×28
        )

        # Block 4: Deep feature extraction (256→512 channels)
        # VGG19: 4 conv layers (vs 3 in VGG16) - more complex object representations
        self.conv_block_4 = nn.Sequential(
            nn.Conv2d(in_channels=256, out_channels=512,
                     kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=512, out_channels=512,
                     kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=512, out_channels=512,
                     kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=512, out_channels=512,
                     kernel_size=3, stride=1, padding=1),  # 4th conv layer - VGG19 addition
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2)  # Downsample: 28×28 → 14×14
        )

        # Block 5: Deepest feature extraction (512→512 channels)
        # VGG19: 4 conv layers (vs 3 in VGG16) - most abstract discriminative features
        self.conv_block_5 = nn.Sequential(
            nn.Conv2d(in_channels=512, out_channels=512,
                     kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=512, out_channels=512,
                     kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=512, out_channels=512,
                     kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=512, out_channels=512,
                     kernel_size=3, stride=1, padding=1),  # 4th conv layer - VGG19 addition
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2)  # Final downsample: 14×14 → 7×7
        )

        # Classification head: Same as VGG16 - convert feature maps to class predictions
        # Dense layers aggregate spatial information for final decision
        self.classifier = nn.Sequential(
            nn.Flatten(),  # Flatten feature maps: [batch, 512, 7, 7] → [batch, 25088]
            nn.Linear(in_features=512*7*7, out_features=4096),  # First dense layer
            nn.ReLU(),
            nn.Linear(in_features=4096, out_features=4096),     # Second dense layer
            nn.ReLU(),
            nn.Linear(in_features=4096, out_features=output_classes)  # Output layer: 256 classes
        )

    def forward(self, input_data):
        """
        Forward pass through the VGG19 network.

        Args:
            input_data (torch.Tensor): Input images, shape [batch_size, 3, 224, 224]

        Returns:
            torch.Tensor: Raw logits for 256 classes, shape [batch_size, 256]
        """
        # Progressive feature extraction through convolutional blocks
        # Each block has more layers than VGG16, providing deeper feature learning
        x = self.conv_block_1(input_data)  # [batch, 3, 224, 224] → [batch, 64, 112, 112]
        x = self.conv_block_2(x)           # [batch, 64, 112, 112] → [batch, 128, 56, 56]
        x = self.conv_block_3(x)           # [batch, 128, 56, 56] → [batch, 256, 28, 28] (4 conv layers)
        x = self.conv_block_4(x)           # [batch, 256, 28, 28] → [batch, 512, 14, 14] (4 conv layers)
        x = self.conv_block_5(x)           # [batch, 512, 14, 14] → [batch, 512, 7, 7] (4 conv layers)

        # Classification based on extracted features
        return self.classifier(x)          # [batch, 512, 7, 7] → [batch, 256]