from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv

@dataclass(frozen=True)
class Settings:
    environment: str
    base_url: str
    api_base_url: str
    username: str
    password: str
    slack_webhook_url: str | None

def load_settings(environment: str) -> Settings:
    env_file = Path(__file__).resolve().parents[1] / f".env.{environment}"
    if not env_file.exists():
        raise FileNotFoundError(f"Environment file not found: {env_file}")
    load_dotenv(env_file, override=True)
    required = ["BASE_URL", "API_BASE_URL", "USERNAME", "PASSWORD"]
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise RuntimeError(f"Missing configuration: {', '.join(missing)}")
    return Settings(
        environment=environment,
        base_url=os.environ["BASE_URL"].rstrip("/"),
        api_base_url=os.environ["API_BASE_URL"].rstrip("/"),
        username=os.environ["USERNAME"],
        password=os.environ["PASSWORD"],
        slack_webhook_url=os.getenv("SLACK_WEBHOOK_URL") or None,
    )
