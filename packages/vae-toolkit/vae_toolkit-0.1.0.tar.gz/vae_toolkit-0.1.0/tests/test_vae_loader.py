"""Tests for VAE loader functionality."""

import pytest
import torch
from unittest.mock import Mock, patch, MagicMock
import logging

from vae_toolkit import VAELoader


class TestVAELoader:
    """Test VAELoader class."""
    
    def test_loader_initialization(self):
        """Test VAELoader initialization."""
        loader = VAELoader()
        assert hasattr(loader, '_model_cache')
        assert loader._model_cache == {}
    
    def test_get_optimal_device_cuda_available(self):
        """Test device selection when CUDA is available."""
        with patch('torch.cuda.is_available', return_value=True):
            device = VAELoader.get_optimal_device("auto")
            assert device == torch.device("cuda")
    
    def test_get_optimal_device_mps_available(self):
        """Test device selection when MPS is available."""
        with patch('torch.cuda.is_available', return_value=False):
            with patch('torch.backends.mps.is_available', return_value=True):
                device = VAELoader.get_optimal_device("auto")
                assert device == torch.device("mps")
    
    def test_get_optimal_device_cpu_fallback(self):
        """Test device selection falls back to CPU."""
        with patch('torch.cuda.is_available', return_value=False):
            with patch('torch.backends.mps.is_available', return_value=False):
                device = VAELoader.get_optimal_device("auto")
                assert device == torch.device("cpu")
    
    def test_get_optimal_device_manual_selection(self):
        """Test manual device selection."""
        device = VAELoader.get_optimal_device("cpu")
        assert device == torch.device("cpu")
    
    @patch('vae_toolkit.vae_loader.AutoencoderKL')
    @patch('vae_toolkit.vae_loader.get_model_config')
    @patch('vae_toolkit.vae_loader.get_default_token')
    def test_load_sd_vae_basic(self, mock_token, mock_config, mock_autoencoder):
        """Test basic VAE loading."""
        # Setup mocks
        mock_token.return_value = "test_token"
        mock_config.return_value = {
            "repo_id": "test_repo",
            "subfolder": "vae"
        }
        mock_vae = Mock()
        mock_vae.to = Mock(return_value=mock_vae)
        mock_autoencoder.from_pretrained.return_value = mock_vae
        
        # Load VAE
        loader = VAELoader()
        with patch('torch.cuda.is_available', return_value=False):
            vae, device = loader.load_sd_vae(model_name="sd14", device="cpu")
        
        # Verify calls
        mock_config.assert_called_once_with("sd14")
        mock_autoencoder.from_pretrained.assert_called_once_with(
            "test_repo",
            subfolder="vae",
            token="test_token"
        )
        mock_vae.to.assert_called_once()
        assert vae == mock_vae
        assert device == torch.device("cpu")
    
    @patch('vae_toolkit.vae_loader.AutoencoderKL')
    @patch('vae_toolkit.vae_loader.get_model_config')
    @patch('vae_toolkit.vae_loader.get_default_token')
    def test_load_sd_vae_with_cache(self, mock_token, mock_config, mock_autoencoder):
        """Test VAE loading with caching."""
        # Setup mocks
        mock_token.return_value = "test_token"
        mock_config.return_value = {
            "repo_id": "test_repo",
            "subfolder": "vae"
        }
        mock_vae = Mock()
        mock_vae.to = Mock(return_value=mock_vae)
        mock_autoencoder.from_pretrained.return_value = mock_vae
        
        loader = VAELoader()
        
        # First load
        with patch('torch.cuda.is_available', return_value=False):
            vae1, _ = loader.load_sd_vae(model_name="sd14", device="cpu", use_cache=True)
        
        # Second load (should use cache)
        with patch('torch.cuda.is_available', return_value=False):
            vae2, _ = loader.load_sd_vae(model_name="sd14", device="cpu", use_cache=True)
        
        # Should only call from_pretrained once due to caching
        assert mock_autoencoder.from_pretrained.call_count == 1
        assert vae1 == vae2
    
    @patch('vae_toolkit.vae_loader.AutoencoderKL')
    @patch('vae_toolkit.vae_loader.get_model_config')
    @patch('vae_toolkit.vae_loader.get_default_token')
    def test_load_sd_vae_without_cache(self, mock_token, mock_config, mock_autoencoder):
        """Test VAE loading without caching."""
        # Setup mocks
        mock_token.return_value = "test_token"
        mock_config.return_value = {
            "repo_id": "test_repo",
            "subfolder": "vae"
        }
        mock_vae = Mock()
        mock_vae.to = Mock(return_value=mock_vae)
        mock_autoencoder.from_pretrained.return_value = mock_vae
        
        loader = VAELoader()
        
        # Load twice without cache
        with patch('torch.cuda.is_available', return_value=False):
            loader.load_sd_vae(model_name="sd14", device="cpu", use_cache=False)
            loader.load_sd_vae(model_name="sd14", device="cpu", use_cache=False)
        
        # Should call from_pretrained twice
        assert mock_autoencoder.from_pretrained.call_count == 2
    
    @patch('vae_toolkit.vae_loader.get_model_config')
    def test_load_sd_vae_invalid_model(self, mock_config):
        """Test loading with invalid model name."""
        mock_config.side_effect = ValueError("Unknown model: invalid")
        
        loader = VAELoader()
        with pytest.raises(ValueError) as exc_info:
            loader.load_sd_vae(model_name="invalid")
        assert "Unknown model" in str(exc_info.value)
    
    @patch('vae_toolkit.vae_loader.AutoencoderKL')
    @patch('vae_toolkit.vae_loader.get_model_config')
    @patch('vae_toolkit.vae_loader.get_default_token')
    def test_load_sd_vae_loading_failure(self, mock_token, mock_config, mock_autoencoder):
        """Test handling of model loading failure."""
        mock_token.return_value = "test_token"
        mock_config.return_value = {
            "repo_id": "test_repo",
            "subfolder": "vae"
        }
        mock_autoencoder.from_pretrained.side_effect = Exception("Network error")
        
        loader = VAELoader()
        with pytest.raises(Exception) as exc_info:
            loader.load_sd_vae(model_name="sd14")
        assert "Network error" in str(exc_info.value)
    
    @patch('vae_toolkit.vae_loader.AutoencoderKL')
    @patch('vae_toolkit.vae_loader.get_model_config')
    def test_load_sd_vae_with_custom_token(self, mock_config, mock_autoencoder):
        """Test loading with custom token."""
        mock_config.return_value = {
            "repo_id": "test_repo",
            "subfolder": "vae"
        }
        mock_vae = Mock()
        mock_vae.to = Mock(return_value=mock_vae)
        mock_autoencoder.from_pretrained.return_value = mock_vae
        
        loader = VAELoader()
        custom_token = "custom_token_123"
        
        with patch('torch.cuda.is_available', return_value=False):
            loader.load_sd_vae(model_name="sd14", device="cpu", token=custom_token)
        
        # Verify custom token was used
        mock_autoencoder.from_pretrained.assert_called_once_with(
            "test_repo",
            subfolder="vae",
            token=custom_token
        )
    
    def test_clear_cache(self):
        """Test cache clearing."""
        loader = VAELoader()
        
        # Add some dummy items to cache
        loader._model_cache["test_key"] = "test_value"
        assert len(loader._model_cache) == 1
        
        # Clear cache
        loader.clear_cache()
        assert len(loader._model_cache) == 0
    
    @patch('vae_toolkit.vae_loader.AutoencoderKL')
    @patch('vae_toolkit.vae_loader.get_model_config')
    @patch('vae_toolkit.vae_loader.get_default_token')
    def test_load_sd_vae_simple_classmethod(self, mock_token, mock_config, mock_autoencoder):
        """Test the simple class method for one-time loading."""
        # Setup mocks
        mock_token.return_value = "test_token"
        mock_config.return_value = {
            "repo_id": "test_repo",
            "subfolder": "vae"
        }
        mock_vae = Mock()
        mock_vae.to = Mock(return_value=mock_vae)
        mock_autoencoder.from_pretrained.return_value = mock_vae
        
        # Use class method
        with patch('torch.cuda.is_available', return_value=False):
            vae, device = VAELoader.load_sd_vae_simple(model_name="sd14", device="cpu")
        
        assert vae == mock_vae
        assert device == torch.device("cpu")
    
    @patch('vae_toolkit.vae_loader.logger')
    @patch('torch.cuda.is_available')
    def test_logging_device_selection(self, mock_cuda, mock_logger):
        """Test that device selection is logged."""
        mock_cuda.return_value = True
        
        device = VAELoader.get_optimal_device("auto")
        
        # Check that info was logged
        mock_logger.info.assert_called()
        log_message = mock_logger.info.call_args[0][0]
        assert "cuda" in log_message.lower()
    
    @patch('vae_toolkit.vae_loader.logger')
    @patch('vae_toolkit.vae_loader.AutoencoderKL')
    @patch('vae_toolkit.vae_loader.get_model_config')
    @patch('vae_toolkit.vae_loader.get_default_token')
    def test_logging_model_loading(self, mock_token, mock_config, mock_autoencoder, mock_logger):
        """Test that model loading is logged."""
        mock_token.return_value = "test_token"
        mock_config.return_value = {
            "repo_id": "test_repo",
            "subfolder": "vae"
        }
        mock_vae = Mock()
        mock_vae.to = Mock(return_value=mock_vae)
        mock_autoencoder.from_pretrained.return_value = mock_vae
        
        loader = VAELoader()
        with patch('torch.cuda.is_available', return_value=False):
            loader.load_sd_vae(model_name="sd14", device="cpu")
        
        # Check that loading was logged
        log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any("Loading VAE model" in msg for msg in log_calls)
        assert any("successfully" in msg for msg in log_calls)