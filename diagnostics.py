"""Deterministic code lookup. Symptoms and vehicle names do not infer faults."""

from dataclasses import dataclass
import re

from code_library import CodeDefinition, CodeLibrary, load_library
from vehicle import VehicleIntake


CODE_PATTERN = re.compile(r"[PBCU][0-3][0-9A-F]{3}\Z", re.ASCII)
URGENCY_RANK = {"unassessed": 0, "soon": 1, "prompt": 2}


@dataclass(frozen=True)
class CodeFinding:
    code: str
    definition: CodeDefinition


@dataclass(frozen=True)
class DiagnosticReport:
    vehicle: VehicleIntake
    findings: tuple[CodeFinding, ...]
    unknown_codes: tuple[str, ...]
    invalid_entries: tuple[str, ...]
    urgency: str
    priority_codes: tuple[str, ...]
    applicable: bool
    no_codes: bool
    library: CodeLibrary


def parse_codes(raw: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Comma-separated, case-insensitive tokens; stable order, no duplicates.

    Never extract a plausible code from malformed text or silently correct it.
    Blank tokens, including trailing commas, are ignored.
    """
    tokens = dict.fromkeys(token.strip().upper() for token in raw.split(",") if token.strip())
    valid = tuple(token for token in tokens if CODE_PATTERN.fullmatch(token))
    invalid = tuple(token for token in tokens if not CODE_PATTERN.fullmatch(token))
    return valid, invalid


def build_report(vehicle: VehicleIntake, library: CodeLibrary | None = None) -> DiagnosticReport:
    library = library if library is not None else load_library()
    codes, invalid = parse_codes(vehicle.obd_code)
    findings = tuple(CodeFinding(code, library.codes[code]) for code in codes if code in library.codes)
    unknown = tuple(code for code in codes if code not in library.codes)
    # This first library covers combustion-engine/emissions systems, not BEVs.
    applicable = vehicle.engine_type != "electric"
    urgency = "unassessed"
    priority_codes = ()
    if findings and applicable:
        urgency = max((item.definition.urgency for item in findings), key=URGENCY_RANK.get)
        priority_codes = tuple(item.code for item in findings if item.definition.urgency == urgency)
    return DiagnosticReport(vehicle, findings, unknown, invalid, urgency,
                            priority_codes, applicable, not codes and not invalid, library)
