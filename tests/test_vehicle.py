"""Run with the standard library's unittest; no additional packages needed."""

import unittest

from translations import TEXT
from vehicle import ENGINE_TYPES, MAX_YEAR, MIN_YEAR, validate_vehicle


def valid_values(**overrides):
    values = dict(manufacturer="Toyota", model="Corolla", year="2020",
                  engine_type="gasoline", displacement="", mileage="",
                  symptoms="Vibration when idling.", obd_code="")
    values.update(overrides)
    return values


class VehicleTests(unittest.TestCase):
    def test_optional_values_and_all_engine_types(self):
        for engine in ENGINE_TYPES:
            with self.subTest(engine=engine):
                vehicle, errors = validate_vehicle(valid_values(engine_type=engine))
                self.assertEqual(errors, [])
                self.assertIsNone(vehicle.displacement)
                self.assertIsNone(vehicle.mileage)

    def test_normalizes_whitespace_decimal_comma_and_obd(self):
        vehicle, errors = validate_vehicle(valid_values(
            manufacturer=" Toyota ", displacement=" 1,6 ", mileage="0", obd_code=" p0300 "))
        self.assertEqual(errors, [])
        self.assertEqual(vehicle.manufacturer, "Toyota")
        self.assertEqual(vehicle.displacement, 1.6)
        self.assertEqual(vehicle.mileage, 0)
        self.assertEqual(vehicle.obd_code, "P0300")

    def test_blank_required_fields(self):
        fields = ("manufacturer", "model", "year", "engine_type", "symptoms")
        vehicle, errors = validate_vehicle(valid_values(**{field: "   " for field in fields}))
        self.assertIsNone(vehicle)
        self.assertEqual(set(errors), {f"required_{field}" for field in fields})

    def test_invalid_numeric_inputs(self):
        cases = {
            "year": ["2020.5", "NaN", str(MIN_YEAR - 1), str(MAX_YEAR + 1)],
            "displacement": ["NaN", "inf", "0", "-1", "101", "abc"],
            "mileage": ["-1", "1.2", "NaN", "abc"],
        }
        for field, inputs in cases.items():
            for value in inputs:
                with self.subTest(field=field, value=value):
                    vehicle, errors = validate_vehicle(valid_values(**{field: value}))
                    self.assertIsNone(vehicle)
                    self.assertIn(f"invalid_{field}", errors)
                    for language in TEXT:
                        self.assertTrue(TEXT[language][f"invalid_{field}"])

    def test_year_boundaries(self):
        for year in (MIN_YEAR, MAX_YEAR):
            self.assertEqual(validate_vehicle(valid_values(year=str(year)))[1], [])

    def test_translations_have_identical_keys(self):
        self.assertEqual(set(TEXT["az"]), set(TEXT["en"]))
        self.assertTrue(all(text for language in TEXT.values() for text in language.values()))


if __name__ == "__main__":
    unittest.main()
