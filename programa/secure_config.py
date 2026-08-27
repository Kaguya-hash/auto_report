"""
Loads the encrypted clinical configuration (scoring rules, cut-offs, and
item text) that build_report.py needs -- without that content ever
existing as plain, greppable source code in this repository.

The decryption key can come from two places, controlled by the
use_env_file argument:

- use_env_file=False (default): read from the ADIR_SECRET_KEY system
  environment variable (e.g. exported in your shell profile, stored in
  your OS keychain, or injected by whatever secrets manager you use).
- use_env_file=True: read from the ADIR_SECRET_KEY line in the given
  .env file instead (system environment is not consulted at all).

Either way, anyone who has the code but not the key -- wherever it
lives -- cannot read secret_data.enc.
"""

import json
import os

from cryptography.fernet import Fernet, InvalidToken

from pathlib import Path

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "data" / "secret_data.enc"
DEFAULT_CONFIG_ENV = Path(__file__).resolve().parent.parent / "data" / ".env"
KEY_ENV_VAR = "ADIR_SECRET_KEY"


def _read_key_from_env_file(env_path: Path) -> str | None:
    if not env_path.exists():
        return None
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith(f"{KEY_ENV_VAR}="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def load_config(
    path: Path = DEFAULT_CONFIG_PATH,
    use_env_file: bool = False,
    env_path: Path = DEFAULT_CONFIG_ENV,
) -> dict:
    if use_env_file:
        key = _read_key_from_env_file(env_path)
        if not key:
            raise RuntimeError(
                f"A chave {KEY_ENV_VAR} não foi encontrada em {env_path}. "
                "Corra encrypt_secret.py para gerar o ficheiro .env com a chave."
            )
    else:
        key = os.environ.get(KEY_ENV_VAR)
        if not key:
            raise RuntimeError(
                f"A variável de ambiente {KEY_ENV_VAR} não está definida. "
                "Defina-a (fora do repositório) com a chave gerada por "
                "encrypt_secret.py antes de correr este programa."
            )

    with open(path, "rb") as f:
        encrypted = f.read()

    try:
        decrypted = Fernet(key.encode()).decrypt(encrypted)
    except InvalidToken as exc:
        raise RuntimeError(
            "Não foi possível decifrar a configuração: chave incorreta, "
            "ou o ficheiro secret_data.enc está corrompido."
        ) from exc

    return json.loads(decrypted)































"""
Loads the encrypted clinical configuration (scoring rules, cut-offs, and
item text) that build_report.py needs -- without that content ever
existing as plain, greppable source code in this repository.

The decryption key is never read from a file inside the project. It must
be supplied at runtime through the ADIR_SECRET_KEY environment variable
(e.g. exported in your shell profile, stored in your OS keychain, or
injected by whatever secrets manager you use). Anyone who has the code
but not this environment variable cannot read secret_data.enc.
"""

'''import json
import os

from cryptography.fernet import Fernet, InvalidToken

from pathlib import Path

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "data" / "secret_data.enc"
DEFAULT_CONFIG_ENV = Path(__file__).resolve().parent.parent / "data" / ".env"
KEY_ENV_VAR = "ADIR_SECRET_KEY"


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> dict:
    key = os.environ.get(KEY_ENV_VAR)
    if not key:
        raise RuntimeError(
            f"A variável de ambiente {KEY_ENV_VAR} não está definida. "
            "Defina-a (fora do repositório) com a chave gerada por "
            "encrypt_secret.py antes de correr este programa."
        )

    with open(path, "rb") as f:
        encrypted = f.read()

    try:
        decrypted = Fernet(key.encode()).decrypt(encrypted)
    except InvalidToken as exc:
        raise RuntimeError(
            "Não foi possível decifrar a configuração: chave incorreta, "
            "ou o ficheiro secret_data.enc está corrompido."
        ) from exc

    return json.loads(decrypted)
'''