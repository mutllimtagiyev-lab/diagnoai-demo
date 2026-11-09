# v0.8 optional symptom extraction

The real integration calls Google's Gemini generateContent REST endpoint with
`gemini-3.5-flash-lite`, a JSON schema, enum-restricted labels and a 15-second
timeout. Only the dedicated AI text is sent. Vehicle identity fields and the
ordinary observations field are not included. No new packages are required.
Responses are validated locally with Pydantic, including rejection of extra
fields. Model prose is never rendered. Refusals, malformed responses, timeouts,
rate limits and other failures leave the manual workflow available.

## Enabling after explicit approval

Keep `DIAGNOAI_AI_ENABLED` unset/false during offline use and testing.
The app checks its process environment first, then Streamlit secrets. However,
Streamlit injects root-level `secrets.toml` entries into that environment.
A local root-level `DIAGNOAI_AI_ENABLED = "false"` or empty `GEMINI_API_KEY`
can therefore override the Windows User variables. Keep those two entries
absent from the project's `.streamlit/secrets.toml` when using Windows User
environment variables. The local project is inside OneDrive, so do not place
a real key in that file. Enter the key privately through Windows User
Environment Variables, restart the local Streamlit process, and verify the AI
button's enabled state without submitting a request. `.env` files are ignored
by Git but are **not** loaded automatically. Do not put credentials in
`config.toml`. Cloud deployment requires its own Streamlit secret settings,
provider quota controls, and separate approval. Never paste a key into Codex,
source code, the symptom form or a report.
The user must consent to transmitting the dedicated text and then click the
extraction button. They must separately confirm the displayed categories before
those suggestions populate the form. Uncertain responses cannot be transferred.
Review the provider's data handling terms and account quota before enabling.
The consent instruction asks users to remove identifiers; this is not an
automatic personal-data anonymizer. Do not use real identifying data for a demo.

One extraction click makes at most one request, without automatic retry.
Language switching, confirmation and ordinary diagnostic submission make zero
API calls. Another extraction click is another request and may incur cost.
Published 3.5 Flash-Lite text pricing: $0.30/million input tokens and
$2.50/million output tokens. A hypothetical 1,000 input + 200 output token call
costs $0.00080, excluding any pricing changes or account-specific charges.
This is an estimate, not measured usage. Check current model availability,
pricing and billing limits before the first approved live test.

## Reproducible evaluation and limits

Run `.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v`.
`tests/test_ai_symptoms.py::CASES` defines 10 English and 10 Azerbaijani
descriptions with editorial expected labels. Tests inject mocked HTTP responses
to validate the adapter contract. They do NOT measure Gemini extraction accuracy.
No live AI accuracy, false-positive rate or false-negative rate is claimed.
Unclear and irrelevant examples must return uncertainty and no categories in
the fixtures; actual model behavior still requires an approved live evaluation.

The independent local keyword precheck warns without an API key. Its detected
hazards also enter the existing deterministic priority rules, preventing routine
recommendations from overriding them. It deliberately does not resolve negation.
Known false positive: "There is no smoke." triggers smoke/fire.
Known false negative: "The pedal sinks and the car will not slow down." misses
the keyword check. Spelling, dialect, implied hazards and mixed languages remain
limitations. No match must never be presented as proof of safety.
The normal observations field remains display-only. Users should explicitly
select urgent observations regardless of AI or keyword output.

Manual v0.7 asks users to select categories. v0.8 optionally uses a language
model to propose those same categories from prose, with human confirmation.
The diagnostic rules, OBD meanings and final safety priority remain deterministic.
AI contributes language interpretation only; it supplies no repair decisions.

## Official references

- Model: https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite
- Structured output: https://ai.google.dev/gemini-api/docs/structured-output
- Pricing: https://ai.google.dev/gemini-api/docs/pricing
- Availability/deprecations: https://ai.google.dev/gemini-api/docs/deprecations
- Data terms: https://ai.google.dev/gemini-api/terms
