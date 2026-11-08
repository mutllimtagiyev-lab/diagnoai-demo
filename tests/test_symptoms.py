"""Safety and integration checks for explicit, offline symptom rules."""

from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest

from diagnostics import build_report
from symptom_analysis import assess_symptoms
from symptom_data import CONDITIONS, GROUPS, RED_FLAGS, RULES
from translations import TEXT, translate
from vehicle import validate_vehicle


def intake(**changes):
    values = dict(manufacturer="Chevrolet", model="Malibu", year="2021",
                  engine_type="gasoline", symptoms="", obd_code="",
                  symptom_ids=("rough_idle",), red_flags=())
    values.update(changes)
    vehicle, errors = validate_vehicle(values)
    assert not errors, errors
    return vehicle


class SymptomLogicTests(unittest.TestCase):
    def test_symptom_only_multiple_and_no_code(self):
        result = assess_symptoms(intake(symptom_ids=("rough_idle", "hard_start", "battery")))
        self.assertEqual(result.urgency, "soon")
        self.assertEqual({r["id"] for r in result.findings}, {"combustion_operation", "electrical"})
        self.assertFalse(result.insufficient)

    def test_combined_code_keeps_standard_code_meaning(self):
        vehicle = intake(obd_code="P0301", diagnostic_mode="have_code_mode")
        self.assertEqual(build_report(vehicle).findings[0].code, "P0301")
        self.assertEqual(len(assess_symptoms(vehicle).findings), 1)

    def test_free_text_is_not_interpreted(self):
        vehicle = intake(symptom_ids=(), symptoms="brake failure and fire")
        result = assess_symptoms(vehicle)
        self.assertTrue(result.insufficient)
        self.assertEqual(result.urgency, "unassessed")

    def test_generic_warning_lights_are_insufficient(self):
        result = assess_symptoms(intake(symptom_ids=("warning_lights",)))
        self.assertTrue(result.insufficient)

    def test_high_risk_flags_and_control_symptoms(self):
        for flag in RED_FLAGS:
            with self.subTest(flag=flag):
                result = assess_symptoms(intake(symptom_ids=(), red_flags=(flag,)))
                self.assertEqual(result.urgency, "high")
        for symptom in ("brakes", "steering", "exhaust_smoke"):
            with self.subTest(symptom=symptom):
                self.assertEqual(assess_symptoms(intake(symptom_ids=(symptom,))).urgency, "high")

    def test_electric_withholds_combustion_pattern(self):
        result = assess_symptoms(intake(engine_type="electric", symptom_ids=("rough_idle",)))
        self.assertTrue(result.insufficient)
        self.assertTrue(result.withheld_for_ev)

    def test_bilingual_rule_and_control_coverage(self):
        keys = {s for group in GROUPS.values() for s in group} | set(CONDITIONS) | set(RED_FLAGS)
        for language in ("az", "en"):
            for key in keys:
                self.assertTrue(translate(language, key))
            for rule in RULES:
                self.assertEqual(len(rule[language]), 7)
                self.assertTrue(all(rule[language]))
        self.assertEqual(set(TEXT["az"]), set(TEXT["en"]))

    def test_unknown_structured_values_rejected(self):
        values = intake().model_dump()
        values["symptom_ids"] = ("invented_fault",)
        self.assertEqual(validate_vehicle(values)[1], ["invalid_symptom_selection"])


