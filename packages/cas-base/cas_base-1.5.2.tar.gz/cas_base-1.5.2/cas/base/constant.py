import os
from dotenv import load_dotenv

load_dotenv()

base_dir = "./"
config_dir = os.path.join(base_dir, "config")
log_dir = os.path.join(config_dir, "logs")
log_level = os.getenv("LOG_LEVEL", "INFO")
current_env = os.getenv("CURRENT_ENV", "pro")

is_dev = current_env == "dev"

if not os.path.exists(config_dir):
    os.makedirs(config_dir)

if not os.path.exists(log_dir):
    os.makedirs(log_dir)
