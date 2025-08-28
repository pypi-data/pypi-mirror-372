import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, List, Tuple

# -----------------------
# BasicBlock (used in ResNet-18/34)
# -----------------------
class BasicBlock(nn.Module):
    """
    Basic residual block for ResNet-18 and ResNet-34.
    
    This block consists of two 3x3 convolutional layers with batch normalization
    and ReLU activation, plus a skip connection (residual connection).
    
    Architecture:
    Input -> Conv3x3 -> BN -> ReLU -> Conv3x3 -> BN -> (+) -> ReLU -> Output
               |                                        ^
               |-> Downsample (if needed) ---------------|
    
    Args:
        in_channels (int): Number of input channels
        out_channels (int): Number of output channels
        stride (int, optional): Stride for the first convolution. Defaults to 1.
        downsample (nn.Module, optional): Downsample layer for skip connection. Defaults to None.
    
    Attributes:
        expansion (int): Channel expansion factor (1 for BasicBlock)
    """
    expansion = 1  # BasicBlock doesn't expand channels

    def __init__(self, in_channels: int, out_channels: int, stride: int = 1, 
                 downsample: Optional[nn.Module] = None):
        super(BasicBlock, self).__init__()
        
        # First convolutional layer - may downsample spatial dimensions
        self.conv1 = nn.Conv2d(
            in_channels, out_channels, kernel_size=3,
            stride=stride, padding=1, bias=False
        )
        self.bn1 = nn.BatchNorm2d(out_channels)
        
        # Second convolutional layer - maintains spatial dimensions
        self.conv2 = nn.Conv2d(
            out_channels, out_channels, kernel_size=3,
            stride=1, padding=1, bias=False
        )
        self.bn2 = nn.BatchNorm2d(out_channels)
        
        # Activation function (shared for memory efficiency)
        self.relu = nn.ReLU(inplace=True)
        
        # Optional downsample layer for skip connection dimension matching
        self.downsample = downsample

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the BasicBlock.
        
        Args:
            x (torch.Tensor): Input tensor of shape (N, C_in, H, W)
            
        Returns:
            torch.Tensor: Output tensor of shape (N, C_out, H', W')
                         where H' and W' depend on stride
        """
        # Store input for skip connection
        identity = x  # Shape: (N, C_in, H, W)

        # First conv-bn-relu block
        out = self.conv1(x)      # Shape: (N, C_out, H/stride, W/stride)
        out = self.bn1(out)      # Shape: (N, C_out, H/stride, W/stride)
        out = self.relu(out)     # Shape: (N, C_out, H/stride, W/stride)

        # Second conv-bn block (no ReLU yet)
        out = self.conv2(out)    # Shape: (N, C_out, H/stride, W/stride)
        out = self.bn2(out)      # Shape: (N, C_out, H/stride, W/stride)

        # Apply downsample to identity if dimensions don't match
        if self.downsample is not None:
            identity = self.downsample(x)  # Shape: (N, C_out, H/stride, W/stride)

        # Residual connection: element-wise addition
        out += identity          # Shape: (N, C_out, H/stride, W/stride)
        out = self.relu(out)     # Final activation after residual connection
        
        return out


# -----------------------
# Bottleneck (used in ResNet-50/101/152)
# -----------------------
class Bottleneck(nn.Module):
    """
    Bottleneck residual block for deeper ResNet architectures (ResNet-50/101/152).
    
    This block uses a "bottleneck" design with 1x1 -> 3x3 -> 1x1 convolutions
    to reduce computational complexity while maintaining representational power.
    The 1x1 convolutions reduce and then expand the number of channels.
    
    Architecture:
    Input -> Conv1x1 -> BN -> ReLU -> Conv3x3 -> BN -> ReLU -> Conv1x1 -> BN -> (+) -> ReLU -> Output
               |                                                                ^
               |-> Downsample (if needed) ------------------------------------|
    
    Args:
        in_channels (int): Number of input channels
        mid_channels (int): Number of intermediate channels (bottleneck width)
        stride (int, optional): Stride for the 3x3 convolution. Defaults to 1.
        downsample (nn.Module, optional): Downsample layer for skip connection. Defaults to None.
    
    Attributes:
        expansion (int): Channel expansion factor (4 for Bottleneck)
    """
    expansion = 4  # Bottleneck expands channels by factor of 4

    def __init__(self, in_channels: int, mid_channels: int, stride: int = 1, 
                 downsample: Optional[nn.Module] = None):
        super(Bottleneck, self).__init__()

        # 1x1 convolution for channel reduction (bottleneck)
        self.conv1 = nn.Conv2d(in_channels, mid_channels, kernel_size=1, bias=False)
        self.bn1 = nn.BatchNorm2d(mid_channels)

        # 3x3 convolution for spatial processing (may downsample)
        self.conv2 = nn.Conv2d(
            mid_channels, mid_channels, kernel_size=3,
            stride=stride, padding=1, bias=False
        )
        self.bn2 = nn.BatchNorm2d(mid_channels)

        # 1x1 convolution for channel expansion
        self.conv3 = nn.Conv2d(
            mid_channels, mid_channels * self.expansion, 
            kernel_size=1, bias=False
        )
        self.bn3 = nn.BatchNorm2d(mid_channels * self.expansion)

        # Shared activation function for memory efficiency
        self.relu = nn.ReLU(inplace=True)
        
        # Optional downsample layer for skip connection dimension matching
        self.downsample = downsample

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the Bottleneck block.
        
        Args:
            x (torch.Tensor): Input tensor of shape (N, C_in, H, W)
            
        Returns:
            torch.Tensor: Output tensor of shape (N, C_out, H', W')
                         where C_out = mid_channels * expansion
                         and H', W' depend on stride
        """
        # Store input for skip connection
        identity = x  # Shape: (N, C_in, H, W)

        # First 1x1 conv-bn-relu (channel reduction)
        out = self.conv1(x)      # Shape: (N, mid_channels, H, W)
        out = self.bn1(out)      # Shape: (N, mid_channels, H, W)
        out = self.relu(out)     # Shape: (N, mid_channels, H, W)

        # 3x3 conv-bn-relu (spatial processing, possible downsampling)
        out = self.conv2(out)    # Shape: (N, mid_channels, H/stride, W/stride)
        out = self.bn2(out)      # Shape: (N, mid_channels, H/stride, W/stride)
        out = self.relu(out)     # Shape: (N, mid_channels, H/stride, W/stride)

        # Second 1x1 conv-bn (channel expansion, no ReLU yet)
        out = self.conv3(out)    # Shape: (N, mid_channels*4, H/stride, W/stride)
        out = self.bn3(out)      # Shape: (N, mid_channels*4, H/stride, W/stride)

        # Apply downsample to identity if dimensions don't match
        if self.downsample is not None:
            identity = self.downsample(x)  # Shape: (N, mid_channels*4, H/stride, W/stride)

        # Residual connection: element-wise addition
        out += identity          # Shape: (N, mid_channels*4, H/stride, W/stride)
        out = self.relu(out)     # Final activation after residual connection
        
        return out