class SymptomAppTests(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=15).run()
        self.assertFalse(self.app.exception)

    def _vehicle(self):
        for field, value in (("vehicle_make", "Chevrolet"), ("vehicle_model", "Malibu"),
                             ("vehicle_year", "2021"), ("engine_type", "gasoline")):
            self.app.selectbox(key=f"{field}_az").set_value(value).run()

    def test_symptom_report_switch_and_invalidation(self):
        self._vehicle()
        self.app.multiselect(key="symptoms_powertrain_az").set_value(["rough_idle", "hard_start"]).run()
        self.app.button(key="analyze").click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual(len(self.app.success), 1)
        self.assertIn("Əlamətlərə əsaslanan ilkin bələdçi", [h.value for h in self.app.header])
        self.app.radio(key="language").set_value("en").run()
        self.assertEqual(self.app.multiselect(key="symptoms_powertrain_en").value, ["rough_idle", "hard_start"])
        self.assertIn("Preliminary symptom guidance", [h.value for h in self.app.header])
        self.app.multiselect(key="symptoms_chassis_en").set_value(["brakes"]).run()
        self.assertEqual(len(self.app.success), 0)
        self.app.button(key="analyze").click().run()
        self.assertEqual(assess_symptoms(self.app.session_state["submitted_vehicle"]).urgency, "high")

    def test_combined_code_workflow_and_make_selector(self):
        self._vehicle()
        self.app.multiselect(key="symptoms_powertrain_az").set_value(["rough_idle"]).run()
        self.app.radio(key="mode_az").set_value("have_code_mode").run()
        self.app.text_input(key="obd_code").set_value("P0301").run()
        self.app.button(key="analyze").click().run()
        self.assertFalse(self.app.exception)
        self.assertTrue(any("İlkin OBD-II hesabatı" in e.value for e in self.app.markdown))
        self.assertIn("Əlamətlərə əsaslanan ilkin bələdçi", [h.value for h in self.app.header])
        self.assertEqual(self.app.session_state["submitted_vehicle"].model, "Malibu")

    def test_warning_answer_survives_language_and_invalidates_report(self):
        self._vehicle()
        self.app.multiselect(key="symptoms_powertrain_az").set_value(["rough_idle", "power_loss"]).run()
        self.app.selectbox(key="warning_light_az").set_value("flashing").run()
        self.app.button(key="analyze").click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual(assess_symptoms(self.app.session_state["submitted_vehicle"]).urgency, "high")
        self.app.radio(key="language").set_value("en").run()
        self.assertEqual(self.app.selectbox(key="warning_light_en").value, "flashing")
        self.assertFalse(any("Spark plugs and ignition coils" in e.value for e in self.app.markdown))
        self.assertTrue(any(TEXT["en"]["urgent_deferred"] == e.value for e in self.app.info))
        self.app.selectbox(key="warning_light_en").set_value("steady").run()
        self.assertEqual(len(self.app.success), 0)

    def test_urgent_safety_precedes_and_withholds_routine_guidance(self):
        self._vehicle()
        self.app.multiselect(key="symptoms_powertrain_az").set_value(["rough_idle", "power_loss"]).run()
        self.app.multiselect(key="red_flags_az").set_value(["fuel_leak"]).run()
        self.app.button(key="analyze").click().run()
        self.assertFalse(self.app.exception)
        self.assertIn(TEXT["az"]["priority_high"], [e.value for e in self.app.error])
        self.assertIn(TEXT["az"]["urgent_deferred"], [e.value for e in self.app.info])
        self.assertFalse(any("Alışdırma şamları" in e.value for e in self.app.markdown))
        self.app.radio(key="language").set_value("en").run()
        self.assertIn(TEXT["en"]["priority_high"], [e.value for e in self.app.error])
        self.assertFalse(any("Spark plugs and ignition coils" in e.value for e in self.app.markdown))

    def test_urgent_combined_code_keeps_meaning_without_routine_checks(self):
        self._vehicle()
        self.app.multiselect(key="symptoms_powertrain_az").set_value(["rough_idle"]).run()
        self.app.radio(key="mode_az").set_value("have_code_mode").run()
        self.app.text_input(key="obd_code").set_value("P0301").run()
        self.app.selectbox(key="warning_light_az").set_value("flashing").run()
        self.app.button(key="analyze").click().run()
        self.assertFalse(self.app.exception)
        html = " ".join(e.value for e in self.app.markdown if "data:image" not in e.value)
        self.assertIn("P0301", html)
        self.assertIn("1-ci silindrdə yanma pozuntusu", html)
        self.assertNotIn(TEXT["az"]["checks_heading"], html)
        self.assertNotIn(TEXT["az"]["urgency_heading"], html)


if __name__ == "__main__":
    unittest.main()
