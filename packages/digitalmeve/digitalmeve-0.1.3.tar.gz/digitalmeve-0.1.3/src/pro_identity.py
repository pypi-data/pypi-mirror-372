"""
DigitalMeve — Pro identity helpers (draft)

Purpose:
- Verify a professional email before issuing a `.MEVE` with `Status: Pro`.
- This file contains stubs so the repo is structured without blocking MVP.

Nothing here is executed by current tests; safe to keep as TODOs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class ProVerificationResult:
    email: str
    domain: str
    is_business_domain: bool
    verified: bool
    reason: Optional[str] = None


DISPOSABLE_HINTS = {"mailinator.com", "guerrillamail.com", "tempmail.com"}


def looks_business_domain(domain: str) -> bool:
    """Very light heuristic: not disposable, not common free-mail providers."""
    common_free = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "live.com"}
    if domain in DISPOSABLE_HINTS:
        return False
    if domain in common_free:
        return False
    return "." in domain  # minimal check


def verify_email_address(email: str) -> ProVerificationResult:
    """
    TODO: send magic link / one-time code and confirm ownership.
    For now, returns a stubbed 'verified=False' to avoid side-effects in MVP.
    """
    try:
        local, domain = email.split("@", 1)
    except ValueError:
        return ProVerificationResult(email=email, domain="", is_business_domain=False, verified=False, reason="invalid-email")

    return ProVerificationResult(
        email=email,
        domain=domain.lower(),
        is_business_domain=looks_business_domain(domain.lower()),
        verified=False,  # flip to True once we implement the email challenge
        reason="stub-verification",
    )
