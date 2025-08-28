import hashlib, json
from pathlib import Path

def verify_meve(file_path, meve_path):
    """
    Vérifie qu'un fichier correspond bien à sa preuve .meve.
    - file_path: chemin du document original
    - meve_path: fichier .meve correspondant
    Retourne un dict { valid: bool, reason: str }
    """
    file_path = Path(file_path)
    meve_path = Path(meve_path)

    if not file_path.exists():
        return {"valid": False, "reason": "Fichier original introuvable"}
    if not meve_path.exists():
        return {"valid": False, "reason": "Fichier .meve introuvable"}

    # recalcul du hash
    content = file_path.read_bytes()
    sha256 = hashlib.sha256(content).hexdigest()

    # lecture du .meve
    meve = json.loads(meve_path.read_text(encoding="utf-8"))

    if meve.get("hash_sha256") != sha256:
        return {"valid": False, "reason": "Empreinte SHA-256 non correspondante"}

    return {
        "valid": True,
        "reason": "OK",
        "issuer": meve.get("issuer", "Unknown"),
        "status": meve.get("status", "Unknown"),
        "time": meve.get("time", None)
    }