# -----------------------
# ResNet (Generic)
# -----------------------
class ResNet(nn.Module):
    """
    ResNet (Residual Network) implementation supporting various architectures.
    
    This implementation supports both ImageNet-style (224x224) and CIFAR-style (32x32)
    inputs with configurable depth and block types. The network uses residual connections
    to enable training of very deep networks by addressing the vanishing gradient problem.
    
    Key Features:
    - Supports both BasicBlock (ResNet-18/34) and Bottleneck (ResNet-50/101/152)
    - Configurable for ImageNet (224x224) or CIFAR (32x32) datasets
    - Proper weight initialization and optimization techniques
    - Memory-efficient implementation with inplace operations
    
    Architecture Overview:
    Input -> Initial Conv + Pool -> Layer1 -> Layer2 -> Layer3 -> Layer4 -> AvgPool -> FC -> Output
    
    Args:
        input_channels (int): Number of input channels (e.g., 3 for RGB)
        block (nn.Module): Block type (BasicBlock or Bottleneck)
        layers (List[int]): Number of blocks in each layer
        output_classes (int): Number of output classes
        cifar (bool, optional): Whether to use CIFAR-optimized architecture. Defaults to False.
        
    Attributes:
        in_channels (int): Current number of channels (used during layer construction)
    """
    
    def __init__(self, input_channels: int, block, layers: List[int], 
                 output_classes: int, cifar: bool = False):
        super(ResNet, self).__init__()
        
        # Initialize channel tracking for layer construction
        self.in_channels = 64 if not cifar else 16
        self.cifar = cifar
        
        # Initial convolutional layer - different for ImageNet vs CIFAR
        if cifar:  
            # CIFAR-style: smaller kernel, no stride, no maxpool
            # Input: (N, 3, 32, 32) -> Output: (N, 16, 32, 32)
            self.conv1 = nn.Conv2d(
                input_channels, 16, kernel_size=3, 
                stride=1, padding=1, bias=False
            )
            self.bn1 = nn.BatchNorm2d(16)
        else:  
            # ImageNet-style: large kernel with stride for downsampling
            # Input: (N, 3, 224, 224) -> Output: (N, 64, 112, 112)
            self.conv1 = nn.Conv2d(
                input_channels, 64, kernel_size=7, 
                stride=2, padding=3, bias=False
            )
            self.bn1 = nn.BatchNorm2d(64)

        # Shared activation function
        self.relu = nn.ReLU(inplace=True)
        
        # Max pooling (only for ImageNet-style)
        # ImageNet: (N, 64, 112, 112) -> (N, 64, 56, 56)
        self.maxpool = None if cifar else nn.MaxPool2d(
            kernel_size=3, stride=2, padding=1
        )

        # Build residual layers with increasing channel dimensions
        # Layer dimensions for ImageNet: 56x56 -> 28x28 -> 14x14 -> 7x7
        # Layer dimensions for CIFAR: 32x32 -> 16x16 -> 8x8
        self.layer1 = self._make_layer(
            block, 64 if not cifar else 16, layers[0], stride=1
        )
        self.layer2 = self._make_layer(
            block, 128 if not cifar else 32, layers[1], stride=2
        )
        self.layer3 = self._make_layer(
            block, 256 if not cifar else 64, layers[2], stride=2
        )
        
        # Layer 4 is optional (not used for CIFAR to prevent over-downsampling)
        self.layer4 = None if cifar else self._make_layer(
            block, 512, layers[3], stride=2
        )

        # Global average pooling to convert feature maps to fixed-size vectors
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        
        # Calculate final feature dimension based on architecture
        if cifar:
            final_dim = 64 * block.expansion  # CIFAR uses layer3 output
        else:
            final_dim = 512 * block.expansion  # ImageNet uses layer4 output
            
        # Final classification layer
        self.fc = nn.Linear(final_dim, output_classes)
        
        # Initialize weights for better convergence
        self._initialize_weights()

    def _make_layer(self, block, out_channels: int, num_blocks: int, 
                   stride: int) -> nn.Sequential:
        """
        Construct a residual layer consisting of multiple blocks.
        
        Args:
            block: Block class (BasicBlock or Bottleneck)
            out_channels (int): Output channels for this layer
            num_blocks (int): Number of blocks in this layer
            stride (int): Stride for the first block (for downsampling)
            
        Returns:
            nn.Sequential: Sequential container of residual blocks
        """
        downsample = None
        
        # Create downsample layer if input/output dimensions don't match
        if stride != 1 or self.in_channels != out_channels * block.expansion:
            downsample = nn.Sequential(
                nn.Conv2d(
                    self.in_channels, out_channels * block.expansion,
                    kernel_size=1, stride=stride, bias=False
                ),
                nn.BatchNorm2d(out_channels * block.expansion),
            )

        layers = []
        
        # First block may downsample and change channels
        layers.append(block(self.in_channels, out_channels, stride, downsample))
        self.in_channels = out_channels * block.expansion

        # Remaining blocks maintain dimensions
        for _ in range(1, num_blocks):
            layers.append(block(self.in_channels, out_channels))

        return nn.Sequential(*layers)
    
    def _initialize_weights(self):
        """
        Initialize network weights using He initialization for better convergence.
        """
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                # He initialization for convolutional layers
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm2d):
                # Initialize batch norm parameters
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                # Initialize linear layer
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.constant_(m.bias, 0)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the ResNet.
        
        Args:
            x (torch.Tensor): Input tensor of shape (N, C, H, W)
                             For ImageNet: (N, 3, 224, 224)
                             For CIFAR: (N, 3, 32, 32)
            
        Returns:
            torch.Tensor: Output logits of shape (N, num_classes)
        """
        # Initial convolution and pooling
        # ImageNet: (N, 3, 224, 224) -> (N, 64, 112, 112) -> (N, 64, 56, 56)
        # CIFAR: (N, 3, 32, 32) -> (N, 16, 32, 32)
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        if self.maxpool is not None:
            x = self.maxpool(x)

        # Progressive feature extraction through residual layers
        # Each layer typically halves spatial dimensions and doubles channels
        x = self.layer1(x)  # ImageNet: 56x56, CIFAR: 32x32
        x = self.layer2(x)  # ImageNet: 28x28, CIFAR: 16x16  
        x = self.layer3(x)  # ImageNet: 14x14, CIFAR: 8x8
        
        if self.layer4 is not None:
            x = self.layer4(x)  # ImageNet: 7x7

        # Global average pooling and classification
        x = self.avgpool(x)     # Shape: (N, channels, 1, 1)
        x = torch.flatten(x, 1) # Shape: (N, channels)
        x = self.fc(x)          # Shape: (N, num_classes)
        
        return x
    
    def get_feature_maps(self, x: torch.Tensor) -> Tuple[torch.Tensor, ...]:
        """
        Extract intermediate feature maps for analysis or transfer learning.
        
        Args:
            x (torch.Tensor): Input tensor
            
        Returns:
            Tuple[torch.Tensor, ...]: Feature maps from each layer
        """
        features = []
        
        # Initial features
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        if self.maxpool is not None:
            x = self.maxpool(x)
        features.append(x)
        
        # Layer features
        x = self.layer1(x)
        features.append(x)
        
        x = self.layer2(x)
        features.append(x)
        
        x = self.layer3(x)
        features.append(x)
        
        if self.layer4 is not None:
            x = self.layer4(x)
            features.append(x)
        
        return tuple(features)


# -----------------------
# Model Factory Functions
# -----------------------

def resnet_18(input_channels: int, output_classes: int, cifar: bool = False) -> ResNet:
    """
    Construct a ResNet-18 model.
    
    ResNet-18 uses BasicBlock with the layer configuration [2, 2, 2, 2],
    resulting in a total of 18 layers (2*2 + 2*2 + 2*2 + 2*2 + 2 = 18).
    This is the lightest ResNet variant, suitable for smaller datasets
    or when computational resources are limited.
    
    Model Statistics:
    - Parameters: ~11.7M (ImageNet), ~0.27M (CIFAR)
    - FLOPs: ~1.8B (ImageNet), ~0.06B (CIFAR)
    - Memory: ~46MB (ImageNet), ~1MB (CIFAR)
    
    Args:
        input_channels (int): Number of input channels (e.g., 3 for RGB images)
        output_classes (int): Number of output classes for classification
        cifar (bool, optional): Use CIFAR-optimized architecture. Defaults to False.
        
    Returns:
        ResNet: Configured ResNet-18 model
        
    Raises:
        ValueError: If input_channels or output_classes is None or invalid
        
    Example:
        >>> model = ResNet18(input_channels=3, output_classes=1000)  # ImageNet
        >>> model = ResNet18(input_channels=3, output_classes=10, cifar=True)  # CIFAR-10
    """
    if input_channels is None or input_channels <= 0:
        raise ValueError("input_channels must be a positive integer")
    if output_classes is None or output_classes <= 0:
        raise ValueError("output_classes must be a positive integer")

    return ResNet(
        input_channels=input_channels,
        block=BasicBlock,
        layers=[2, 2, 2, 2],
        output_classes=output_classes,
        cifar=cifar
    )


def resnet_34(input_channels: int, output_classes: int, cifar: bool = False) -> ResNet:
    """
    Construct a ResNet-34 model.
    
    ResNet-34 uses BasicBlock with the layer configuration [3, 4, 6, 3],
    resulting in a total of 34 layers. This model provides a good balance
    between performance and computational efficiency.
    
    Model Statistics:
    - Parameters: ~21.8M (ImageNet), ~0.46M (CIFAR)
    - FLOPs: ~3.7B (ImageNet), ~0.12B (CIFAR)
    - Memory: ~87MB (ImageNet), ~2MB (CIFAR)
    
    Args:
        input_channels (int): Number of input channels (e.g., 3 for RGB images)
        output_classes (int): Number of output classes for classification
        cifar (bool, optional): Use CIFAR-optimized architecture. Defaults to False.
        
    Returns:
        ResNet: Configured ResNet-34 model
        
    Raises:
        ValueError: If input_channels or output_classes is None or invalid
    """
    if input_channels is None or input_channels <= 0:
        raise ValueError("input_channels must be a positive integer")
    if output_classes is None or output_classes <= 0:
        raise ValueError("output_classes must be a positive integer")

    return ResNet(
        input_channels=input_channels,
        block=BasicBlock,
        layers=[3, 4, 6, 3],
        output_classes=output_classes,
        cifar=cifar
    )


def resnet_32(input_channels: int, output_classes: int, cifar: bool = True) -> ResNet:
    """
    Construct a ResNet-32 model optimized for CIFAR datasets.
    
    ResNet-32 is a CIFAR-specific variant with layer configuration [5, 5, 5].
    This architecture is specifically designed for 32x32 input images
    and provides good performance on smaller datasets.
    
    Model Statistics (CIFAR):
    - Parameters: ~0.46M
    - FLOPs: ~0.09B
    - Memory: ~2MB
    
    Args:
        input_channels (int): Number of input channels (typically 3 for CIFAR)
        output_classes (int): Number of output classes (10 for CIFAR-10, 100 for CIFAR-100)
        cifar (bool, optional): Use CIFAR-optimized architecture. Defaults to True.
        
    Returns:
        ResNet: Configured ResNet-32 model
        
    Raises:
        ValueError: If input_channels or output_classes is None or invalid
        
    Note:
        This model is primarily designed for CIFAR datasets (32x32 images).
        For ImageNet-style inputs, consider ResNet-18 or ResNet-34.
    """
    if input_channels is None or input_channels <= 0:
        raise ValueError("input_channels must be a positive integer")
    if output_classes is None or output_classes <= 0:
        raise ValueError("output_classes must be a positive integer")

    return ResNet(
        input_channels=input_channels,
        block=BasicBlock,
        layers=[5, 5, 5],
        output_classes=output_classes,
        cifar=cifar
    )


def resnet_50(input_channels: int, output_classes: int, cifar: bool = False) -> ResNet:
    """
    Construct a ResNet-50 model.
    
    ResNet-50 uses Bottleneck blocks with layer configuration [3, 4, 6, 3],
    resulting in a total of 50 layers. This is the most popular ResNet variant,
    offering excellent performance on ImageNet and other large-scale datasets.
    
    Model Statistics:
    - Parameters: ~25.6M (ImageNet), ~0.58M (CIFAR)
    - FLOPs: ~4.1B (ImageNet), ~0.13B (CIFAR)
    - Memory: ~102MB (ImageNet), ~2.3MB (CIFAR)
    
    Args:
        input_channels (int): Number of input channels (e.g., 3 for RGB images)
        output_classes (int): Number of output classes for classification
        cifar (bool, optional): Use CIFAR-optimized architecture. Defaults to False.
        
    Returns:
        ResNet: Configured ResNet-50 model
        
    Raises:
        ValueError: If input_channels or output_classes is None or invalid
        
    Example:
        >>> model = ResNet50(input_channels=3, output_classes=1000)  # ImageNet
        >>> model = ResNet50(input_channels=3, output_classes=100, cifar=True)  # CIFAR-100
    """
    if input_channels is None or input_channels <= 0:
        raise ValueError("input_channels must be a positive integer")
    if output_classes is None or output_classes <= 0:
        raise ValueError("output_classes must be a positive integer")

    return ResNet(
        input_channels=input_channels,
        block=Bottleneck,
        layers=[3, 4, 6, 3],
        output_classes=output_classes,
        cifar=cifar
    )


def resnet_101(input_channels: int, output_classes: int, cifar: bool = False) -> ResNet:
    """
    Construct a ResNet-101 model.
    
    ResNet-101 uses Bottleneck blocks with layer configuration [3, 4, 23, 3],
    resulting in a total of 101 layers. This deeper variant provides higher
    accuracy at the cost of increased computational requirements.
    
    Model Statistics:
    - Parameters: ~44.5M (ImageNet), ~1.0M (CIFAR)
    - FLOPs: ~7.8B (ImageNet), ~0.25B (CIFAR)
    - Memory: ~178MB (ImageNet), ~4MB (CIFAR)
    
    Args:
        input_channels (int): Number of input channels (e.g., 3 for RGB images)
        output_classes (int): Number of output classes for classification
        cifar (bool, optional): Use CIFAR-optimized architecture. Defaults to False.
        
    Returns:
        ResNet: Configured ResNet-101 model
        
    Raises:
        ValueError: If input_channels or output_classes is None or invalid
        
    Note:
        This model requires significant computational resources and memory.
        Consider ResNet-50 for most applications unless the extra accuracy is needed.
    """
    if input_channels is None or input_channels <= 0:
        raise ValueError("input_channels must be a positive integer")
    if output_classes is None or output_classes <= 0:
        raise ValueError("output_classes must be a positive integer")

    return ResNet(
        input_channels=input_channels,
        block=Bottleneck,
        layers=[3, 4, 23, 3],
        output_classes=output_classes,
        cifar=cifar
    )


def resnet_152(input_channels: int, output_classes: int, cifar: bool = False) -> ResNet:
    """
    Construct a ResNet-152 model.
    
    ResNet-152 uses Bottleneck blocks with layer configuration [3, 8, 36, 3],
    resulting in a total of 152 layers. This is the deepest standard ResNet
    variant, providing maximum accuracy at very high computational cost.
    
    Model Statistics:
    - Parameters: ~60.2M (ImageNet), ~1.37M (CIFAR)
    - FLOPs: ~11.6B (ImageNet), ~0.37B (CIFAR)
    - Memory: ~241MB (ImageNet), ~5.5MB (CIFAR)
    
    Args:
        input_channels (int): Number of input channels (e.g., 3 for RGB images)
        output_classes (int): Number of output classes for classification
        cifar (bool, optional): Use CIFAR-optimized architecture. Defaults to False.
        
    Returns:
        ResNet: Configured ResNet-152 model
        
    Raises:
        ValueError: If input_channels or output_classes is None or invalid
        
    Warning:
        This model requires substantial computational resources and memory.
        Training may be slow and require large amounts of GPU memory.
        Consider smaller variants unless maximum accuracy is critical.
    """
    if input_channels is None or input_channels <= 0:
        raise ValueError("input_channels must be a positive integer")
    if output_classes is None or output_classes <= 0:
        raise ValueError("output_classes must be a positive integer")

    return ResNet(
        input_channels=input_channels,
        block=Bottleneck,
        layers=[3, 8, 36, 3],
        output_classes=output_classes,
        cifar=cifar
    )


# -----------------------
# Utility Functions
# -----------------------

def get_model_summary(model: ResNet, input_shape: Tuple[int, int, int] = (3, 224, 224)) -> str:
    """
    Generate a detailed summary of the ResNet model architecture.
    
    Args:
        model (ResNet): The ResNet model to summarize
        input_shape (Tuple[int, int, int]): Input tensor shape (C, H, W)
        
    Returns:
        str: Formatted model summary string
    """
    def count_parameters(model):
        return sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    def estimate_memory(model, input_shape, batch_size=1):
        # Rough estimation of memory usage in MB
        params = count_parameters(model)
        param_memory = params * 4 / (1024 * 1024)  # 4 bytes per float32
        
        # Estimate activation memory (very rough)
        c, h, w = input_shape
        activation_memory = batch_size * c * h * w * 4 / (1024 * 1024)
        
        return param_memory + activation_memory
    
    total_params = count_parameters(model)
    memory_mb = estimate_memory(model, input_shape)
    
    summary = f"""
