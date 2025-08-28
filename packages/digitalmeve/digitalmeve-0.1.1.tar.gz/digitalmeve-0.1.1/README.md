# DigitalMeve — The Certified Digital Memory

[![Tests](https://github.com/BACOUL/digitalmeve/actions/workflows/tests.yml/badge.svg)](https://github.com/BACOUL/digitalmeve/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## 🚀 Vision

**DigitalMeve** defines a new universal format of digital certification: **.MEVE (Memory Verified)**.  
A simple, human-readable (2-second) proof that attests:

- 📌 The **existence** of a document at a given date  
- 🔐 The **integrity** of the document (SHA-256 fingerprint)  
- 👤 The **authenticity** of the **issuer** (person, professional, or institution)

**Goal:** become the “**PDF of digital proof**” for the world.

---

## 🧩 What is a `.meve` file?

A small, signed proof file **linked to any document**. It contains:
- the document’s SHA-256 `hash`,
- the original file name & MIME type,
- the generation timestamp (ISO 8601),
- the **issuer** identity (e.g., email/domain) and **signature** (base64).

It can live as:
- **embedded metadata** (for formats that support it), or
- **sidecar** JSON file (`yourfile.meve.json`) for maximal interoperability.

---

## 📦 Quickstart

### 1) Clone & install
```bash
git clone https://github.com/BACOUL/digitalmeve.git
cd digitalmeve
python -m venv .venv && source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt

2) Generate a .meve proof

python cli_generate.py \
  --file ./examples/facture.pdf \
  --issuer "contact@example.com" \
  --out ./examples/facture.meve

3) Verify a document against its proof

python cli_verify.py \
  --file ./examples/facture.pdf \
  --meve ./examples/facture.meve

If your format has no metadata (e.g., .txt) or the file is very large, use the sidecar:

python cli_generate.py --file big.pdf --issuer "contact@example.com" --out big.meve.json
python cli_verify.py   --file big.pdf --meve big.meve.json


---

🛠️ How it works (high-level)

1. We compute the SHA-256 of the document.


2. We create a compact proof structure (issuer, timestamp, file meta, hash).


3. We sign that structure and store the signature with the proof.


4. Verification recomputes the hash and checks the signature & fields.



> ✅ If any metadata or content is modified, verification fails instantly.




---

📄 Example of a .meve (human-readable)

MEVE/1
Status: Pro
Issuer: contact@example.com
Certified: DigitalMeve (email verified)
Time: 2025-08-27T22:35:01Z
Hash-SHA256: 5f2a6c4cf0b67d2f9c3f8ad...
ID: MEVE-9XJ3L
Signature: 0JfA0a9sDsa7D3gS== (base64 Ed25519)
Meta: facture.pdf • 18230 bytes • application/pdf
Doc-Ref: facultatif

Visible instantly — no complex tools required.


---

🔒 Security & integrity

Tamper-proof by design: the SHA-256 hash binds the proof to the exact content.

Metadata edits (title, author, etc.) are detected because the verification recomputes the hash.

Large files: prefer sidecar .meve.json to avoid touching heavy binaries.

Interoperability: sidecar works for all formats (including .txt).

Legal note: the proof attests to the content (hash), not the visual rendering.
For example, a “PDF optimization” that changes bytes changes the hash → it’s a different document.


See SECURITY.md to report a vulnerability.


---

✅ Tests (CI)

Unit tests run on GitHub Actions for Python 3.10 / 3.11 / 3.12.

Local run:


pip install -r requirements.txt
pytest -q


---

🗺️ Roadmap (next milestones)

🔐 Optional public-key registry for issuer discovery & trust.

🧾 Embedded metadata for more formats; seamless sidecar fallback.

🧰 Official pip package (digitalmeve) and stable CLI.

🌍 Multilingual docs.


Track progress in CHANGELOG.md and Releases.


---

🤝 Contributing & community

Start with CONTRIBUTING.md

Follow our Code of Conduct

Open issues with our templates: .github/ISSUE_TEMPLATE/

Ask questions or propose ideas in Discussions.



---

📜 License

Released under the MIT License — permissive for commercial and open source use.
See LICENSE.
If you use DigitalMeve in production, please keep a link to the repo:

DigitalMeve — https://github.com/BACOUL/digitalmeve  (MIT)


---

🔗 Useful links

Releases: https://github.com/BACOUL/digitalmeve/releases

Actions (CI): https://github.com/BACOUL/digitalmeve/actions

Issues: https://github.com/BACOUL/digitalmeve/issues

Discussions: https://github.com/BACOUL/digitalmeve/discussions



---

© 2025 DigitalMeve. All rights reserved under MIT terms.
