# DiagnoAI reference and rule notes

Definitions were checked on 2026-11-07 against public manufacturer documents.
The JSON library stores a source ID and a printed-page location for each code.
The report links the corresponding document. Source links are optional to open;
no reference document is fetched while generating a report.

## Definition sources

1. **Volkswagen, 2014 Jetta & GLI Quick Reference Specification Book,
   February 2014**, printed page 22, Ignition System DTC table. Hosted in
   NHTSA's manufacturer communications archive:
   [Manufacturer document](https://static.nhtsa.gov/odi/tsbs/2014/MC-10074001-2280.pdf).
   Used to check the P0300/P0301/P0302 meanings, not to import VW-specific
   monitor thresholds or repair procedures into a Chevrolet report.
2. **Ford, 2024–2025 MY OBD System Operation Summary for Gasoline Engines**,
   revision April 16, 2024:
   [Ford service document](https://www.fordservicecontent.com/Ford_Content/catalog/motorcraft/OBD_Operation_Summary_to_Gasoline_MY_2024_2025.pdf).
   Used for the code-to-monitored-condition mappings below. These are not
   Chevrolet service procedures or proof of applicability to every engine.

| Codes | Definition location (printed pages) |
| --- | --- |
| P0300, P0301, P0302 | Volkswagen p. 22, Ignition System |
| P0171 | Ford pp. 21, 96, Fuel System Monitor |
| P0420 | Ford p. 2, Catalyst Monitor |
| P0101 | Ford p. 121, MAF Sensor Check |
| P0113 | Ford pp. 107, 114, Intake Air Temperature |
| P0128 | Ford p. 71, Thermostat Monitor |
| P0442, P0455 | Ford p. 11, EVAP System Monitor |

P0301 identifies a cylinder-1 misfire condition, not its cause. P0113 describes
a high electrical input, not necessarily high air temperature. P0128 concerns
coolant warm-up below the thermostat regulation target, not an overheating
diagnosis. Code wording varies slightly between manufacturer tables; the app
uses conventional generic names and Azerbaijani translations.

## Safety reference

**Chevrolet, 2021 Malibu Owner's Manual**, printed pp. 87–88,
Malfunction Indicator Lamp (Check Engine Light):
[Chevrolet owner's manual](https://www.chevrolet.com/ownercenter/content/dam/gmownercenter/gmna/dynamic/manuals/2021/chevrolet/malibu/2021-chevrolet-malibu-owners-manual.pdf).
It describes the need for service and the risk of emissions-system damage when
the light flashes. DiagnoAI uses conservative stop-and-seek-assistance guidance
for flashing lights or severe symptoms; this is not a reproduction of the
manual's complete procedure. Other vehicles require their own manuals.

## Editorial content and limits

The Azerbaijani translations, brief explanations, unranked possible-cause lists,
safe observations, and priority rules are DiagnoAI editorial content. They are
not quotations from a repair manual, manufacturer-approved diagnostic trees,
or a validated urgency assessment. The cited pages support code definitions;
they do not substantiate a particular cause or repair for the user's vehicle.
Professional testing is required before a part is condemned or replaced.

The OBD rules deliberately do not use free-text symptoms, make, model, year,
displacement, or mileage to infer faults. Those details are preserved for
review. No probabilities, confidence scores, repair prices, or causal links
between codes are fabricated.

## Reproducible priority rules

- P0300, P0301, P0302: **prompt professional assessment**, due to the potential
  consequences of continued misfire. Actual severity cannot be established
  from a stored code alone.
- The other seven supported codes: **service soon**. This does not declare
  that driving is safe. Each entry explains the relevant monitored condition.
- Multiple recognized codes: the highest entry priority wins; the report
  identifies which codes determined it. Causes remain attached to their codes.
- Unknown/malformed codes: no definition or causes are generated. Mixed reports
  retain the known-code priority and explicitly leave the rest unassessed.
- Missing codes: the OBD code lookup remains **not assessed**. The separate
  v0.6 symptom module can provide broad guidance from explicit selections.
- Electric vehicles: generic definitions only; combustion-system causes,
  checks, and priority are withheld pending vehicle/module verification.
- Safety warnings are always shown. The v0.6 symptom module uses explicit
  red-flag selections; it does not automatically recognize them in free text.

## v0.6 symptom guidance and safety sources

The local `symptom_data.py` patterns are DiagnoAI editorial prompts. They map
explicit selections to broad systems for a qualified technician to inspect;
the cited sources do **not** validate a particular cause, component or repair
for an individual vehicle. The app does not interpret the user's free text.

- [2021 Chevrolet Malibu Owner's Manual](https://www.chevrolet.com/ownercenter/content/dam/gmownercenter/gmna/dynamic/manuals/2021/chevrolet/malibu/2021-chevrolet-malibu-owners-manual.pdf),
  especially printed pp. 87–88 (flashing check-engine light), brake and
  steering warnings, and the engine-overheating section. These support the
  conservative warning to seek service when a safety-relevant indication is
  present. The owner's manual for the user's own vehicle takes precedence.
- [NHTSA, Driver Assistance Technologies](https://www.nhtsa.gov/vehicle-safety/driver-assistance-technologies):
  braking and steering are central to maintaining vehicle control. This is
  context for treating reported control problems as high priority; it is not
  a diagnostic procedure or proof of fault.
- [Chevrolet, Diagnostic Alerts](https://www.chevrolet.com/support/vehicle/maintenance/repair-and-service/diagnostic-alerts):
  distinguishes monitored engine, transmission, anti-lock braking and battery
  areas. It supports broad system grouping, not vehicle-specific fitment.

The urgency labels are conservative editorial rules, **not** a validated
triage scale. Brake/steering concerns, reported unusual exhaust smoke and
explicit severe overheating, fire/smoke, fuel leakage, severe power loss or a
flashing engine light trigger the high-priority message. Other matched
patterns suggest professional inspection soon. Generic warning lights alone
do not identify a system. No rule suggests driving to reproduce a fault,
opening fuel or hot cooling systems, high-voltage work or replacing a part.

## Updating the library

### v0.7 component inspection candidates

Reviewed 2026-11-08. These are unranked editorial inspection candidates, not
manufacturer diagnostic trees or proof of a failed part. No model-specific
fitment is inferred. Hybrid fuel type is unspecified, so component guidance
is withheld pending clarification; electric vehicles receive system guidance.

- [NGK/Niterra ignition coil guidance](https://www.ngkntk.com/nordic/newsroom/blog/nordic/you-asked-google-ngk-spark-plug-answers-part-4-ignition-coils-leads-caps/)
  supports ignition as one possible contributor to rough idle and reduced power.
- [DENSO spark plug troubleshooting](https://www.denso.com/global/en/products-and-services/automotive-service-parts-and-accessories/plug/basic/diagnosis/)
  describes ignition-related running and load symptoms.
- [Delphi diesel injector technical leaflet](https://www.delphiautoparts.com/docs/default-source/products-technologies/d_explore-diesel-reman_flyer_a4_en.pdf?sfvrsn=ce07aa04_1)
  discusses poor running and power loss associated with injector conditions.

Air/sensor and mechanical checks are broad editorial inspection categories,
not a claim that any listed component causes the user's complaint. A technician
must select tests from the actual vehicle's service information. Condition
answers influence the requested inspection context; a flashing warning-light
answer independently raises safety priority. Free text remains uninterpreted.

Edit `data/obd_codes.json`, supply both `az` and `en` text for every field,
verify the source URL and printed-page location, update `reviewed_on`, and run
the tests. Keep checks observational and leave hazardous work to professionals.
Do not add code definitions by guessing from a code's number.
