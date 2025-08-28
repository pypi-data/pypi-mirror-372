"""Configuration management for Harmony Benchmark."""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any
import os


class ModelMode(Enum):
    """Available model execution modes."""
    API = "api"
    LOCAL_TRANSFORMERS = "local_transformers" 
    LOCAL_OLLAMA = "local_ollama"


@dataclass
class BenchmarkConfig:
    """Configuration for benchmark execution."""
    
    
    mode: ModelMode = ModelMode.API
    max_workers: int = 10
    
    
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None
    api_model: str = "openai/gpt-oss-20b"
    
    # Local Transformers settings
    local_model_name: str = "openai/gpt-oss-20b"
    device: str = "auto"  # auto, cpu, cuda
    max_length: int = 512
    
    # Local Ollama settings  
    ollama_model: str = "llama2"
    ollama_host: str = "localhost"
    ollama_port: int = 11434
    
    # Output settings
    show_plots: bool = True
    save_results: bool = True
    results_file: str = "benchmark_results.json"
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.mode == ModelMode.API and not self.api_key:
            self.api_key = os.getenv('OPENROUTER_API_KEY')
            if not self.api_key:
                raise ValueError("API key required for API mode. Set OPENROUTER_API_KEY")
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'BenchmarkConfig':
        """Create config from dictionary."""
        if 'mode' in config_dict and isinstance(config_dict['mode'], str):
            config_dict['mode'] = ModelMode(config_dict['mode'])
        return cls(**config_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, ModelMode):
                result[key] = value.value
            else:
                result[key] = value
        return result