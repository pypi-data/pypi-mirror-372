import os
from .utils import sha256_path, iso8601_now, guess_mime

def generate_meve(file_path: str, issuer: str = "unknown", signature: str | None = None) -> dict:
    """
    Génère un dictionnaire représentant les métadonnées d'un fichier.
    - file_path : chemin du fichier
    - issuer : émetteur (par défaut "unknown")
    - signature : signature optionnelle

    Retourne un dict avec : path, hash, size, mime, created_at, issuer, signature.
    """
    return {
        "path": file_path,
        "hash": sha256_path(file_path),
        "size": os.path.getsize(file_path),
        "mime": guess_mime(file_path),
        "created_at": iso8601_now(),
        "issuer": issuer,
        "signature": signature,
    }
