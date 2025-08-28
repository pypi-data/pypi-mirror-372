"""
DigitalMeve — Official identity helpers (draft)

Purpose:
- Verify domain ownership via DNS TXT challenge for `Status: Official`.
- Optional org key issuance (Ed25519) to co-sign `.MEVE`.

These are stubs to structure the repo without impacting the MVP.
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from typing import Optional


def create_dns_challenge(domain: str) -> str:
    """
    Return a nonce to be placed in a DNS TXT record at: _meve.<domain>
    Example value: "meve-verify=<nonce>"
    """
    nonce = secrets.token_urlsafe(24)
    return f"meve-verify={nonce}"


def verify_dns_challenge(domain: str, expected_value: str) -> bool:
    """
    TODO: Resolve TXT for _meve.<domain> and compare value against expected_value.
    In MVP, this remains a stub (returns False). Implement in Phase 2.
    """
    return False


@dataclass
class OfficialBadge:
    domain: str
    dns_verified: bool
    org_key_id: Optional[str] = None  # future


def issue_official_badge(domain: str, dns_verified: bool) -> OfficialBadge:
    """Create a badge object that can be embedded in verification UI."""
    return OfficialBadge(domain=domain, dns_verified=dns_verified)
