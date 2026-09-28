import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY", "").strip()

if not api_key:
    print("Missing GROQ_API_KEY. Check and save your .env file.")
    raise SystemExit(1)

try:
    print("Connecting to Groq...")

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": (
                    "In one short sentence, explain why an incident "
                    "response assistant should remember failed fixes."
                ),
            }
        ],
    )

    answer = response.choices[0].message.content

    if answer:
        print("\nSUCCESS: Groq responded.\n")
        print(answer)
    else:
        print("Groq returned no text.")

except Exception as error:
    print(f"\nGroq test failed: {type(error).__name__}")
    print("Do not share your API key.")