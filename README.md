# QuantumShield Banking
### AI-Powered Quantum-Safe Readiness Scanner

Built for the IBM Z Datathon — Theme: **AI Secured: Innovation Without Exposure**

---

## What this is

QuantumShield Banking is a prototype that scans a (simulated) banking environment for cryptographic weaknesses — including algorithms that are already broken (like MD5, DES) and algorithms that are vulnerable to future quantum computers (like RSA, ECC, Diffie-Hellman). It then combines those technical findings with real business context (how sensitive the data is, how long it must be retained, whether the service is public-facing) to produce an **explainable risk score**, a **visual dependency graph**, and a **phased migration roadmap** — all shown in an interactive dashboard with basic login and role-based access control.

No real bank, customer, or quantum computer is involved. This is a self-contained demo built to show the *pattern*: discover → contextualize → score → prioritize → protect.

## Project structure

```
quantumshield/
├── bank-env/              ← synthetic test data: 5 fake banking apps
│   ├── payment-gateway/       (public, PCI data, weak crypto — highest risk)
│   ├── kyc-service/            (internal, PII data, mixed crypto)
│   ├── loan-service/           (internal, financial data, weak DH)
│   ├── internal-test-app/      (no real data — proves low risk despite weak crypto)
│   ├── mobile-banking-api/     (public, already quantum-safe — the "good example")
│   └── README.md               (explains the design of the test data)
│
├── scanner/               ← the Python scanning engine
│   ├── file_walker.py          (finds every relevant file)
│   ├── crypto_detector.py      (detects crypto algorithms in code)
│   ├── cert_reader.py          (reads real certificate details)
│   ├── config_reader.py        (reads each service's business-context blueprint)
│   ├── risk_scorer.py          (explainable AI risk scoring engine)
│   ├── roadmap_generator.py    (turns risk into a phased action plan)
│   ├── report_generator.py     (builds the final CBOM report)
│   ├── run_scan.py             (main script — run this to scan everything)
│   └── cbom_report.json        (output: the full scan results, regenerated each run)
│
├── dashboard/              ← the React website
│   └── src/
│       ├── App.jsx              (main dashboard: ranking, cards, roadmap, login gate)
│       ├── App.css              (all styling)
│       ├── Login.jsx            (login screen)
│       ├── DependencyGraph.jsx  (the visual node/graph view)
│       └── cbom_report.json     (a COPY of the scanner's output — dashboard reads this)
│
├── venv/                   ← Python virtual environment (not part of the project logic)
├── demo_script.md          ← presentation script for judges
└── judge_writeup.md        ← one-page write-up mapping this to IBM Z's alignment
```

## How the pieces fit together

1. `bank-env/` is the input — fake source code, certificates, and blueprints
2. `scanner/run_scan.py` reads `bank-env/`, analyzes everything, and writes `scanner/cbom_report.json`
3. That JSON file is manually copied into `dashboard/src/cbom_report.json`
4. `dashboard/` reads that copy and displays it as an interactive website

**Important:** the scanner and dashboard are two separate programs. Re-running the scanner does *not* automatically update the dashboard — you must re-copy the file (see Step 3 below) and the dashboard will pick up the change automatically since it's already running.

---

## How to run this project from scratch

### Prerequisites (one-time setup)
- Python 3.x installed, with `pip`
- Node.js (LTS version) installed
- Git for Windows installed (provides `openssl`, used only if regenerating certificates)

### Step 1 — Set up and activate the Python virtual environment

```
cd quantumshield
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install cryptography pycryptodome pyyaml
```

You'll need to re-run the `Activate.ps1` line every time you open a new terminal to work on the scanner.

### Step 2 — Run the scanner

```
cd scanner
python run_scan.py
```

This prints the full scan (source code findings, certificate findings, business context, risk scores, priority ranking, and migration roadmap) to the terminal, and saves everything to `scanner/cbom_report.json`.

### Step 3 — Update the dashboard's copy of the data

Every time you re-run the scanner and want the dashboard to reflect new results:

```
cd ..
Copy-Item scanner\cbom_report.json dashboard\src\cbom_report.json
```

### Step 4 — Run the dashboard

```
cd dashboard
npm install    # only needed the very first time
npm run dev
```

Open the URL it prints (typically `http://localhost:5173/`) in your browser. Keep this terminal window open while viewing the dashboard.

### Step 5 — Sign in

The dashboard requires signing in first. Enter any name, and choose either:
- **Viewer** — sees risk scores, explanations, and the roadmap, but not vendor names or certificate technical details
- **Security Analyst** — sees everything, including the access audit log

---

## Regenerating certificates (only needed if you rebuild bank-env from scratch)

If `OPENSSL_CONF` isn't already set in your terminal session, run this first:

```
$env:OPENSSL_CONF = "C:\Program Files\Git\mingw64\etc\ssl\openssl.cnf"
```

Then, inside each service's `certs/` folder, use the appropriate command (RSA for `payment-gateway`, ECC for `kyc-service`) — see the scanner/demo history for exact commands used.

---

## Known limitations (be upfront about these if asked)

- **Synthetic data only** — `bank-env` is fictional, built specifically for this demo
- **Pattern-matching, not full static analysis** — the crypto detector uses text/regex matching rather than a full code-parsing tool like Semgrep
- **Self-declared login role** — not connected to a real identity provider (e.g. SSO/Active Directory)
- **In-memory audit log** — resets on page refresh; not yet written to persistent storage
- **No real quantum computer involved** — by design. This tool prepares for a *future* threat using entirely classical computing today

## Credits / Alignment

Built to align with IBM Z's quantum-safe security guidance: discover cryptographic assets, classify by risk, assess business impact, and prioritize migration — before adopting quantum-safe cryptography on platforms like IBM Z (Crypto Express, ICSF, pervasive encryption).
