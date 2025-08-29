#!/usr/bin/env python3
"""
画像前処理・変換ユーティリティモジュール

VAEエンコード用の画像前処理とテンソル⇔PIL変換機能を提供します。
Stable Diffusion VAE用に最適化された前処理パイプラインを含みます。
"""

from typing import Tuple, Optional, Union
import torch
from PIL import Image
import numpy as np
import torchvision.transforms as transforms
from pathlib import Path


class ImageProcessingError(Exception):
    """画像処理専用例外クラス"""
    pass


def load_and_preprocess_image(image_path: Union[str, Path], target_size: int = 512) -> Tuple[torch.Tensor, Image.Image]:
    """
    画像を読み込んでVAE用に前処理
    
    Args:
        image_path: 画像ファイルのパス
        target_size: リサイズ後のサイズ（正方形）
        
    Returns:
        Tuple[torch.Tensor, Image.Image]: (前処理済みテンソル, 元PIL画像)
        - テンソル形状: [1, 3, target_size, target_size]
        - テンソル値域: [-1, 1]
    
    Raises:
        ImageProcessingError: 画像読み込みまたは処理に失敗した場合
    """
    print(f"Loading image from: {image_path}")
    
    try:
        # 画像読み込み
        pil_image = Image.open(image_path).convert('RGB')
        print(f"Original size: {pil_image.size}")
        
        # サイズ検証：target_sizeと完全一致する必要がある
        if pil_image.size != (target_size, target_size):
            raise ImageProcessingError(
                f"Image size {pil_image.size} does not match required size ({target_size}, {target_size}). "
                f"Resizing and cropping are disabled."
            )
        
    except FileNotFoundError:
        raise ImageProcessingError(f"Image file not found: {image_path}")
    except Exception as e:
        raise ImageProcessingError(f"Failed to load image {image_path}: {str(e)}")
    
    # 前処理パイプライン（リサイズ・クロップなし）
    try:
        # 正規化のみ実行（リサイズとクロップは無効）
        transform = transforms.Compose([
            transforms.ToTensor(),                       # PIL → Tensor [0,1]
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])  # [0,1] → [-1,1]
        ])
        
        image_tensor = transform(pil_image).unsqueeze(0)  # バッチ次元追加: [C,H,W] → [1,C,H,W]
        
        print(f"Preprocessed tensor shape: {image_tensor.shape}")
        print(f"Tensor range: [{image_tensor.min():.3f}, {image_tensor.max():.3f}]")
        
        return image_tensor, pil_image
        
    except Exception as e:
        raise ImageProcessingError(f"Failed to preprocess image: {str(e)}")


def tensor_to_pil(tensor: torch.Tensor) -> Image.Image:
    """
    テンソルをPIL画像に変換
    
    Args:
        tensor: 入力テンソル
                - 形状: [C, H, W] または [1, C, H, W]
                - 値域: [-1, 1] (VAEデコード出力想定)
                
    Returns:
        Image.Image: PIL画像 (RGB, uint8)
        
    Raises:
        ImageProcessingError: テンソル変換に失敗した場合
    """
    try:
        # テンソルのコピーを作成（元を変更しない）
        tensor = tensor.clone()
        
        # [-1, 1] → [0, 1] 逆正規化
        tensor = (tensor + 1) / 2
        tensor = tensor.clamp(0, 1)  # 範囲制限（数値安定性）
        
        # バッチ次元がある場合は除去
        if tensor.dim() == 4:
            if tensor.shape[0] != 1:
                raise ImageProcessingError(f"Batch size must be 1, got {tensor.shape[0]}")
            tensor = tensor.squeeze(0)
        elif tensor.dim() != 3:
            raise ImageProcessingError(f"Expected tensor dimension 3 or 4, got {tensor.dim()}")
        
        # テンソル形状確認
        if tensor.shape[0] != 3:
            raise ImageProcessingError(f"Expected 3 channels, got {tensor.shape[0]}")
        
        # CHW → HWC 変換、GPU → CPU 移動
        numpy_image = tensor.permute(1, 2, 0).cpu().numpy()
        
        # [0, 1] → [0, 255] uint8 変換
        numpy_image = (numpy_image * 255).astype(np.uint8)
        
        return Image.fromarray(numpy_image)
        
    except Exception as e:
        raise ImageProcessingError(f"Failed to convert tensor to PIL: {str(e)}")


