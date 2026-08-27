"""
One-off LOCAL utility: encrypts a plaintext JSON configuration file into
secret_data.enc using a Fernet symmetric key.

Usage:
    python encrypt_secret.py

Every run generates a FRESH key and overwrites the .env file with it
entirely -- whatever was in .env before (including a previous key) is
discarded, no check is made first. Nothing is read from or exported to
the system/shell environment; the key lives only in this .env file.

NEVER commit secret_data.json (the plaintext) or the .env file to
version control -- add "secret_data.json" and ".env" to .gitignore
yourself.
"""

import json
import os
from pathlib import Path

from cryptography.fernet import Fernet

ENV_VAR_NAME = "ADIR_SECRET_KEY"

CONFIG_ENC_FILE = Path(__file__).resolve().parent.parent / "data" / "secret_data.enc"
CONFIG_ENV = Path(__file__).resolve().parent.parent / "data" / ".env"


def write_key_to_env_file(key: str, env_path: Path) -> None:
    """Overwrite the .env file entirely with just this one line."""
    env_path.write_text(f"{ENV_VAR_NAME}={key}\n", encoding="utf-8")
    try:
        os.chmod(env_path, 0o600)  # restrict to the current user
    except OSError:
        pass  # not fatal if this hardening step fails


def build_key_data(input_path: Path, output_path: Path = CONFIG_ENC_FILE, env_path: Path = CONFIG_ENV) -> None:
    key = Fernet.generate_key().decode()
    write_key_to_env_file(key, env_path)

    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    encrypted = Fernet(key.encode()).encrypt(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    with output_path.open("wb") as f:
        f.write(encrypted)