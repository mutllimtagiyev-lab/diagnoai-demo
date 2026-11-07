"""Code coverage, parser edge cases, offline behavior, and report rules."""

import unittest
from unittest.mock import patch

from code_library import load_library
from diagnostics import build_report, parse_codes
from report_translations import REPORT_TEXT
from vehicle import VehicleIntake


EXPECTED_CODES = {"P0300", "P0301", "P0302", "P0171", "P0420", "P0101", "P0113", "P0128", "P0442", "P0455"}


def demo_vehicle(codes="P0301", **overrides):
    values = dict(manufacturer="Chevrolet", model="Malibu", year=2021,
                  engine_type="gasoline", symptoms="Rough idle.", obd_code=codes)
    values.update(overrides)
    return VehicleIntake(**values)


class DiagnosticTests(unittest.TestCase):
    def test_exact_code_coverage(self):
        self.assertEqual(set(load_library().codes), EXPECTED_CODES)

    def test_every_known_code_generates_a_finding(self):
        for code in EXPECTED_CODES:
            with self.subTest(code=code):
                report = build_report(demo_vehicle(code))
                self.assertEqual([f.code for f in report.findings], [code])
                self.assertFalse(report.unknown_codes)
                self.assertNotEqual(report.urgency, "unassessed")

    def test_cylinder_definitions_are_not_interchanged(self):
        library = load_library()
        self.assertEqual(library.codes["P0301"].meaning.en, "Cylinder 1 Misfire Detected")
        self.assertEqual(library.codes["P0302"].meaning.en, "Cylinder 2 Misfire Detected")
        self.assertIn("Multiple", library.codes["P0300"].meaning.en)

    def test_unknown_code_has_no_invented_finding(self):
        report = build_report(demo_vehicle("P0999"))
        self.assertEqual(report.unknown_codes, ("P0999",))
        self.assertFalse(report.findings)
        self.assertEqual(report.urgency, "unassessed")

    def test_missing_codes_do_not_analyze_even_alarming_symptom_text(self):
        for raw in ("", " ", ", ,"):
            report = build_report(demo_vehicle(raw, symptoms="Flashing light, smoke, overheating"))
            self.assertTrue(report.no_codes)
            self.assertFalse(report.findings)
            self.assertEqual(report.urgency, "unassessed")

    def test_multiple_codes_case_whitespace_and_duplicates(self):
        report = build_report(demo_vehicle(" p0420, p0301, P0171, P0301, "))
        self.assertEqual([f.code for f in report.findings], ["P0420", "P0301", "P0171"])
        self.assertEqual(report.urgency, "prompt")
        self.assertEqual(report.priority_codes, ("P0301",))

    def test_unknown_codes_do_not_reduce_known_priority(self):
        report = build_report(demo_vehicle("P0301,P0999"))
        self.assertEqual(report.urgency, "prompt")
        self.assertEqual(report.unknown_codes, ("P0999",))

    def test_malformed_entries_are_not_silently_repaired(self):
        valid, invalid = parse_codes("P0301 P0171, P030, P9999, hello, P0301;P0171, P0301")
        self.assertEqual(valid, ("P0301",))
        self.assertEqual(len(invalid), 5)
        self.assertIn("P0301 P0171", invalid)

    def test_electric_vehicle_is_not_given_combustion_priority(self):
        report = build_report(demo_vehicle(engine_type="electric"))
        self.assertFalse(report.applicable)
        self.assertEqual(report.urgency, "unassessed")
        self.assertTrue(report.findings)  # Generic meaning remains available.

    def test_make_and_symptoms_do_not_infer_extra_faults(self):
        first = build_report(demo_vehicle())
        second = build_report(demo_vehicle(manufacturer="Another make", symptoms="Different symptoms"))
        self.assertEqual(first.findings, second.findings)
        self.assertEqual(first.urgency, second.urgency)

    def test_report_is_deterministic_and_keeps_vehicle_data(self):
        vehicle = demo_vehicle(displacement=1.5, mileage=85000)
        self.assertEqual(build_report(vehicle), build_report(vehicle))
        self.assertEqual(build_report(vehicle).vehicle, vehicle)

    def test_localized_library_and_valid_references(self):
        library = load_library()
        for code, definition in library.codes.items():
            texts = [definition.meaning, definition.explanation, definition.urgency_reason,
                     *definition.possible_causes, *definition.safe_checks, *definition.warnings]
            for text in texts:
                self.assertTrue(text.az.strip(), code)
                self.assertTrue(text.en.strip(), code)
                self.assertNotEqual(text.az, text.en, code)
            for reference in definition.references:
                self.assertIn(reference.source, library.sources)
                self.assertTrue(str(library.sources[reference.source].url).startswith("https://"))
        self.assertEqual(set(REPORT_TEXT["az"]), set(REPORT_TEXT["en"]))

    def test_report_generation_needs_no_network(self):
        with patch("socket.socket", side_effect=AssertionError("Network use forbidden")):
            report = build_report(demo_vehicle("P0301,P0171"))
        self.assertEqual(len(report.findings), 2)


if __name__ == "__main__":
    unittest.main()
