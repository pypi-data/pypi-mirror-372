"""
VAE Toolkit - Stable Diffusion VAE utilities for image processing and model loading.

This toolkit provides comprehensive utilities for working with Stable Diffusion VAE models,
including image preprocessing, tensor conversions, and model loading capabilities.
"""

__version__ = "0.1.0"
__author__ = "Yus314"
__email__ = "shizhaoyoujie@gmail.com"

# Image processing utilities
from .image_utils import (
    load_and_preprocess_image,
    tensor_to_pil,
    pil_to_tensor,
    ImageProcessor,
    ImageProcessingError,
    DEFAULT_PROCESSOR,
    SD_PROCESSOR
)

# VAE loader utilities
from .vae_loader import VAELoader

# Model configurations
from .model_config import (
    get_model_config,
    get_all_model_configs,
    list_available_models,
    add_model_config,
    get_default_token
)

# Define public API
__all__ = [
    # Package metadata
    "__version__",
    "__author__",
    "__email__",
    
    # Image processing
    "load_and_preprocess_image",
    "tensor_to_pil",
    "pil_to_tensor",
    "ImageProcessor",
    "ImageProcessingError",
    "DEFAULT_PROCESSOR",
    "SD_PROCESSOR",
    
    # VAE loader
    "VAELoader",
    
    # Model configuration
    "get_model_config",
    "get_all_model_configs",
    "list_available_models",
    "add_model_config",
    "get_default_token",
]