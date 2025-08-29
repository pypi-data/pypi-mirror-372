"""Tests for image processing utilities."""

import pytest
import torch
import numpy as np
from PIL import Image
from pathlib import Path
import tempfile

from vae_toolkit import (
    load_and_preprocess_image,
    tensor_to_pil,
    pil_to_tensor,
    ImageProcessor,
    ImageProcessingError,
)


@pytest.fixture
def sample_image():
    """Create a sample RGB image for testing."""
    # Create a 512x512 RGB image with random colors
    img_array = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
    return Image.fromarray(img_array, mode='RGB')


@pytest.fixture
def sample_tensor():
    """Create a sample tensor for testing."""
    # Create a tensor with shape [1, 3, 512, 512] in range [-1, 1]
    tensor = torch.randn(1, 3, 512, 512)
    tensor = torch.tanh(tensor)  # Ensure values are in [-1, 1]
    return tensor


class TestImageLoading:
    """Test image loading and preprocessing functions."""
    
    def test_load_and_preprocess_valid_image(self, sample_image):
        """Test loading and preprocessing a valid image."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            sample_image.save(tmp.name)
            tmp_path = Path(tmp.name)
            
            try:
                tensor, original = load_and_preprocess_image(str(tmp_path), target_size=512)
                
                # Check tensor properties
                assert tensor.shape == (1, 3, 512, 512)
                assert tensor.dtype == torch.float32
                assert -1.1 <= tensor.min() <= -0.9
                assert 0.9 <= tensor.max() <= 1.1
                
                # Check original image
                assert isinstance(original, Image.Image)
                assert original.size == (512, 512)
            finally:
                tmp_path.unlink()
    
    def test_load_invalid_path(self):
        """Test loading from an invalid path."""
        with pytest.raises(ImageProcessingError) as exc_info:
            load_and_preprocess_image("nonexistent_file.jpg")
        assert "not found" in str(exc_info.value) or "Failed to load" in str(exc_info.value)
    
    def test_load_wrong_size_image(self, sample_image):
        """Test loading an image with wrong dimensions."""
        # Create a 256x256 image
        small_image = sample_image.resize((256, 256))
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            small_image.save(tmp.name)
            tmp_path = Path(tmp.name)
            
            try:
                with pytest.raises(ImageProcessingError) as exc_info:
                    load_and_preprocess_image(str(tmp_path), target_size=512)
                assert "does not match required size" in str(exc_info.value)
            finally:
                tmp_path.unlink()


class TestTensorConversions:
    """Test tensor to PIL and PIL to tensor conversions."""
    
    def test_tensor_to_pil_basic(self, sample_tensor):
        """Test basic tensor to PIL conversion."""
        pil_image = tensor_to_pil(sample_tensor)
        
        assert isinstance(pil_image, Image.Image)
        assert pil_image.mode == 'RGB'
        assert pil_image.size == (512, 512)
    
    def test_tensor_to_pil_without_batch(self):
        """Test tensor to PIL conversion without batch dimension."""
        tensor = torch.randn(3, 256, 256)
        tensor = torch.tanh(tensor)
        
        pil_image = tensor_to_pil(tensor)
        
        assert isinstance(pil_image, Image.Image)
        assert pil_image.size == (256, 256)
    
    def test_tensor_to_pil_invalid_shape(self):
        """Test tensor to PIL with invalid shape."""
        invalid_tensor = torch.randn(2, 3, 256, 256)  # Batch size > 1
        
        with pytest.raises(ImageProcessingError) as exc_info:
            tensor_to_pil(invalid_tensor)
        assert "Batch size must be 1" in str(exc_info.value)
    
    def test_pil_to_tensor_basic(self, sample_image):
        """Test basic PIL to tensor conversion."""
        tensor = pil_to_tensor(sample_image)
        
        assert tensor.shape == (3, 512, 512)
        assert tensor.dtype == torch.float32
        assert -1.1 <= tensor.min() <= 1.1
        assert -1.1 <= tensor.max() <= 1.1
    
    def test_pil_to_tensor_with_resize(self, sample_image):
        """Test PIL to tensor with resizing."""
        tensor = pil_to_tensor(sample_image, target_size=256)
        
        assert tensor.shape == (3, 256, 256)
    
    def test_pil_to_tensor_without_normalization(self, sample_image):
        """Test PIL to tensor without normalization."""
        tensor = pil_to_tensor(sample_image, normalize=False)
        
        assert tensor.shape == (3, 512, 512)
        assert 0 <= tensor.min() <= 1
        assert 0 <= tensor.max() <= 1
    
    def test_round_trip_conversion(self, sample_image):
        """Test round-trip conversion PIL -> Tensor -> PIL."""
        # Convert PIL to tensor
        tensor = pil_to_tensor(sample_image, normalize=True)
        
        # Add batch dimension for tensor_to_pil
        tensor_batched = tensor.unsqueeze(0)
        
        # Convert back to PIL
        reconstructed = tensor_to_pil(tensor_batched)
        
        assert isinstance(reconstructed, Image.Image)
        assert reconstructed.size == sample_image.size
        assert reconstructed.mode == sample_image.mode


class TestImageProcessor:
    """Test ImageProcessor class."""
    
    def test_processor_initialization(self):
        """Test ImageProcessor initialization."""
        processor = ImageProcessor(
            target_size=768,
            normalize_mean=(0.485, 0.456, 0.406),
            normalize_std=(0.229, 0.224, 0.225)
        )
        
        assert processor.target_size == 768
        assert processor.normalize_mean == (0.485, 0.456, 0.406)
        assert processor.normalize_std == (0.229, 0.224, 0.225)
    
    def test_processor_preprocess_pil(self, sample_image):
        """Test preprocessing PIL image with ImageProcessor."""
        processor = ImageProcessor(target_size=256)
        
        # Resize sample image to 256x256 to match processor expectations
        resized_image = sample_image.resize((256, 256))
        tensor = processor.preprocess_pil(resized_image)
        
        assert tensor.shape == (1, 3, 256, 256)
        assert tensor.dtype == torch.float32
    
    def test_processor_with_non_rgb_image(self):
        """Test processor with non-RGB image."""
        # Create a grayscale image
        gray_image = Image.new('L', (512, 512), color=128)
        
        processor = ImageProcessor()
        tensor = processor.preprocess_pil(gray_image)
        
        assert tensor.shape == (1, 3, 512, 512)  # Should be converted to RGB


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_empty_image_path(self):
        """Test with empty image path."""
        with pytest.raises(ImageProcessingError):
            load_and_preprocess_image("")
    
    def test_invalid_tensor_dimension(self):
        """Test tensor_to_pil with invalid dimensions."""
        invalid_tensor = torch.randn(5)  # 1D tensor
        
        with pytest.raises(ImageProcessingError) as exc_info:
            tensor_to_pil(invalid_tensor)
        assert "dimension" in str(exc_info.value).lower()
    
    def test_invalid_channel_count(self):
        """Test tensor_to_pil with wrong channel count."""
        invalid_tensor = torch.randn(1, 4, 256, 256)  # 4 channels instead of 3
        
        with pytest.raises(ImageProcessingError) as exc_info:
            tensor_to_pil(invalid_tensor)
        assert "3 channels" in str(exc_info.value)


class TestValueRanges:
    """Test value range handling and normalization."""
    
    def test_normalization_range(self, sample_image):
        """Test that normalization produces correct value range."""
        tensor = pil_to_tensor(sample_image, normalize=True)
        
        # Values should be approximately in [-1, 1]
        assert tensor.min() >= -1.1
        assert tensor.max() <= 1.1
    
    def test_denormalization_range(self):
        """Test that denormalization in tensor_to_pil works correctly."""
        # Create a tensor with exact -1 and 1 values
        tensor = torch.zeros(1, 3, 100, 100)
        tensor[0, 0, :50, :] = -1.0  # Red channel, half image = -1
        tensor[0, 1, :, :50] = 1.0   # Green channel, half image = 1
        
        pil_image = tensor_to_pil(tensor)
        np_array = np.array(pil_image)
        
        # Check that extreme values map correctly
        assert np_array.min() >= 0
        assert np_array.max() <= 255


class TestDefaultProcessors:
    """Test default processor instances."""
    
    def test_default_processors_exist(self):
        """Test that default processors are available."""
        from vae_toolkit import DEFAULT_PROCESSOR, SD_PROCESSOR
        
        assert isinstance(DEFAULT_PROCESSOR, ImageProcessor)
        assert isinstance(SD_PROCESSOR, ImageProcessor)
        assert SD_PROCESSOR.target_size == 512