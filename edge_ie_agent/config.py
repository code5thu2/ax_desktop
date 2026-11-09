"""Configuration management for Multi-Agent Edge IE Automation."""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

@dataclass
class Config:
    api_key: str
    base_url: str = "https://api.aipro.vn/v1"
    glm_model: str = "glm-4-flash"        # Main Orchestrator (Fast Text)
    qwen_model: str = "qwen-vl-plus"      # Vision Subagent (Screen Perception)
    edge_keyword: str = "Edge"
    max_steps: int = 20
    model_name: Optional[str] = None

    def __post_init__(self):
        if self.model_name and not self.qwen_model:
            self.qwen_model = self.model_name
        elif not self.model_name:
            self.model_name = self.qwen_model

def load_config(env_path: Optional[str] = None) -> Config:
    """Loads configuration from environment variables or .env file."""
    if env_path and os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path, override=True)
    else:
        load_dotenv(override=True)
        
    api_key = os.getenv("AIPRO_API_KEY", "")
    base_url = os.getenv("AIPRO_BASE_URL", "https://api.aipro.vn/v1")
    glm_model = os.getenv("GLM_MODEL_NAME", "glm-4-flash")
    qwen_model = os.getenv("QWEN_MODEL_NAME", "qwen-vl-plus")
    edge_keyword = os.getenv("EDGE_WINDOW_KEYWORD", "Edge")
    max_steps_str = os.getenv("MAX_STEPS", "20")
    
    try:
        max_steps = int(max_steps_str)
    except ValueError:
        max_steps = 20
        
    return Config(
        api_key=api_key,
        base_url=base_url,
        glm_model=glm_model,
        qwen_model=qwen_model,
        edge_keyword=edge_keyword,
        max_steps=max_steps
    )
