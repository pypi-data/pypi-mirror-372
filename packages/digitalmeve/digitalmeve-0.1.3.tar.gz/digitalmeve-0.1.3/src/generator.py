import hashlib, json, datetime
from pathlib import Path

def generate_meve(file_path, issuer="DigitalMeve", status="Pro", output_path=None):
    """
    Génère un fichier .meve lié à un document.
    - file_path: chemin du fichier à certifier
    - issuer: émetteur de la preuve (par défaut: DigitalMeve)
    - status: type (Pro, Personal, Official)
    - output_path: chemin de sortie optionnel
    """
    file_path = Path(file_path)
    content = file_path.read_bytes()
    sha256 = hashlib.sha256(content).hexdigest()

    meve = {
        "version": "MEVE/1",
        "status": status,
        "issuer": issuer,
        "time": datetime.datetime.utcnow().isoformat() + "Z",
        "hash_sha256": sha256,
        "meta": {
            "filename": file_path.name,
            "size": file_path.stat().st_size,
        },
    }

    # fichier de sortie
    out = Path(output_path) if output_path else file_path.with_suffix(file_path.suffix + ".meve")
    out.write_text(json.dumps(meve, indent=2), encoding="utf-8")
    return out
