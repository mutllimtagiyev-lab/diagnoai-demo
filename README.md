# DiagnoAI

A bilingual, offline OBD-II reference assistant built with Streamlit and Pydantic.
Version 0.3 preserves the vehicle intake interface and adds preliminary reports
from a bundled JSON code library and deterministic Python rules. It does not use
generative AI, make paid API calls, or require a database server.

## Run on Windows

From the project folder, start the application using the existing environment:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local URL shown in the terminal. Press `Ctrl+C` to stop the server.

If the server is already running, refresh its page. No new packages are needed
for version 0.3. The already installed, tested dependency versions are pinned in
`requirements.txt`. Restart the server if an imported module change is not picked up.

## Try the interface

1. Azerbaijani is selected initially. Use the language control to switch to English.
2. Fill in manufacturer, model, year, engine type, and the symptom description.
3. Optionally add displacement in liters, mileage in kilometers, and OBD-II codes.
   Use a decimal point or comma for displacement and whole digits for mileage.
4. Separate codes with commas, for example `P0301, P0171`. Click
   **Avtomobili təhlil et** / **Analyze Vehicle** for the summary and preliminary report.
5. Try submitting empty fields or an invalid year to see translated validation messages.
6. Switch languages to check translated labels and summaries. Editing an input
   clears the previous summary; submit again to review the updated information.

The local library contains **P0300, P0301, P0302, P0171, P0420, P0101, P0113,
P0128, P0442, P0455**. It provides bilingual meanings, explanations, unranked
possible causes, safe observations, warnings, and definition references.
Codes are trimmed, uppercased, and deduplicated in first-seen order. Blank comma
segments are ignored. Malformed tokens are reported without guessing a code.
Unknown codes get no invented definition or causes. With no code, symptom-only
analysis is explicitly unavailable. Symptoms are recorded but never interpreted.

All four engine types remain available. For electric vehicles these combustion
references are shown as definitions only; causes/checks and urgency are withheld.
Optional displacement can be blank. Required values cannot contain only whitespace.

## Chevrolet Malibu 2021 demonstration

1. Set manufacturer to `Chevrolet`, model to `Malibu`, year to `2021`, and engine
   type to **Benzin / Gasoline**. Leave displacement/mileage blank if unknown.
2. For a sample symptom, enter `Boş gedişdə titrəmə müşahidə olunur.` or
   `Rough idle.` These are demo inputs, not observations of a real vehicle.
3. Enter `P0301` and submit.
4. Expect **Cylinder 1 Misfire Detected / 1-ci silindrdə yanma pozuntusu aşkar
   edilib**, possible causes, safe next checks, a prompt-assessment priority with
   its reason, and limitations. No particular component is declared faulty.
5. Switch languages; the vehicle information and report remain available.
6. Try `P0301, P0171, P0999` to show multiple known codes plus an unknown code.
   Clear the code field to demonstrate the symptom-only limitation.

See [references and rules](docs/REFERENCES.md) for verified manufacturer links,
page locations, editorial limits, and the exact urgency policy. Online source
links are optional; the report itself works without internet access.

## Project files

- `app.py`: page setup, language selection, and submission flow.
- `ui.py`: reusable interface sections and safe summary rendering.
- `translations.py`: Azerbaijani and English interface text.
- `vehicle.py`: Pydantic model and input validation.
- `data/obd_codes.json`: structured, read-only bilingual code library and sources.
- `code_library.py`: schema validation and portable local file loading.
- `diagnostics.py`: comma-separated parser and deterministic report rules.
- `report_ui.py`, `report_translations.py`: bilingual report presentation.
- `docs/REFERENCES.md`: source mapping and documented limitations/rules.
- `styles.css`: colors, spacing, cards, and responsive styling.
- `.streamlit/config.toml`: native dark theme and disabled usage statistics.
- `tests/test_vehicle.py`: validation and translation checks.
- `tests/test_app.py`: interaction checks using Streamlit's built-in AppTest.
- `tests/test_diagnostics.py`: known/unknown/multiple/missing code and offline checks.

Inputs live only in the current Streamlit session and are never written into the
code library. Reloading or closing a session may discard them. When run locally,
processing stays on the local server; when deployed, it runs in that hosted
Streamlit session. There are no AI API requests. Local `.env` files and Streamlit
secrets are ignored by Git.

## Check the code

```powershell
.\.venv\Scripts\python.exe -m py_compile app.py ui.py translations.py vehicle.py code_library.py diagnostics.py report_ui.py report_translations.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

AppTest needs local socket access. If an execution sandbox blocks that access,
run the checks from a normal terminal in this project folder.

## Streamlit Community Cloud readiness

Use `app.py` as the entry point. Include the Python files, `styles.css`,
`data/obd_codes.json`, `.streamlit/config.toml`, and `requirements.txt` in the
repository. Exclude `.venv`, `.env`, secrets, caches, and `.local-tmp`.
The project is tested with Python 3.13; choose a compatible Python runtime in
the deployment settings. No secrets, external services, or OS packages are needed.
The code library path is relative to its module, not a Windows-specific path.
No cloud deployment has been performed as part of this version.

Follow the [official Streamlit deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app)
when ready to deploy.
