# 🧠 RecallOps: Incident Response with Persistent Memory

> **Hackathon Submission:** AI Agents That Learn Using Hindsight (by Vectorize)  
> **Track:** Engineering & DevOps — Incident Response Agent  
> **Built With:** [Hindsight](https://hindsight.vectorize.io/), [Groq](https://groq.com/), Streamlit, Python  

---

## 📌 Problem Statement: The Incident Amnesia Tax

When production systems fail at 2:00 AM, on-call engineers face an uphill battle:
- *Has this incident happened before?*
- *Which troubleshooting attempts failed previously?*
- *What was the actual root cause and resolution?*
- *What read-only checks should we run before making risky production changes?*

Stateless AI chatbots and standard LLMs fail during outages because they **lack operational memory**. They repeatedly recommend generic fixes (such as service restarts or pod reboots) without knowing that the exact same action caused cascading failures in last month's post-mortem.

**RecallOps** bridges this gap by using **Hindsight persistent memory**. It recalls verified past incident post-mortems, explicitly warns engineers against repeating previously failed actions, cites historical evidence (`[E1]`, `[E2]`), and closes the learning loop by saving confirmed outcomes back into memory.

---

## 🌟 Why Memory Is the Star (The Hindsight Advantage)

| Capability | Generic AI (Without Memory) | RecallOps (With Hindsight Memory) |
| :--- | :--- | :--- |
| **Outage Troubleshooting** | Suggests generic restarts, scaling replicas, or credential refreshes. | Recalls that restarting previously failed (`[E4]`) and identifies the real root cause (`[E1]`). |
| **Anti-Pattern Prevention** | Recommends actions that previously prolonged downtime. | **Actively warns** engineers: *"Do NOT restart—restart failed in Incident TEST-001 [E4]; revert connection pool settings instead [E3]."* |
| **Evidence & Grounding** | Hallucinates plausible-sounding configurations or metric names. | Cites concrete historical post-mortems with strict ASCII citations (`[E1]`, `[E2]`). |
| **Continuous Learning** | Retains zero context between incidents or sessions. | Post-mortems recorded today immediately inform tomorrow's triage without model retraining. |

---

## 🏗️ Architecture & Continuous Feedback Loop

```mermaid
flowchart TD
    User["👨‍💻 On-Call Engineer"] -->|1. Reports Incident Symptoms| StreamlitUI["Streamlit Dashboard (RecallOps)"]
    StreamlitUI -->|2. Query Semantic Context| Hindsight["🧠 Hindsight Memory Bank (Vectorize)"]
    Hindsight -->|3. Recalled Post-Mortems [E1, E2...]| Agent["Incident Triage Engine (incident_agent.py)"]
    StreamlitUI -->|Current Symptoms| Agent
    Agent -->|4. Prompt with Grounding Rules| GroqLLM["⚡ Groq LLM (openai/gpt-oss-120b)"]
    GroqLLM -->|Draft Plan| SafetyReviewer["🛡️ Automated Safety Reviewer (evidence_review.py)"]
    SafetyReviewer -->|Verified Plan & Citations| StreamlitUI
    User -->|5. Confirms Actual Resolution| RecordOutcome["Record Post-Mortem (pages/2_Record_Outcome.py)"]
    RecordOutcome -->|6. client.retain()| Hindsight
```

---

## 🛡️ Safety & Reliability Principles

1. **Advisory by Design:** RecallOps never executes production changes automatically. All remediation requires explicit human approval, rollback procedures, and post-change verification.
2. **Read-Only First:** Every step in the prioritized investigation plan is explicitly qualified as safe and non-disruptive (e.g., inspecting metrics, reading audit logs).
3. **Automated Safety Reviewer (`evidence_review.py`):** Every generated draft is evaluated by a secondary model pass that validates:
   - Historical vs. current incident separation (never assumes past fixes were attempted now).
   - Citation validity (every historical claim must cite a valid `[E#]` label).
   - Strictly relevant evidence (ignores crosstalk from unrelated services).
   - Credential safety (never asks for secrets or advises rolling back to unverified credentials).

---

## 🚀 Getting Started

### 1. Clone & Set Up Virtual Environment

```bash
git clone https://github.com/your-username/RecallOps.git
cd RecallOps

python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file based on `.env.example`:

```env
HINDSIGHT_API_URL=https://api.hindsight.vectorize.io
HINDSIGHT_API_KEY=your_hindsight_api_key
HINDSIGHT_BANK_ID=recallops-demo
GROQ_API_KEY=your_groq_api_key
```

### 3. Seed Demo Memories (Optional)

Run the connection test script to create the memory bank and seed synthetic demonstration data:

```bash
python connection_test.py
```

### 4. Launch the RecallOps Dashboard

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## 🎬 60-Second Demo Story

1. **Step 1 — Search Memory (`app.py`):**  
   Search past incident knowledge: *"What failed and what worked when the checkout service had database connection timeouts?"*  
   $\rightarrow$ View recalled historical entries showing that restarting the service failed, while reverting the pool config succeeded.

2. **Step 2 — Memory-Grounded Analysis (`1_Incident_Analysis.py`):**  
   Select **Scenario 1** (Checkout DB Connection Timeouts). Click **Analyze & Compare**.  
   - Inspect the **Memory-Informed Plan** citing `[E3]` and `[E4]`.
   - Switch to the **Before / After Comparison** tab to see how Stateless AI suggests restarting (wasting 20 minutes), while RecallOps warns against it.

3. **Step 3 — Closing the Loop (`2_Record_Outcome.py`):**  
   Use the Quick Demo Helper to load a synthetic post-mortem (e.g. `DEMO-003`).  
   - Review and save the outcome to Hindsight with one click.
   - Immediate verification: future queries instantly incorporate this new experience!

---

## 📁 Repository Structure

```
RecallOps/
├── app.py                      # Main dashboard: Hindsight incident memory search
├── incident_agent.py           # Memory triage engine & prompt guardrails
├── evidence_review.py          # Automated safety reviewer & citation validator
├── connection_test.py          # Hindsight connectivity & bank seeding test
├── groq_test.py                # Groq API connectivity test
├── pages/
│   ├── 1_Incident_Analysis.py  # Incident analysis & Before/After comparison
│   └── 2_Record_Outcome.py     # Post-mortem capture & Hindsight retain loop
├── requirements.txt            # Python dependencies
├── .env.example                # Example configuration template
└── README.md                   # Project documentation & demo guide
```

---

## ⚖️ Hackathon Compliance & Synthetic Data

All data used in demonstrations and test scripts is **fictional and synthetic**. No confidential credentials, production logs, or private data are stored in or queried from Hindsight memory banks.
