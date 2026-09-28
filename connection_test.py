import os

from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

api_key = os.getenv("HINDSIGHT_API_KEY", "").strip()
api_url = os.getenv("HINDSIGHT_API_URL", "").strip()
bank_id = os.getenv("HINDSIGHT_BANK_ID", "").strip()

if not all([api_key, api_url, bank_id]):
    print("Missing configuration. Check and save your .env file.")
    raise SystemExit(1)

stage = "connecting"

try:
    with Hindsight(
        base_url=api_url,
        api_key=api_key,
        timeout=120.0,
    ) as client:
        stage = "creating the memory bank"
        print("1. Setting up the RecallOps demo bank...")

        client.create_bank(
            bank_id=bank_id,
            name="RecallOps Demo",
        )

        stage = "saving the example incident"
        print("2. Saving a synthetic incident...")

        client.retain(
            bank_id=bank_id,
            document_id="recallops-connection-test",
            content=(
                "SYNTHETIC DEMO INCIDENT TEST-001: "
                "The checkout service had database connection timeouts "
                "after a connection pool configuration change. "
                "Restarting the service did not fix the issue. "
                "Reverting the pool configuration resolved the issue. "
                "This is demonstration data, not a real incident."
            ),
            retain_async=False,
        )

        stage = "retrieving memory"
        print("3. Searching for the saved incident...")

        response = client.recall(
            bank_id=bank_id,
            query="In TEST-001, what failed and what resolved the issue?",
            max_tokens=1024,
        )

        if response.results:
            print("\nSUCCESS: Hindsight returned memory.")
            for memory in response.results:
                print("\n", memory.text)
        else:
            print(
                "\nThe save request completed, but no memory was retrieved. "
                "Check the demo bank in your Hindsight dashboard."
            )

except Exception as error:
    print(f"\nFAILED while {stage}.")
    print(f"Error type: {type(error).__name__}")
    print("Do not share your API key when reporting this error.")