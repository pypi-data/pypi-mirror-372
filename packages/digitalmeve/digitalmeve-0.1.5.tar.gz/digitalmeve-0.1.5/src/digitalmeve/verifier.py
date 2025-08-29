from __future__ import annotations

from typing import Any, Optional

from .utils import format_identity


def verify_identity(data: Any, expected_issuer: Optional[str] = None) -> bool:
    """
    Vérifie l'identité de façon robuste.
    - `data` peut être une chaîne ou un dict contenant 'issuer'/'name'.
    - comparaison insensible à la casse, avec trimming.
    - renvoie False s'il n'y a pas d'attendu.
    """
    if expected_issuer is None:
        return False

    # Extraire l'émetteur réel depuis data (string ou dict)
    actual = None
    if isinstance(data, dict):
        actual = data.get("issuer") or data.get("name") or data
    else:
        actual = data

    return format_identity(actual) == format_identity(expected_issuer)
