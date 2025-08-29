"""
VAE model loader for Stable Diffusion models.
"""

import torch
from typing import Optional, Tuple, Dict, Any
import logging
from diffusers import AutoencoderKL

from .model_config import get_model_config, get_all_model_configs, get_default_token


logger = logging.getLogger(__name__)


class VAELoader:
    """
    Stable Diffusion VAE model loader with device management and caching.
    """
    
    def __init__(self):
        self._model_cache: Dict[str, AutoencoderKL] = {}
    
    @staticmethod
    def get_optimal_device(preferred_device: str = "auto") -> torch.device:
        """
        Get the optimal device for model loading.
        
        Args:
            preferred_device: Preferred device ("auto", "cuda", "cpu", "mps")
            
        Returns:
            torch.device: The selected device
        """
        if preferred_device == "auto":
            if torch.cuda.is_available():
                device = torch.device("cuda")
            elif torch.backends.mps.is_available():
                device = torch.device("mps")
            else:
                device = torch.device("cpu")
        else:
            device = torch.device(preferred_device)
            
        logger.info(f"Selected device: {device}")
        return device
    
    def load_sd_vae(
        self,
        model_name: str = "sd14",
        device: str = "auto",
        token: Optional[str] = None,
        use_cache: bool = True
    ) -> Tuple[AutoencoderKL, torch.device]:
        """
        Load Stable Diffusion VAE model.
        
        Args:
            model_name: Model identifier (sd14, sd15, etc.)
            device: Target device for the model
            token: Hugging Face token for private repos
            use_cache: Whether to use model caching
            
        Returns:
            Tuple of (model, device)
        """
        # Use default token if not provided
        if token is None:
            token = get_default_token()
        
        # Get device
        target_device = self.get_optimal_device(device)
        
        # Check cache
        cache_key = f"{model_name}_{target_device}"
        if use_cache and cache_key in self._model_cache:
            logger.info(f"Using cached VAE model: {model_name}")
            return self._model_cache[cache_key], target_device
        
        # Get model configuration
        try:
            config = get_model_config(model_name)
        except ValueError as e:
            logger.error(str(e))
            raise
        
        try:
            logger.info(f"Loading VAE model: {model_name}")
            vae = AutoencoderKL.from_pretrained(
                config["repo_id"],
                subfolder=config["subfolder"],
                token=token,
            )
            
            # Move to device
            vae = vae.to(target_device)
            logger.info(f"VAE model loaded successfully on {target_device}")
            
            # Cache model
            if use_cache:
                self._model_cache[cache_key] = vae
                
            return vae, target_device
            
        except Exception as e:
            logger.error(f"Failed to load VAE model {model_name}: {e}")
            raise
    
    @classmethod
    def load_sd_vae_simple(
        cls,
        model_name: str = "sd14",
        device: str = "auto",
        token: Optional[str] = None
    ) -> Tuple[AutoencoderKL, torch.device]:
        """
        Simple class method for one-time VAE loading without caching.
        
        Args:
            model_name: Model identifier
            device: Target device
            token: Hugging Face token
            
        Returns:
            Tuple of (model, device)
        """
        loader = cls()
        return loader.load_sd_vae(model_name, device, token, use_cache=False)
    
    def clear_cache(self) -> None:
        """Clear model cache."""
        self._model_cache.clear()
        logger.info("Model cache cleared")
    
