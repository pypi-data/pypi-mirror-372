# VAE Toolkit

[![PyPI version](https://badge.fury.io/py/vae-toolkit.svg)](https://badge.fury.io/py/vae-toolkit)
[![Python Support](https://img.shields.io/pypi/pyversions/vae-toolkit.svg)](https://pypi.org/project/vae-toolkit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive toolkit for working with Stable Diffusion VAE models, providing image preprocessing utilities and model loading capabilities.

## Features

- 🖼️ **Image Processing**: Efficient image preprocessing and tensor conversions optimized for VAE models
- 🚀 **Model Loading**: Easy loading of Stable Diffusion VAE models with automatic device selection
- ⚡ **Performance**: Built-in caching and optimized transforms for faster processing
- 🔧 **Flexible API**: Both high-level and low-level APIs for different use cases
- 🛡️ **Type Safety**: Full type hints for better IDE support and code reliability
- 🔐 **Secure**: No hardcoded tokens - authentication via environment variables only

## Installation

```bash
pip install vae-toolkit
```

### Optional Dependencies

For development:
```bash
pip install vae-toolkit[dev]
```

For testing:
```bash
pip install vae-toolkit[test]
```

For all extras:
```bash
pip install vae-toolkit[all]
```

## Quick Start

### Basic Image Processing

```python
from vae_toolkit import load_and_preprocess_image, tensor_to_pil

# Load and preprocess an image for VAE encoding
tensor, original_pil = load_and_preprocess_image("path/to/image.png", target_size=512)
print(f"Tensor shape: {tensor.shape}")  # [1, 3, 512, 512]
print(f"Value range: [{tensor.min():.2f}, {tensor.max():.2f}]")  # [-1.00, 1.00]

# Convert tensor back to PIL image
reconstructed = tensor_to_pil(tensor)
reconstructed.save("reconstructed.png")
```

### Loading VAE Models

```python
from vae_toolkit import VAELoader

# Initialize the loader
loader = VAELoader()

# Load Stable Diffusion v1.5 VAE
vae, device = loader.load_sd_vae(
    model_name="sd15",  # or "sd14" for v1.4
    device="auto"        # automatically selects GPU/CPU
)

print(f"Model loaded on: {device}")
```

### Complete VAE Workflow

```python
import torch
from vae_toolkit import load_and_preprocess_image, VAELoader, tensor_to_pil

# Setup
loader = VAELoader()
vae, device = loader.load_sd_vae("sd14")

# Load and preprocess image
image_tensor, original = load_and_preprocess_image("input.jpg", target_size=512)
image_tensor = image_tensor.to(device)

# Encode to latent space
with torch.no_grad():
    latent = vae.encode(image_tensor).latent_dist.sample()
    print(f"Latent shape: {latent.shape}")  # [1, 4, 64, 64]

# Decode back to image
with torch.no_grad():
    decoded = vae.decode(latent).sample
    
# Save result
output_image = tensor_to_pil(decoded)
output_image.save("output.png")
```

### Using the ImageProcessor Class

```python
from vae_toolkit import ImageProcessor

# Create a processor with custom settings
processor = ImageProcessor(
    target_size=768,
    normalize_mean=(0.5, 0.5, 0.5),
    normalize_std=(0.5, 0.5, 0.5)
)

# Process multiple images with the same settings
for image_path in image_paths:
    tensor, original = processor.load_and_preprocess(image_path)
    # Process tensor...
```

## Authentication

To use models from Hugging Face Hub, set your token as an environment variable:

```bash
export HF_TOKEN="your_huggingface_token"
# or
export HUGGING_FACE_HUB_TOKEN="your_huggingface_token"
```

## API Reference

### Image Processing Functions

#### `load_and_preprocess_image(image_path, target_size=512)`
Loads and preprocesses an image for VAE encoding.

**Parameters:**
- `image_path` (str | Path): Path to the input image
- `target_size` (int): Target size for the square output image

**Returns:**
- `tuple[torch.Tensor, PIL.Image]`: Preprocessed tensor and original PIL image

#### `tensor_to_pil(tensor)`
Converts a tensor to PIL Image format.

**Parameters:**
- `tensor` (torch.Tensor): Input tensor with shape [C, H, W] or [1, C, H, W]

**Returns:**
- `PIL.Image`: RGB PIL image

#### `pil_to_tensor(pil_image, target_size=None, normalize=True)`
Converts a PIL image to tensor format.

**Parameters:**
- `pil_image` (PIL.Image): Input PIL image
- `target_size` (int | None): Optional target size for resizing
- `normalize` (bool): Whether to normalize to [-1, 1] range

**Returns:**
- `torch.Tensor`: Tensor with shape [3, H, W]

### VAE Loader

#### `VAELoader`
Main class for loading and managing Stable Diffusion VAE models.

**Methods:**
- `load_sd_vae(model_name="sd14", device="auto", token=None, use_cache=True)`
  - Loads a Stable Diffusion VAE model
  - Returns: `tuple[AutoencoderKL, torch.device]`
  
- `get_optimal_device(preferred_device="auto")`
  - Determines the best available device
  - Returns: `torch.device`
  
- `clear_cache()`
  - Clears the model cache to free memory

### Model Configuration

#### `get_model_config(model_name)`
Gets configuration for a specific model.

#### `list_available_models()`
Lists all available model identifiers.

#### `add_model_config(model_name, config)`
Adds a custom model configuration.

## Available Models

- `sd14`: Stable Diffusion v1.4 VAE
- `sd15`: Stable Diffusion v1.5 VAE

## Error Handling

The toolkit includes custom exceptions for better error handling:

```python
from vae_toolkit import ImageProcessingError

try:
    tensor, _ = load_and_preprocess_image("invalid_path.jpg")
except ImageProcessingError as e:
    print(f"Failed to process image: {e}")
```

## Performance Tips

1. **Use caching**: The VAELoader caches models by default to avoid reloading
2. **Batch processing**: Process multiple images together when possible
3. **Device selection**: Use "auto" for automatic GPU/CPU selection
4. **Memory management**: Call `loader.clear_cache()` when switching between models

## Requirements

- Python >= 3.8
- PyTorch >= 2.0.0
- torchvision >= 0.15.0
- Pillow >= 9.0.0
- numpy >= 1.20.0
- diffusers >= 0.20.0

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Testing

Run tests with pytest:

```bash
# Install test dependencies
pip install vae-toolkit[test]

# Run tests
pytest

# Run with coverage
pytest --cov=vae_toolkit
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this toolkit in your research, please cite:

```bibtex
@software{vae-toolkit,
  author = {Yus314},
  title = {VAE Toolkit: Stable Diffusion VAE utilities},
  year = {2024},
  url = {https://github.com/mdipcit/vae-toolkit}
}
```

## Acknowledgments

- Built on top of the amazing [diffusers](https://github.com/huggingface/diffusers) library
- Inspired by the Stable Diffusion community

## Support

For issues and questions, please use the [GitHub Issues](https://github.com/mdipcit/vae-toolkit/issues) page.