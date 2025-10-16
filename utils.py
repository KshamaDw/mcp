import json

def load_config(file_path = 'mcp_config.json'):
    with open(file_path, 'r') as f:
        config = json.load(f)
    return config

def save_config(config, file_path = 'mcp_config.json'):
    with open(file_path, 'w') as f:
        json.dump(config, f, indent=4)
    return