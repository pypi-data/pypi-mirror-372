# DigitalMeve — The Certified Digital Memory

[![Tests](https://img.shields.io/github/actions/workflow/status/BACOUL/digitalmeve/tests.yml?label=tests)](https://github.com/BACOUL/digitalmeve/actions)
[![Publish](https://img.shields.io/github/actions/workflow/status/BACOUL/digitalmeve/publish.yml?label=publish)](https://github.com/BACOUL/digitalmeve/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](#-license)
[![PyPI](https://img.shields.io/pypi/v/digitalmeve.svg)](https://pypi.org/project/digitalmeve/)

**DigitalMeve** introduces a simple, universal proof format: **`.MEVE`** (Memory Verified).  
It lets anyone **timestamp & prove** a document’s existence and integrity, and lets professionals/institutions **certify** provenance.

---

## 🔰 What a `.MEVE` proves
1. **Existence at a given date** (UTC timestamp)
2. **Integrity of the content** (SHA-256 hash)
3. **Issuer link** (Personal / Pro / Official)
4. **Authenticity** via **Ed25519** digital signature (Base64)

> **Important:** the proof binds to the **content bytes** (hash), not to the visual rendering of a document.

---

## 🧩 Levels of trust
- **Personal** — self-asserted proof (free): existence + integrity.
- **Pro** — **email verified** at a business domain (paid): links proof to a professional identity.
- **Official** — **DNS-verified domain** (and optional org signing key): institutional/official provenance.

The status is **computed by the verifier**, never user-declared.

---

## 📦 Install

```bash
pip install -U digitalmeve

Command-line tools:

# Generate a .MEVE for a document
meve-generate path/to/document.pdf --issuer-email you@domain.com --status Pro --meta ref=FAC-2025 amount=123.45

# Verify a .MEVE against the original document (auto-detects sidecar)
meve-verify path/to/document.pdf
# or explicitly:
meve-verify path/to/document.pdf --meve path/to/document.pdf.meve

Python usage (soon):

from src.generator import generate_meve
from src.verifier import verify_meve


---

🗂️ .MEVE/1 text format (spec)

MEVE/1
Status: Official | Pro | Personal
Issuer: <identity>
Certified: DigitalMeve (dns|email|self)
Time: <UTC ISO8601>
Hash-SHA256: <hex digest>
ID: <short code>
Signature: <base64 Ed25519>
Meta: <filename> • <size bytes> • <mime>
Doc-Ref: <optional>

Default: inline .meve file.

Fallback for large/unsupported formats: myfile.ext.meve.json (sidecar).

The verifier recomputes the hash from the original file and checks the signature.



---

🧪 Examples

# Example: create proof for invoice.pdf
meve-generate examples/invoice.pdf --issuer-email billing@acme.com --status Pro --meta ref=FAC-2025 client=ACME amount=123.45

# Verify later
meve-verify examples/invoice.pdf

examples/ will contain sample files (invoice.pdf + invoice.pdf.meve) in next releases.


---

🔒 Security model

Hash: SHA-256 over the exact bytes of the document. Any modification → different hash → verification fails.

Signature: Ed25519 (Base64) issued by DigitalMeve; prevents tampering with the .meve file itself.

Sidecar fallback: for formats without stable metadata or large files (>50MB), use *.meve.json.

No private data inside signature; meta fields are minimal.



---

⚖️ Legal notes (plain language)

A .MEVE is a technical proof (existence + integrity + issuer link).

It is not a legal certification by itself.

Personal = self-asserted; Pro = email verified; Official = DNS/org verified.

Where applicable, DigitalMeve can export a PDF footer “Certified by DigitalMeve” (Phase 2).



---

👤 Pro (email) — draft

Flow: user proves ownership of name@company.tld (magic link or one-time code).

Proof fields: Status: Pro, Certified: DigitalMeve (email), issuer = the verified email.

Heuristics deny disposable/public free-mail for Pro status.

See docs/PRO.md.


🏛️ Official (DNS/org) — draft

Flow: admin adds a DNS TXT challenge at _meve.<domain> and we verify it.

Proof fields: Status: Official, Certified: DigitalMeve (dns), issuer = org name/domain.

Optional org signing key (Ed25519) for co-signature (later).

See docs/OFFICIAL.md.



---

🗺️ Roadmap

[x] Personal (MVP): generate & verify .MEVE (hash + Ed25519)

[x] Packaging (PyPI) and CLI (meve-generate, meve-verify)

[x] CI (tests) + Releases (Trusted Publisher → PyPI)

[ ] Examples: examples/invoice.pdf + invoice.pdf.meve

[ ] Website (Framer) — Personal only v1

[ ] Pro verification (email) — docs/PRO.md

[ ] Official verification (DNS/org) — docs/OFFICIAL.md

[ ] Public API + PDF footer “Certified by DigitalMeve” (Phase 2)



---

🤝 Contributing

See CONTRIBUTING.md.
Please open issues/discussions for proposals; PRs welcome.


---

🔐 Security

See SECURITY.md.
If you suspect a vulnerability, contact us privately before disclosure.


---

📜 License

MIT © DigitalMeve.
The names DigitalMeve and .MEVE are used as project identifiers; please attribute in derivative works.


---

📎 Project links

Homepage: https://github.com/BACOUL/digitalmeve

Issues: https://github.com/BACOUL/digitalmeve/issues

PyPI: https://pypi.org/project/digitalmeve/

Pro spec: docs/PRO.md — Official spec: docs/OFFICIAL.md


---
