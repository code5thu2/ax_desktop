import os
from edge_ie_agent.config import load_config, Config

def test_load_config_defaults(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("AIPRO_API_KEY=test-key-123\n")
    
    cfg = load_config(str(env_file))
    assert cfg.api_key == "test-key-123"
    assert "api" in cfg.base_url.lower() or "http" in cfg.base_url.lower()
    assert cfg.edge_keyword == "Edge"
    assert cfg.max_steps == 20

def test_load_config_custom_values(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "AIPRO_API_KEY=my-custom-key\n"
        "AIPRO_BASE_URL=https://custom.aipro.io/v1\n"
        "QWEN_MODEL_NAME=qwen-vl-max\n"
        "EDGE_WINDOW_KEYWORD=Internet Explorer\n"
        "MAX_STEPS=30\n"
    )
    
    cfg = load_config(str(env_file))
    assert cfg.api_key == "my-custom-key"
    assert cfg.base_url == "https://custom.aipro.io/v1"
    assert cfg.model_name == "qwen-vl-max"
    assert cfg.edge_keyword == "Internet Explorer"
    assert cfg.max_steps == 30
