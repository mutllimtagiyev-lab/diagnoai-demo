"""Deterministic symptom guidance, independent of the OBD code library."""

from dataclasses import dataclass

from symptom_data import CONDITIONS, GROUPS, RED_FLAGS, RULES
from vehicle import VehicleIntake

SYMPTOM_IDS = frozenset(item for group in GROUPS.values() for item in group)
HIGH_RISK_SYMPTOMS = frozenset(("brakes", "steering", "exhaust_smoke"))


@dataclass(frozen=True)
class SymptomAssessment:
    findings: tuple[dict, ...]
    urgency: str
    safety_indicators: tuple[str, ...]
    insufficient: bool
    withheld_for_ev: bool


def assess_symptoms(vehicle: VehicleIntake) -> SymptomAssessment:
    """Match explicit selections only; never parse prose or infer a failed part."""
    selected = set(vehicle.symptom_ids) & SYMPTOM_IDS
    flags = tuple(flag for flag in vehicle.red_flags if flag in RED_FLAGS)
    if vehicle.warning_light == 'flashing':
        flags += ('flashing_light',)
    safety = tuple(dict.fromkeys((*flags, *(s for s in selected if s in HIGH_RISK_SYMPTOMS))))
    candidates = tuple(rule for rule in RULES if selected.intersection(rule["symptoms"]))
    withheld = vehicle.engine_type == "electric" and any(rule["combustion_only"] for rule in candidates)
    findings = tuple(rule for rule in candidates if not (vehicle.engine_type == "electric" and rule["combustion_only"]))
    urgency = "high" if safety else "soon" if findings else "unassessed"
    return SymptomAssessment(findings, urgency, safety, not bool(findings), withheld)


def valid_symptom_values(vehicle: VehicleIntake) -> bool:
    return (set(vehicle.symptom_ids) <= SYMPTOM_IDS
            and set(vehicle.red_flags) <= set(RED_FLAGS)
            and vehicle.issue_condition in ("", *CONDITIONS))