ResNet Model Summary
{'=' * 50}
Architecture: {model.__class__.__name__}
Input Shape: {input_shape}
CIFAR Mode: {model.cifar}

Layer Information:
- Initial Conv: {model.conv1.out_channels} channels
- Layer 1: {len(model.layer1)} blocks, {model.layer1[0].conv1.out_channels if hasattr(model.layer1[0], 'conv1') else model.layer1[0].conv2.out_channels} channels
- Layer 2: {len(model.layer2)} blocks, {model.layer2[0].conv1.out_channels if hasattr(model.layer2[0], 'conv1') else model.layer2[0].conv2.out_channels} channels  
- Layer 3: {len(model.layer3)} blocks, {model.layer3[0].conv1.out_channels if hasattr(model.layer3[0], 'conv1') else model.layer3[0].conv2.out_channels} channels
{"- Layer 4: " + str(len(model.layer4)) + " blocks, " + str(model.layer4[0].conv1.out_channels if hasattr(model.layer4[0], 'conv1') else model.layer4[0].conv2.out_channels) + " channels" if model.layer4 else "- Layer 4: None (CIFAR mode)"}
- Final FC: {model.fc.out_features} classes

Model Statistics:
- Total Parameters: {total_params:,}
- Estimated Memory: {memory_mb:.1f} MB
- Block Type: {'BasicBlock' if hasattr(model.layer1[0], 'expansion') and model.layer1[0].expansion == 1 else 'Bottleneck'}
{'=' * 50}
    """
    
    return summary.strip()


# -----------------------
# Model Comparison Helper
# -----------------------

def compare_resnet_variants() -> str:
    """
    Generate a comparison table of different ResNet variants.
    
    Returns:
        str: Formatted comparison table
    """
    variants = [
        ("ResNet-18", "BasicBlock", "[2,2,2,2]", "~11.7M", "~1.8B", "Light"),
        ("ResNet-34", "BasicBlock", "[3,4,6,3]", "~21.8M", "~3.7B", "Balanced"),
        ("ResNet-32*", "BasicBlock", "[5,5,5]", "~0.46M", "~0.09B", "CIFAR"),
        ("ResNet-50", "Bottleneck", "[3,4,6,3]", "~25.6M", "~4.1B", "Popular"),
        ("ResNet-101", "Bottleneck", "[3,4,23,3]", "~44.5M", "~7.8B", "Deep"),
        ("ResNet-152", "Bottleneck", "[3,8,36,3]", "~60.2M", "~11.6B", "Deepest"),
    ]
    
    comparison = """
ResNet Variants Comparison (ImageNet scale)
{'=' * 80}
{'Model':<12} {'Block':<12} {'Layers':<12} {'Params':<10} {'FLOPs':<10} {'Usage':<10}
{'-' * 80}
"""
    
    for variant in variants:
        comparison += f"{variant[0]:<12} {variant[1]:<12} {variant[2]:<12} {variant[3]:<10} {variant[4]:<10} {variant[5]:<10}\n"
    
    comparison += f"""
{'-' * 80}
* ResNet-32 is optimized for CIFAR datasets (32x32 images)
FLOPs = Floating Point Operations (forward pass only)
Params = Trainable parameters
{'=' * 80}
"""
    
    return comparison.strip()