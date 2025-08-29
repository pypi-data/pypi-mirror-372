from blazemetrics import Guardrails, guardrails_check

texts = [
    "My email is alice@example.com and my SSN is 123-45-6789.",
    "I will bomb the building.",
    "Totally safe sentence.",
]

# High-level class usage
gr = Guardrails(
    blocklist=["bomb", "terror"],
    regexes=[r"\bSSN\b", r"\b\d{3}-\d{2}-\d{4}\b"],
    case_insensitive=True,
    redact_pii=True,
    safety=True,
)
result = gr.check(texts)
print("Class API:", result)

# Functional API
result2 = guardrails_check(
    texts,
    blocklist=["bomb"],
    regexes=[r"\b\d{3}-\d{2}-\d{4}\b"],
)
print("Func API:", result2) 