import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from groq import Groq
from hindsight_client import Hindsight

load_dotenv()

SYSTEM_PROMPT = """
You are RecallOps, an incident-response assistant.

Analyze the current incident using the supplied historical evidence.

CRITICAL RULES TO PASS SAFETY REVIEW:
1. INCIDENT SUMMARY:
   - Summarize ONLY the symptoms and conditions explicitly described in the CURRENT INCIDENT.
   - NEVER state or imply that any fix (such as a restart or rollback) has already been attempted in the current incident.
2. SERVICE RELEVANCE & CITATIONS:
   - ONLY cite historical evidence that directly pertains to the specific service and symptoms in the CURRENT INCIDENT.
   - If the current incident is about the checkout service, completely IGNORE any evidence regarding the notifications worker, credential rotations, or other services. Do NOT cite them or create investigation steps for them.
   - Cite historical claims using ASCII labels such as [E1]. NEVER use Unicode brackets like 【...】 or footnote markers.
3. PREVIOUSLY FAILED APPROACHES:
   - State clearly that the failed action occurred in a PAST incident (e.g. "In past incident [E4], restarting the checkout service failed to resolve the timeouts.").
   - Explicitly note that this action has NOT been attempted in the current incident, but historical evidence indicates it does not resolve configuration issues.
4. INVESTIGATION PLAN (READ-ONLY SAFETY):
   - Every single step in the investigation plan MUST be explicitly prefixed with "Read-only: " and describe safe, non-disruptive inspection.
   - Do NOT propose state changes or speculative checks for unrelated services.
5. REMEDIATION (REQUIRES APPROVAL):
   - Recommend actions (e.g. configuration revert [E3]) only with explicit prerequisites, rollback steps, verification, and human approval.
   - Never claim to execute a fix.

Use these exact headings:
## Incident summary
## Likely causes and supporting evidence
## Previously failed approaches
## Prioritized investigation plan
## Possible remediation — requires approval
## Missing information

Keep the response concise, factual, and strictly grounded.
"""



def analyze_incident(description):
    if not description.strip():
        raise ValueError("Enter an incident description.")

    required = [
        "HINDSIGHT_API_URL",
        "HINDSIGHT_API_KEY",
        "HINDSIGHT_BANK_ID",
        "GROQ_API_KEY",
    ]

    missing = [
        name for name in required
        if not os.getenv(name, "").strip()
    ]

    if missing:
        raise ValueError(
            "Missing configuration: " + ", ".join(missing)
        )

    with Hindsight(
        base_url=os.environ["HINDSIGHT_API_URL"],
        api_key=os.environ["HINDSIGHT_API_KEY"],
        timeout=120.0,
    ) as memory_client:
        recalled = memory_client.recall(
            bank_id=os.environ["HINDSIGHT_BANK_ID"],
            query=description.strip(),
            max_tokens=2048,
        )

    evidence = [
        {"label": f"E{index}", "text": memory.text}
        for index, memory in enumerate(
            recalled.results, start=1
        )
    ]

    evidence_text = "\n\n".join(
        f"[{item['label']}] {item['text']}"
        for item in evidence
    )

    if not evidence_text:
        evidence_text = "No historical evidence was retrieved."

    llm_client = Groq(
        api_key=os.environ["GROQ_API_KEY"]
    )

    response = llm_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        temperature=0.0,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    "CURRENT INCIDENT:\n"
                    + description.strip()
                    + "\n\nHISTORICAL EVIDENCE:\n"
                    + evidence_text
                ),
            },
        ],
    )

    analysis = response.choices[0].message.content

    if not analysis:
        raise RuntimeError("Groq returned no analysis text.")
    from evidence_review import review_draft

    analysis = review_draft(
        client=llm_client,
        description=description.strip(),
        evidence=evidence,
        draft=analysis,
        rules=SYSTEM_PROMPT,
    )

    return {
        "analysis": analysis,
        "evidence": evidence,
    }


def analyze_without_memory(description: str) -> str:
    """Analyze an incident using Groq baseline WITHOUT Hindsight memory.

    Provides the comparison baseline to demonstrate how generic models
    suggest ungrounded or repeatedly failed troubleshooting steps.
    """
    if not description.strip():
        raise ValueError("Enter an incident description.")

    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise ValueError("Missing GROQ_API_KEY in environment.")

    llm_client = Groq(api_key=api_key)
    response = llm_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        temperature=0.0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a standard AI DevOps assistant helping an on-call engineer.\n"
                    "You DO NOT have access to historical incident memories, post-mortems, or past failure logs.\n"
                    "Provide a general incident triage and investigation plan based on standard industry practices.\n"
                    "Structure your response with: Incident Summary, Hypotheses, Immediate Actions (e.g. restarts, scaling, logging), and Verification."
                ),
            },
            {
                "role": "user",
                "content": f"CURRENT INCIDENT:\n{description.strip()}",
            },
        ],
    )
    return response.choices[0].message.content or ""



if __name__ == "__main__":
    demo_incident = (
        "SYNTHETIC DEMO: Checkout requests are experiencing "
        "database connection timeouts after a connection pool "
        "configuration change. The cause has not been confirmed. "
        "What should we investigate before making changes?"
    )

    try:
        print("Retrieving memories and analyzing the demo incident...")

        result = analyze_incident(demo_incident)

        print("\nRETRIEVED EVIDENCE")
        for item in result["evidence"]:
            print(f"\n[{item['label']}] {item['text']}")

        print("\nAI INVESTIGATION PLAN\n")
        print(result["analysis"])

    except Exception as error:
        print(f"\nAnalysis failed: {type(error).__name__}")
        print("Do not share API keys when reporting this error.")