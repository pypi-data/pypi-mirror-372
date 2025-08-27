import os
import yaml
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "config.yaml"

def load_config():
    """Loads configuration from the YAML file."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return yaml.safe_load(f)
    return {}

def save_config(config):
    """Saves configuration to the YAML file."""
    with open(CONFIG_FILE, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

def get_or_prompt_path(config, path_key, prompt_text):
    """
    Gets a path from the config or prompts the user, with an option to save.
    """
    paths = config.get("paths", {})
    path_val = paths.get(path_key)

    if path_val and Path(path_val).exists():
        print(f"✓ Found saved {path_key}: {path_val}")
        use_saved = input("Use saved path? (Y/n): ").strip().lower()
        if use_saved not in ['n', 'no']:
            return Path(path_val)

    while True:
        new_path_str = input(f"{prompt_text} (default: current directory): ").strip()
        new_path = Path(new_path_str) if new_path_str else Path.cwd()
        if new_path.is_dir():
            break
        print(f"Error: Path '{new_path}' is not a valid directory. Please try again.")

    save_path = input("Save this path for future runs? (Y/n): ").strip().lower()
    if save_path not in ['n', 'no']:
        if "paths" not in config:
            config["paths"] = {}
        config["paths"][path_key] = str(new_path)
        save_config(config)
        print(f"✓ {path_key} saved to config.yaml.")

    return new_path

def get_training_paths(config):
    """
    Gets training mode paths from config or prompts the user for them.
    Returns a dictionary with the 4 main training paths.
    """
    training_paths = config.get("training_paths", {})
    
    # Check if all paths are configured
    required_paths = {
        'amendments_data_dir': 'Enter path to directory containing CSV amendment files (e.g., Data)',
        'original_laws_dir': 'Enter path to directory containing original law JSON files (e.g., Data/JSON_Laws_v2)', 
        'amended_output_dir': 'Enter path to directory for saving amended law JSON files (e.g., Outputs)',
        'generated_scripts_dir': 'Enter path to directory for saving generated Python scripts (e.g., Outputs/Generated_Scripts_Generalized)'
    }
    
    paths_to_update = {}
    need_save = False
    
    for path_key, prompt_text in required_paths.items():
        path_val = training_paths.get(path_key)
        
        if path_val and Path(path_val).exists():
            print(f"✓ Found saved training {path_key}: {path_val}")
            use_saved = input("Use saved path? (Y/n): ").strip().lower()
            if use_saved not in ['n', 'no']:
                paths_to_update[path_key] = Path(path_val)
                continue
        
        # Provide default suggestions based on current directory
        if path_key == 'amendments_data_dir':
            default_suggestion = "Data"
        elif path_key == 'original_laws_dir':
            default_suggestion = "Data/JSON_Laws_v2"
        elif path_key == 'amended_output_dir':
            default_suggestion = "Outputs"
        elif path_key == 'generated_scripts_dir':
            default_suggestion = "Outputs/Generated_Scripts_Generalized"
        
        print(f"\n{prompt_text}")
        print(f"Suggested default: {default_suggestion}")
        
        while True:
            new_path_str = input(f"Enter path (press Enter for '{default_suggestion}'): ").strip()
            if not new_path_str:
                new_path_str = default_suggestion
            
            new_path = Path(new_path_str)
            
            # Create directory if it doesn't exist
            if not new_path.exists():
                create_dir = input(f"Directory '{new_path}' does not exist. Create it? (Y/n): ").strip().lower()
                if create_dir not in ['n', 'no']:
                    try:
                        new_path.mkdir(parents=True, exist_ok=True)
                        print(f"✓ Created directory: {new_path}")
                        break
                    except Exception as e:
                        print(f"Error creating directory: {e}")
                        continue
                else:
                    print("Please enter a different path.")
                    continue
            elif new_path.is_dir():
                break
            else:
                print(f"Error: '{new_path}' exists but is not a directory. Please try again.")
                continue
        
        paths_to_update[path_key] = new_path
        need_save = True
    
    if need_save:
        save_training = input("Save these training paths for future runs? (Y/n): ").strip().lower()
        if save_training not in ['n', 'no']:
            if "training_paths" not in config:
                config["training_paths"] = {}
            for key, path in paths_to_update.items():
                config["training_paths"][key] = str(path)
            save_config(config)
            print("✓ Training paths saved to config.yaml.")
    
    return paths_to_update

def get_api_key(config):
    """
    Gets Gemini API key from config file or prompts the user, with an option to save.
    """
    api_conf = config.get("api", {})
    api_key = api_conf.get("google_api_key")

    if api_key:
        print("✓ Found GOOGLE_API_KEY in config.yaml.")
        use_existing = input("Use this key? (Y/n): ").strip().lower()
        if use_existing not in ['n', 'no']:
            return api_key

    new_api_key = input("Please enter your GOOGLE_API_KEY: ").strip()
    
    save_key = input("Save this API key to config.yaml for future runs? (Y/n): ").strip().lower()
    if save_key not in ['n', 'no']:
        if "api" not in config:
            config["api"] = {}
        config["api"]["google_api_key"] = new_api_key
        save_config(config)
        print("✓ API key saved to config.yaml.")
        
    return new_api_key

def get_model_config(config):
    """Returns model configuration from the config file."""
    return config.get("model", {
        "name": "gemini-1.5-flash",
        "max_output_tokens": 8192,
        "temperature": 0.2,
        "api_retry_limit": 3,
        "api_retry_delay_seconds": 10,
        "max_script_generation_attempts": 3,
        "max_execution_attempts": 2,
        "self_correction_threshold": 85,
        "self_correction_retries": 2
    })

def get_default_mode(config):
    """
    Gets the default mode from config or prompts the user, with an option to save.
    """
    defaults = config.get("defaults", {})
    mode = defaults.get("mode")

    if mode and mode in ["training", "product"]:
        print(f"✓ Found saved default mode: {mode.title()} Mode")
        use_saved = input("Use saved mode? (Y/n): ").strip().lower()
        if use_saved not in ['n', 'no']:
            return mode

    while True:
        choice = input("Enter default mode (1 for Training, 2 for Product): ").strip()
        if choice == '1':
            new_mode = "training"
            break
        elif choice == '2':
            new_mode = "product"
            break
        print("Invalid choice. Please enter 1 or 2.")

    save_mode = input(f"Save '{new_mode.title()} Mode' as default for future runs? (Y/n): ").strip().lower()
    if save_mode not in ['n', 'no']:
        if "defaults" not in config:
            config["defaults"] = {}
        config["defaults"]["mode"] = new_mode
        save_config(config)
        print("✓ Default mode saved to config.yaml.")

    return new_mode 