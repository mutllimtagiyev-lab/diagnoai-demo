"""Exercise real Streamlit widget state, validation, and summary output."""

from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest

from translations import TEXT
from vehicle_catalog import CATALOG, OTHER
from vehicle_selection import initialize_selection, year_options
from unittest.mock import patch


APP_PATH = str(Path(__file__).resolve().parents[1] / "app.py")


class AppTests(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(APP_PATH, default_timeout=15).run()
        self.assertFalse(self.app.exception)

    def choose(self, field, value):
        language = self.app.radio(key="language").value
        self.app.selectbox(key=f"{field}_{language}").set_value(value).run()

    def fill_vehicle(self):
        self.choose("vehicle_make", "Toyota")
        self.choose("vehicle_model", "Corolla")
        self.choose("vehicle_year", "2020")
        self.choose("engine_type", "hybrid")
        self.app.text_area(key="symptoms").set_value("Vibration when idling.")
        self.app.run()

    def code_mode(self):
        language = self.app.radio(key="language").value
        self.app.radio(key=f"mode_{language}").set_value("have_code_mode").run()

    def test_default_language_and_translated_errors(self):
        self.assertEqual(self.app.radio(key="language").value, "az")
        self.app.button(key="analyze").click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual(len(self.app.error), 6)
        self.assertEqual(self.app.error[1].value, TEXT["az"]["required_manufacturer"])
        self.app.radio(key="language").set_value("en").run()
        self.assertEqual(self.app.error[1].value, TEXT["en"]["required_manufacturer"])
        self.assertEqual(self.app.button(key="analyze").label, "Analyze Vehicle")

    def test_draft_and_summary_survive_language_switch(self):
        self.fill_vehicle()
        self.app.radio(key="language").set_value("en").run()
        self.assertEqual(self.app.selectbox(key="vehicle_make_en").value, "Toyota")
        self.assertEqual(self.app.session_state["selected_engine"], "hybrid")
        self.assertEqual(self.app.selectbox(key="engine_type_en").key, "engine_type_en")
        self.app.button(key="analyze").click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual(len(self.app.error), 0)
        self.assertEqual(len(self.app.success), 1)
        html = " ".join(element.value for element in self.app.markdown)
        self.assertIn("Hybrid", html)
        self.assertIn("Not provided", html)
        self.app.radio(key="language").set_value("az").run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.session_state["selected_engine"], "hybrid")
        self.assertEqual(self.app.selectbox(key="engine_type_az").key, "engine_type_az")
        self.assertEqual(len(self.app.success), 1)
        html = " ".join(element.value for element in self.app.markdown)
        self.assertIn("Hibrid", html)
        self.assertIn("Daxil edilməyib", html)
        self.choose("vehicle_model", "Yaris")
        self.assertEqual(len(self.app.success), 0)

    def test_summary_escapes_markup_and_keeps_zero_mileage(self):
        self.fill_vehicle()
        self.choose("vehicle_make", OTHER)
        self.app.text_input(key="manual_make_az").set_value("<b>Toyota</b>").run()
        self.choose("vehicle_model", OTHER)
        self.app.text_input(key="manual_model_az").set_value("Corolla").run()
        self.app.text_input(key="mileage").set_value("0")
        self.app.text_area(key="symptoms").set_value("<script>alert(1)</script>\nSecond line")
        self.app.button(key="analyze").click().run()
        self.assertFalse(self.app.exception)
        html = " ".join(element.value for element in self.app.markdown)
        self.assertIn("&lt;b&gt;Toyota&lt;/b&gt;", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>", html)
        self.assertIn("0 km", html)

    def test_bilingual_malibu_report(self):
        self.fill_vehicle()
        self.code_mode()
        self.choose("vehicle_make", "Chevrolet")
        self.choose("vehicle_model", "Malibu")
        self.choose("vehicle_year", "2021")
        self.app.text_input(key="obd_code").set_value("P0301")
        self.app.button(key="analyze").click().run()
        self.assertFalse(self.app.exception)
        html = " ".join(e.value for e in self.app.markdown)
        self.assertIn("Malibu", html)
        self.assertIn("1-ci silindrdə yanma pozuntusu", html)
        self.assertIn(TEXT["az"]["causes_heading"], html)
        self.app.radio(key="language").set_value("en").run()
        html = " ".join(e.value for e in self.app.markdown)
        self.assertIn("Cylinder 1 Misfire Detected", html)
        self.assertIn(TEXT["en"]["limitations_heading"], html)
        self.assertTrue(any(TEXT["en"]["urgency_prompt"] == e.value for e in self.app.warning))
        self.app.text_input(key="obd_code").set_value("P0420").run()
        self.assertNotIn("Preliminary OBD-II report", " ".join(e.value for e in self.app.markdown))

    def test_missing_unknown_and_mixed_code_reports(self):
        self.fill_vehicle()
        self.app.radio(key="language").set_value("en").run()
        self.app.button(key="analyze").click().run()
        self.assertIn(TEXT["en"]["symptom_report_title"],
                      " ".join(e.value for e in self.app.header))
        self.assertTrue(any(TEXT["en"]["insufficient"] == e.value for e in self.app.info))
        self.code_mode()
        self.app.text_input(key="obd_code").set_value("P0999").run()
        self.app.button(key="analyze").click().run()
        html = " ".join(e.value for e in self.app.markdown)
        self.assertIn(TEXT["en"]["unknown_heading"], html)
        self.assertNotIn(TEXT["en"]["causes_heading"], html)
        self.app.text_input(key="obd_code").set_value("P0301, P0171, P0999").run()
        self.app.button(key="analyze").click().run()
        self.assertFalse(self.app.exception)
        html = " ".join(e.value for e in self.app.markdown)
        self.assertIn("Cylinder 1 Misfire Detected", html)
        self.assertIn("System Too Lean (Bank 1)", html)
        self.assertIn("P0999", html)

    def test_electric_report_withholds_inapplicable_advice(self):
        self.fill_vehicle()
        self.code_mode()
        self.choose("engine_type", "electric")
        self.app.text_input(key="obd_code").set_value("P0301")
        self.app.radio(key="language").set_value("en").run()
        self.app.button(key="analyze").click().run()
        self.assertFalse(self.app.exception)
        html = " ".join(e.value for e in self.app.markdown)
        self.assertIn("Cylinder 1 Misfire Detected", html)
        self.assertNotIn(TEXT["en"]["causes_heading"], html)
        self.assertTrue(any(TEXT["en"]["ev_heading"] in e.value for e in self.app.info))

    def test_missing_library_fails_without_report(self):
        self.fill_vehicle()
        self.code_mode()
        self.app.text_input(key="obd_code").set_value("P0301").run()
        with patch("diagnostics.load_library", side_effect=OSError("Missing test library")):
            self.app.button(key="analyze").click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.error[0].value, TEXT["az"]["library_error"])

    def test_model_disabled_until_make_selected(self):
        self.assertTrue(self.app.selectbox(key="vehicle_model_az").disabled)
        self.assertIsNone(self.app.selectbox(key="vehicle_year_az").value)
        self.choose("vehicle_make", "BMW")
        self.assertFalse(self.app.selectbox(key="vehicle_model_az").disabled)
        self.assertIn("5 Series", self.app.selectbox(key="vehicle_model_az").options)
        self.assertNotIn("Malibu", self.app.selectbox(key="vehicle_model_az").options)

    def test_make_change_clears_model_and_report_but_keeps_details(self):
        self.fill_vehicle()
        self.code_mode()
        self.app.text_input(key="mileage").set_value("85000")
        self.app.text_input(key="displacement").set_value("1,6")
        self.app.text_input(key="obd_code").set_value("P0301")
        self.app.button(key="analyze").click().run()
        self.assertEqual(len(self.app.success), 1)
        self.choose("vehicle_make", "Chevrolet")
        self.assertIsNone(self.app.selectbox(key="vehicle_model_az").value)
        self.assertEqual(len(self.app.success), 0)
        self.assertEqual(self.app.selectbox(key="vehicle_year_az").value, "2020")
        self.assertEqual(self.app.session_state["selected_engine"], "hybrid")
        for field, value in (("mileage", "85000"), ("displacement", "1,6"), ("obd_code", "P0301")):
            self.assertEqual(self.app.text_input(key=field).value, value)
        self.assertEqual(self.app.text_area(key="symptoms").value, "Vibration when idling.")
        self.choose("vehicle_make", "Toyota")
        self.assertIsNone(self.app.selectbox(key="vehicle_model_az").value)

    def test_clearing_make_disables_and_clears_model(self):
        self.fill_vehicle()
        self.choose("vehicle_make", None)
        self.assertTrue(self.app.selectbox(key="vehicle_model_az").disabled)
        self.assertIsNone(self.app.selectbox(key="vehicle_model_az").value)

    def test_other_model_for_listed_make(self):
        self.fill_vehicle()
        self.choose("vehicle_model", OTHER)
        self.app.text_input(key="manual_model_az").set_value("Crown").run()
        self.app.button(key="analyze").click().run()
        self.assertEqual(self.app.session_state["submitted_vehicle"].model, "Crown")
        self.assertEqual(self.app.session_state["submitted_vehicle"].manufacturer, "Toyota")

    def test_manual_names_survive_language_roundtrip(self):
        self.fill_vehicle()
        self.choose("vehicle_make", OTHER)
        self.app.text_input(key="manual_make_az").set_value("Saab").run()
        self.choose("vehicle_model", OTHER)
        self.app.text_input(key="manual_model_az").set_value("9-3").run()
        for language in ("en", "az"):
            self.app.radio(key="language").set_value(language).run()
            self.assertEqual(self.app.text_input(key=f"manual_make_{language}").value, "Saab")
            self.assertEqual(self.app.text_input(key=f"manual_model_{language}").value, "9-3")
            self.assertEqual(self.app.selectbox(key=f"vehicle_year_{language}").value, "2020")
            self.assertIn(TEXT[language]["not_listed"], self.app.selectbox(key=f"vehicle_make_{language}").options)
        self.app.button(key="analyze").click().run()
        self.assertEqual(self.app.session_state["submitted_vehicle"].model, "9-3")

    def test_blank_manual_names_require_validation(self):
        self.fill_vehicle()
        self.choose("vehicle_make", OTHER)
        self.choose("vehicle_model", OTHER)
        self.app.button(key="analyze").click().run()
        messages = [error.value for error in self.app.error]
        self.assertIn(TEXT["az"]["required_manufacturer"], messages)
        self.assertIn(TEXT["az"]["required_model"], messages)

    def test_editing_manual_make_clears_manual_model(self):
        self.choose("vehicle_make", OTHER)
        self.app.text_input(key="manual_make_az").set_value("Saab").run()
        self.choose("vehicle_model", OTHER)
        self.app.text_input(key="manual_model_az").set_value("9-3").run()
        self.app.text_input(key="manual_make_az").set_value("Tesla").run()
        self.assertIsNone(self.app.selectbox(key="vehicle_model_az").value)
        self.assertEqual(self.app.session_state["manual_model"], "")

    def test_stale_model_state_is_rejected(self):
        self.choose("vehicle_make", "Toyota")
        self.app.session_state["vehicle_model"] = "Malibu"
        self.app.run()
        self.assertFalse(self.app.exception)
        self.assertIsNone(self.app.selectbox(key="vehicle_model_az").value)

    def test_year_dropdown_limits_and_clearing(self):
        self.fill_vehicle()
        self.assertEqual(self.app.selectbox(key="vehicle_year_az").options, list(year_options()))
        self.choose("vehicle_year", year_options()[-1])
        self.app.button(key="analyze").click().run()
        self.assertEqual(len(self.app.error), 0)
        self.choose("vehicle_year", None)
        self.app.button(key="analyze").click().run()
        self.assertIn(TEXT["az"]["required_year"], [error.value for error in self.app.error])

    def test_catalog_and_legacy_draft_migration(self):
        self.assertEqual(len(CATALOG), 30)
        self.assertEqual(list(CATALOG), sorted(CATALOG, key=str.casefold))
        for models in CATALOG.values():
            self.assertGreaterEqual(len(models), 3)
            self.assertEqual(len(models), len(set(models)))
        for make, model, expected_make, expected_model in (
            ("Chevrolet", "Malibu", "Chevrolet", "Malibu"),
            ("Saab", "9-3", OTHER, OTHER),
            ("Toyota", "Crown", "Toyota", OTHER),
        ):
            state = dict(manufacturer=make, model=model, year="2021", mileage="12000")
            initialize_selection(state)
            self.assertEqual(state["vehicle_make"], expected_make)
            self.assertEqual(state["vehicle_model"], expected_model)
            self.assertEqual(state["vehicle_year"], "2021")
            self.assertEqual(state["mileage"], "12000")


if __name__ == "__main__":
    unittest.main()
