"""Configuration management for Edge IE Visual Agent."""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

@dataclass
class Config:
    api_key: str
    base_url: str = "https://api.aipro.vn/v1"
    model_name: str = "qwen-vl-plus"
    edge_keyword: str = "Edge"
    max_steps: int = 20

def load_config(env_path: Optional[str] = None) -> Config:
    """Loads configuration from environment variables or .env file."""
    if env_path and os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path, override=True)
    else:
        load_dotenv(override=True)
        
    api_key = os.getenv("AIPRO_API_KEY", "")
    base_url = os.getenv("AIPRO_BASE_URL", "https://api.aipro.vn/v1")
    model_name = os.getenv("QWEN_MODEL_NAME", "qwen-vl-plus")
    edge_keyword = os.getenv("EDGE_WINDOW_KEYWORD", "Edge")
    max_steps_str = os.getenv("MAX_STEPS", "20")
    
    try:
        max_steps = int(max_steps_str)
    except ValueError:
        max_steps = 20
        
    return Config(
        api_key=api_key,
        base_url=base_url,
        model_name=model_name,
        edge_keyword=edge_keyword,
        max_steps=max_steps
    )
