"""Tests for model configuration management."""

import pytest
import os
from unittest.mock import patch

from vae_toolkit import (
    get_model_config,
    get_all_model_configs,
    list_available_models,
    add_model_config,
    get_default_token
)


class TestModelConfig:
    """Test model configuration functions."""
    
    def test_get_model_config_sd14(self):
        """Test getting SD 1.4 configuration."""
        config = get_model_config("sd14")
        
        assert "repo_id" in config
        assert "subfolder" in config
        assert config["repo_id"] == "CompVis/stable-diffusion-v1-4"
        assert config["subfolder"] == "vae"
        assert config["latent_channels"] == 4
    
    def test_get_model_config_sd15(self):
        """Test getting SD 1.5 configuration."""
        config = get_model_config("sd15")
        
        assert "repo_id" in config
        assert config["repo_id"] == "runwayml/stable-diffusion-v1-5"
        assert config["subfolder"] == "vae"
    
    def test_get_model_config_invalid(self):
        """Test getting configuration for invalid model."""
        with pytest.raises(ValueError) as exc_info:
            get_model_config("invalid_model")
        
        assert "Unknown model" in str(exc_info.value)
        assert "invalid_model" in str(exc_info.value)
    
    def test_get_model_config_returns_copy(self):
        """Test that get_model_config returns a copy, not reference."""
        config1 = get_model_config("sd14")
        config2 = get_model_config("sd14")
        
        # Modify one config
        config1["test_key"] = "test_value"
        
        # Other config should not be affected
        assert "test_key" not in config2
    
    def test_get_all_model_configs(self):
        """Test getting all model configurations."""
        all_configs = get_all_model_configs()
        
        assert isinstance(all_configs, dict)
        assert "sd14" in all_configs
        assert "sd15" in all_configs
        assert len(all_configs) >= 2
    
    def test_get_all_model_configs_returns_copy(self):
        """Test that get_all_model_configs returns a copy."""
        configs1 = get_all_model_configs()
        configs2 = get_all_model_configs()
        
        # Modify one
        configs1["test_model"] = {"test": "value"}
        
        # Other should not be affected
        assert "test_model" not in configs2
    
    def test_list_available_models(self):
        """Test listing available models."""
        models = list_available_models()
        
        assert isinstance(models, list)
        assert "sd14" in models
        assert "sd15" in models
        assert len(models) >= 2
    
    def test_add_model_config(self):
        """Test adding a custom model configuration."""
        # Get initial count
        initial_models = list_available_models()
        initial_count = len(initial_models)
        
        # Add new model
        custom_config = {
            "repo_id": "custom/model",
            "subfolder": "vae",
            "description": "Custom model",
            "latent_channels": 4
        }
        add_model_config("custom_model", custom_config)
        
        # Verify it was added
        models_after = list_available_models()
        assert len(models_after) == initial_count + 1
        assert "custom_model" in models_after
        
        # Verify we can get the config
        retrieved = get_model_config("custom_model")
        assert retrieved["repo_id"] == "custom/model"
        
        # Clean up - remove the custom model
        from vae_toolkit.model_config import MODEL_CONFIGS
        if "custom_model" in MODEL_CONFIGS:
            del MODEL_CONFIGS["custom_model"]
    
    def test_add_model_config_overwrite(self):
        """Test overwriting an existing model configuration."""
        # Get original config
        original = get_model_config("sd14")
        original_repo = original["repo_id"]
        
        # Overwrite with custom config
        custom_config = {
            "repo_id": "custom/sd14",
            "subfolder": "custom_vae",
            "description": "Custom SD 1.4"
        }
        add_model_config("sd14", custom_config)
        
        # Verify it was overwritten
        new_config = get_model_config("sd14")
        assert new_config["repo_id"] == "custom/sd14"
        
        # Restore original
        from vae_toolkit.model_config import MODEL_CONFIGS
        MODEL_CONFIGS["sd14"]["repo_id"] = original_repo
        MODEL_CONFIGS["sd14"]["subfolder"] = "vae"


class TestTokenHandling:
    """Test token handling functions."""
    
    def test_get_default_token_no_env(self):
        """Test getting token when no environment variables are set."""
        with patch.dict(os.environ, {}, clear=True):
            token = get_default_token()
            assert token is None
    
    def test_get_default_token_hf_token(self):
        """Test getting token from HF_TOKEN environment variable."""
        test_token = "test_hf_token_123"
        with patch.dict(os.environ, {"HF_TOKEN": test_token}, clear=True):
            token = get_default_token()
            assert token == test_token
    
    def test_get_default_token_hugging_face_hub_token(self):
        """Test getting token from HUGGING_FACE_HUB_TOKEN."""
        test_token = "test_hub_token_456"
        with patch.dict(os.environ, {"HUGGING_FACE_HUB_TOKEN": test_token}, clear=True):
            token = get_default_token()
            assert token == test_token
    
    def test_get_default_token_priority(self):
        """Test that HF_TOKEN has priority over HUGGING_FACE_HUB_TOKEN."""
        hf_token = "hf_priority"
        hub_token = "hub_secondary"
        
        with patch.dict(os.environ, {
            "HF_TOKEN": hf_token,
            "HUGGING_FACE_HUB_TOKEN": hub_token
        }, clear=True):
            token = get_default_token()
            assert token == hf_token
    
    def test_no_hardcoded_token(self):
        """Test that no token is hardcoded in the module."""
        # Import the module source
        import vae_toolkit.model_config as config_module
        import inspect
        
        # Get the source code
        source = inspect.getsource(config_module)
        
        # Check for common token patterns
        suspicious_patterns = [
            "hf_",  # Hugging Face token prefix
            "api_key",
            "secret",
        ]
        
        # Check that none of these appear in string literals with actual values
        lines = source.split('\n')
        for line in lines:
            # Skip comments and docstrings
            if line.strip().startswith('#') or line.strip().startswith('"""'):
                continue
            
            # Check for hardcoded token patterns
            for pattern in suspicious_patterns:
                if pattern in line.lower():
                    # Make sure it's not just in a variable name or comment
                    if '=' in line and ('"' in line or "'" in line):
                        # Check if it's assigning a real value (not None or env var)
                        if 'os.getenv' not in line and 'None' not in line:
                            # This would be a hardcoded token
                            pytest.fail(f"Possible hardcoded token found: {line.strip()}")


class TestModelConfigIntegration:
    """Integration tests for model configuration."""
    
    def test_all_models_have_required_fields(self):
        """Test that all models have required configuration fields."""
        required_fields = ["repo_id", "subfolder"]
        
        all_configs = get_all_model_configs()
        for model_name, config in all_configs.items():
            for field in required_fields:
                assert field in config, f"Model {model_name} missing required field {field}"
    
    def test_model_configs_are_valid(self):
        """Test that all model configurations have valid values."""
        all_configs = get_all_model_configs()
        
        for model_name, config in all_configs.items():
            # Check repo_id format
            assert isinstance(config["repo_id"], str)
            assert "/" in config["repo_id"], f"Invalid repo_id format for {model_name}"
            
            # Check subfolder
            assert isinstance(config["subfolder"], str)
            assert len(config["subfolder"]) > 0
            
            # Check optional fields if present
            if "latent_channels" in config:
                assert isinstance(config["latent_channels"], int)
                assert config["latent_channels"] > 0
            
            if "input_size" in config:
                assert isinstance(config["input_size"], tuple)
                assert len(config["input_size"]) == 2