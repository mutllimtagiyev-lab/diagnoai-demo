# DiagnoAI

## v0.8 release

An optional Gemini symptom-extraction section now proposes existing symptom and
urgent-observation categories from Azerbaijani or English text. Users must confirm
suggestions; existing diagnostic rules remain authoritative. A local conservative
keyword precheck works even with AI disabled. The manual workflow stays offline.
AI is disabled by default in deployments without configured credentials. One
controlled English request succeeded locally; Azerbaijani, urgent and unclear
model behavior remains covered by mocked tests, not live accuracy measurements.
See [AI setup, evaluation and limitations](docs/AI-EVALUATION.md) before enabling.
The v0.7 description below documents the preserved manual workflow.

DiagnoAI v0.7 is a bilingual, offline, rule-based preliminary vehicle guidance
application built with Streamlit and Pydantic. It does not use generative AI,
paid APIs, a database server, or a live vehicle scan. Reports are not confirmed
diagnoses or permission to drive.

## What v0.7 does

Gasoline rough idle or power loss now yields unconfirmed component inspection
candidates, rationale and professional checks. Diesel omits gasoline ignition
components. Hybrid engine subtype remains unknown, so component suggestions
are withheld until verified; EVs retain broad system guidance. The warning-light
follow-up is saved across languages and flashing raises safety priority.
Existing condition selections provide context for professional checks.
`component_guidance.py` contains the curated bilingual extension; tests live in
`tests/test_components.py` and the existing Streamlit interaction suite.

The local library explains ten generic OBD-II codes. Without a code, selected
symptoms produce broad system guidance. Free text is displayed for review but
is not interpreted by the rules. No failed part, probability, repair price,
vehicle-specific specification, or replacement recommendation is inferred.

When a reported safety indicator raises priority to high, stop-and-seek-help
guidance appears before the reported evidence. Routine system and component
inspection suggestions are withheld; OBD meanings remain visible without
routine code checks. The vehicle's own warnings and owner's manual take priority.

## Run on Windows

From the project folder, start the application using the existing environment:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local URL shown in the terminal. Press `Ctrl+C` to stop the server.

If the server is already running, refresh its page. The tested dependencies are pinned in
`requirements.txt`. Restart the server if an imported module change is not picked up.

## Try the interface

1. Azerbaijani is selected initially. Use the language control to switch to English.
2. Select **Diaqnostikaya başla / Start Diagnosis** to jump to the form.
   Fill in manufacturer, model, year and engine type. Select one or more symptoms.
3. Optionally add a condition, frequency, warning-light status and free-text observations. Select the
   **I have an OBD code** mode to enter codes. Displacement and mileage are optional.
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
Unknown codes get no invented definition or causes. A generic warning light or
free text alone yields an explicit insufficient-information message.

All four engine types remain available. Electric vehicles receive generic
combustion-code meanings only, with code causes/checks and priority withheld.
Gasoline rough-idle/power-loss selections may show unconfirmed ignition, fuel,
air and mechanical inspection candidates. Diesel excludes gasoline ignition
parts. Hybrid component guidance is withheld until engine type is verified.
Optional displacement can be blank. Required values cannot contain only whitespace.

## Chevrolet Malibu 2021 demonstration

1. Set manufacturer to `Chevrolet`, model to `Malibu`, year to `2021`, and engine
   type to **Benzin / Gasoline**. Leave displacement/mileage blank if unknown.
2. Select **Engine vibration / rough idle** and **Loss of power**. These are demo inputs, not
   observations of a real vehicle.
3. Keep the default no-code mode and submit. Review the unconfirmed inspection
   candidates, safety priority, missing information and limitations.
4. For the OBD workflow, switch to **I have an OBD code**, enter `P0301` and
   submit again. The standard cylinder-1 misfire meaning remains separate.
5. Switch languages; the vehicle information and report remain available.
6. Try `P0301, P0171, P0999` to show multiple known codes plus an unknown code.
   Select a high-risk observation to see safety guidance take precedence.

See [references and rules](docs/REFERENCES.md) for verified manufacturer links,
page locations, editorial limits, and the exact urgency policy. Online source
links are optional; the report itself works without internet access.

## Project files

- `app.py`: page setup, language selection, and submission flow.
- `homepage.py`, `home_translations.py`: homepage sections and bilingual copy.
- `assets/vehicle-hero.webp`: local hero vehicle image, not a live scan.
- `ui.py`: reusable interface sections and safe summary rendering.
- `translations.py`: Azerbaijani and English interface text.
- `vehicle.py`: Pydantic model and input validation.
- `data/obd_codes.json`: structured, read-only bilingual code library and sources.
- `code_library.py`: schema validation and portable local file loading.
- `diagnostics.py`: comma-separated parser and deterministic report rules.
- `report_ui.py`, `report_translations.py`: bilingual report presentation.
- `symptom_data.py`, `symptom_analysis.py`: curated patterns and deterministic matching.
- `symptom_ui.py`, `symptom_translations.py`: bilingual symptom controls and report.
- `component_guidance.py`: bilingual, engine-aware professional inspection candidates.
- `vehicle_catalog.py`, `vehicle_selection.py`, `data/vehicle_catalog.json`: smart vehicle selection.
- `assets/VEHICLE-HERO-SOURCE.md`: hero image provenance and license notes.
- `docs/REFERENCES.md`: source mapping and documented limitations/rules.
- `styles.css`: colors, spacing, cards, and responsive styling.
- `.streamlit/config.toml`: native dark theme and disabled usage statistics.
- `tests/test_vehicle.py`: validation and translation checks.
- `tests/test_app.py`: interaction checks using Streamlit's built-in AppTest.
- `tests/test_diagnostics.py`: known/unknown/multiple/missing code and offline checks.
- `tests/test_symptoms.py`: symptom, safety, bilingual and combined-workflow checks.
- `tests/test_components.py`: component applicability checks.

Inputs live only in the current Streamlit session and are never written into the
code library. Reloading or closing a session may discard them. When run locally,
processing stays on the local server; when deployed, it runs in that hosted
Streamlit session. There are no AI API requests. Local `.env` files and Streamlit
secrets are ignored by Git.

## Check the code

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

AppTest needs local socket access. If an execution sandbox blocks that access,
run the checks from a normal terminal in this project folder.

## Streamlit Community Cloud readiness

Use `app.py` as the entry point. Commit all application Python modules,
`styles.css`, `assets/vehicle-hero.webp`, `assets/VEHICLE-HERO-SOURCE.md`,
`data/obd_codes.json`, `data/vehicle_catalog.json`, `.streamlit/config.toml`,
`requirements.txt`, documentation and tests. The catalogs and hero image are
required at runtime. Exclude `.venv`, `.env`, secrets, caches, `.local-tmp`,
`assets/diagnostic-car.png` and `assets/vehicle-blueprint.svg`.
The project is tested with Python 3.13; choose a compatible Python runtime in
the deployment settings. No secrets, external services, or OS packages are needed.
The code library path is relative to its module, not a Windows-specific path.
No cloud deployment has been performed as part of this version.

Follow the [official Streamlit deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app)
when ready to deploy.

## Presentation notes

The oil and fuel service is marked coming soon and supplies no specifications.
Contact details are a placeholder. All new text is available in Azerbaijani and
English. The hero uses a local WebP image with no external fonts or runtime
dependencies. Check the homepage at desktop and mobile widths, follow the start
link, and run the Malibu demonstration above. The application uses deterministic
local rules; its guidance requires professional verification.