def pil_to_tensor(pil_image: Image.Image, 
                  target_size: Optional[int] = None,
                  normalize: bool = True) -> torch.Tensor:
    """
    PIL画像をテンソルに変換（新規追加機能）
    
    Args:
        pil_image: PIL画像
        target_size: リサイズサイズ（Noneの場合はリサイズなし）
        normalize: [-1,1]正規化を行うかどうか
        
    Returns:
        torch.Tensor: 
            - 形状: [3, H, W] （バッチ次元なし）
            - 値域: [-1, 1] (normalize=True) または [0, 1] (normalize=False)
            
    Raises:
        ImageProcessingError: 変換に失敗した場合
    """
    try:
        # RGB変換
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # 前処理パイプライン構築
        transform_list = []
        
        if target_size is not None:
            transform_list.extend([
                transforms.Resize(target_size),
                transforms.CenterCrop(target_size)
            ])
        
        transform_list.append(transforms.ToTensor())  # [0, 1] 変換
        
        if normalize:
            transform_list.append(
                transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])  # [-1, 1] 正規化
            )
        
        transform = transforms.Compose(transform_list)
        tensor = transform(pil_image)
        
        return tensor
        
    except Exception as e:
        raise ImageProcessingError(f"Failed to convert PIL to tensor: {str(e)}")


class ImageProcessor:
    """
    VAE用画像処理クラス（設定の一元管理）
    
    設定を事前に指定して、複数の画像に対して一貫した前処理を適用する場合に使用。
    """
    
    def __init__(self, 
                 target_size: int = 512,
                 normalize_mean: Tuple[float, float, float] = (0.5, 0.5, 0.5),
                 normalize_std: Tuple[float, float, float] = (0.5, 0.5, 0.5)):
        """
        Args:
            target_size: リサイズ後のサイズ
            normalize_mean: 正規化の平均値
            normalize_std: 正規化の標準偏差
        """
        self.target_size = target_size
        self.normalize_mean = normalize_mean  
        self.normalize_std = normalize_std
        
        # 変換パイプライン構築
        self.transform = transforms.Compose([
            transforms.Resize(target_size),
            transforms.CenterCrop(target_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=normalize_mean, std=normalize_std)
        ])
    
    def load_and_preprocess(self, image_path: Union[str, Path]) -> Tuple[torch.Tensor, Image.Image]:
        """
        画像読み込み・前処理（設定済みパラメータ使用）
        
        Args:
            image_path: 画像ファイルのパス
            
        Returns:
            Tuple[torch.Tensor, Image.Image]: (前処理済みテンソル, 元PIL画像)
        """
        return load_and_preprocess_image(image_path, self.target_size)
    
    def preprocess_pil(self, pil_image: Image.Image) -> torch.Tensor:
        """
        PIL画像から前処理済みテンソル生成
        
        Args:
            pil_image: PIL画像
            
        Returns:
            torch.Tensor: 前処理済みテンソル [1, 3, H, W]
        """
        try:
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            tensor = self.transform(pil_image).unsqueeze(0)  # バッチ次元追加
            return tensor
            
        except Exception as e:
            raise ImageProcessingError(f"Failed to preprocess PIL image: {str(e)}")


# 事前設定済みプロセッサインスタンス
DEFAULT_PROCESSOR = ImageProcessor()
SD_PROCESSOR = ImageProcessor(target_size=512)  # Stable Diffusion用