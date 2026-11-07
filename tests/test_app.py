"""Exercise real Streamlit widget state, validation, and summary output."""

from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest

from translations import TEXT
from unittest.mock import patch


APP_PATH = str(Path(__file__).resolve().parents[1] / "app.py")


class AppTests(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(APP_PATH, default_timeout=15).run()
        self.assertFalse(self.app.exception)

    def fill_vehicle(self):
        for key, value in (("manufacturer", "Toyota"), ("model", "Corolla"), ("year", "2020")):
            self.app.text_input(key=key).set_value(value)
        self.app.selectbox[0].set_value("hybrid")
        self.app.text_area(key="symptoms").set_value("Vibration when idling.")
        self.app.run()

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
        self.assertEqual(self.app.text_input(key="manufacturer").value, "Toyota")
        self.assertEqual(self.app.selectbox[0].value, "hybrid")
        self.assertEqual(self.app.selectbox[0].key, "engine_type_en")
        self.app.button(key="analyze").click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual(len(self.app.error), 0)
        self.assertEqual(len(self.app.success), 1)
        html = " ".join(element.value for element in self.app.markdown)
        self.assertIn("Hybrid", html)
        self.assertIn("Not provided", html)
        self.app.radio(key="language").set_value("az").run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.selectbox[0].value, "hybrid")
        self.assertEqual(self.app.selectbox[0].key, "engine_type_az")
        self.assertEqual(len(self.app.success), 1)
        html = " ".join(element.value for element in self.app.markdown)
        self.assertIn("Hibrid", html)
        self.assertIn("Daxil edilməyib", html)
        self.app.text_input(key="model").set_value("Yaris").run()
        self.assertEqual(len(self.app.success), 0)

    def test_summary_escapes_markup_and_keeps_zero_mileage(self):
        self.fill_vehicle()
        self.app.text_input(key="manufacturer").set_value("<b>Toyota</b>")
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
        for key, value in (("manufacturer", "Chevrolet"), ("model", "Malibu"), ("year", "2021"), ("obd_code", "P0301")):
            self.app.text_input(key=key).set_value(value)
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
        self.assertTrue(any("Symptom-only analysis is not supported" in e.value for e in self.app.info))
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
        self.app.selectbox[0].set_value("electric")
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
        with patch("diagnostics.load_library", side_effect=OSError("Missing test library")):
            self.app.button(key="analyze").click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.error[0].value, TEXT["az"]["library_error"])


if __name__ == "__main__":
    unittest.main()
