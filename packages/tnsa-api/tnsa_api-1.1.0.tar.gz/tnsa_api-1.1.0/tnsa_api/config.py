"""
Configuration management for TNSA API client.
"""

import os
import yaml
from typing import Optional, Dict, Any, Union
from pathlib import Path


class Config:
    """Configuration manager for TNSA API client."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        config_file: Optional[Union[str, Path]] = None,
    ):
        """
        Initialize configuration with priority:
        1. Explicit parameters
        2. Environment variables
        3. Configuration file
        4. Default values
        """
        self._config_file = config_file or self._find_config_file()
        self._file_config = self._load_config_file()
        
        # Set configuration with priority
        self.api_key = (
            api_key 
            or os.getenv("TNSA_API_KEY")
            or self._file_config.get("api_key")
        )
        
        self.base_url = (
            base_url
            or os.getenv("TNSA_BASE_URL") 
            or self._file_config.get("base_url")
            or "https://api.tnsaai.com"
        ).rstrip("/")
        
        self.timeout = float(
            timeout
            or os.getenv("TNSA_TIMEOUT")
            or self._file_config.get("timeout")
            or 30.0
        )
        
        self.max_retries = int(
            max_retries
            or os.getenv("TNSA_MAX_RETRIES")
            or self._file_config.get("max_retries")
            or 3
        )
        
        self.default_model = (
            os.getenv("TNSA_DEFAULT_MODEL")
            or self._file_config.get("default_model")
            or "NGen3.9-Pro"
        )
        
        self.log_level = (
            os.getenv("TNSA_LOG_LEVEL")
            or self._file_config.get("log_level")
            or "WARNING"
        )
        
        # Validate required configuration
        if not self.api_key:
            raise ValueError(
                "API key is required. Set TNSA_API_KEY environment variable, "
                "provide api_key parameter, or add it to config file."
            )
    
    def _find_config_file(self) -> Optional[Path]:
        """Find configuration file in common locations."""
        possible_paths = [
            Path("config.yaml"),
            Path("tnsa_config.yaml"),
            Path(".tnsa/config.yaml"),
            Path.home() / ".tnsa" / "config.yaml",
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        return None
    
    def _load_config_file(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self._config_file or not Path(self._config_file).exists():
            return {}
        
        try:
            with open(self._config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Warning: Failed to load config file {self._config_file}: {e}")
            return {}
    
    def get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        return {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": "tnsa-api-python/1.0.0",
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "api_key": "***" if self.api_key else None,  # Mask API key
            "base_url": self.base_url,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "default_model": self.default_model,
            "log_level": self.log_level,
        }