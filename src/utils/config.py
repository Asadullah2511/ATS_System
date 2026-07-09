import os
from pathlib import Path
from dotenv import load_dotenv


def load_config():
    env_path = Path(__file__).parent.parent.parent / '.env'
    load_dotenv(env_path)

    config = {
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        'anthropic_api_key': os.getenv('ANTHROPIC_API_KEY'),
        'database_url': os.getenv('DATABASE_URL', 'sqlite:///./ats_system.db'),
        'redis_host': os.getenv('REDIS_HOST', 'localhost'),
        'redis_port': int(os.getenv('REDIS_PORT', 6379)),
        'redis_db': int(os.getenv('REDIS_DB', 0)),
        'log_level': os.getenv('LOG_LEVEL', 'INFO'),
    }

    return config
