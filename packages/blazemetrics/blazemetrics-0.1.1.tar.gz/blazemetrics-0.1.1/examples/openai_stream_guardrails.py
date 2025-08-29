import os
import sys
from typing import Iterator
from blazemetrics import Guardrails, enforce_stream_sync

# Requires: pip install openai>=1.40
from openai import OpenAI

API_KEY = os.environ.get("OPENAI_API_KEY", "")
if not API_KEY:
    print("Set OPENAI_API_KEY to run this example", file=sys.stderr)
    sys.exit(0)

client = OpenAI(api_key=API_KEY)

prompt = "Write a short paragraph that includes a phone number and SSN in a story."

rails = Guardrails(
    blocklist=["bomb", "terror"],
    regexes=[r"\b\d{3}-\d{2}-\d{4}\b"],
    case_insensitive=True,
    redact_pii=True,
    safety=True,
)

def token_iter() -> Iterator[str]:
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
        temperature=0.0,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content or ""
        if delta:
            yield delta

for out in enforce_stream_sync(token_iter(), rails, every_n_tokens=25, replacement="[BLOCKED]", safety_threshold=0.6):
    print(out, end="", flush=True)
print() 