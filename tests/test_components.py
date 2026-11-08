import unittest
from vehicle import VehicleIntake
from component_guidance import component_candidates, COPY
from symptom_analysis import assess_symptoms

def vehicle(engine='gasoline', **kwargs):
    return VehicleIntake(manufacturer='Chevrolet', model='Malibu', year=2021,
                         engine_type=engine, symptom_ids=('rough_idle','power_loss'), **kwargs)

class ComponentTests(unittest.TestCase):
    def test_gasoline_candidates(self):
        self.assertEqual(len(component_candidates(vehicle())), 4)
    def test_diesel_excludes_ignition(self):
        self.assertNotIn('ignition', [r[0] for r in component_candidates(vehicle('diesel'))])
    def test_ev_and_unspecified_hybrid_withhold_components(self):
        for engine in ('electric','hybrid'):
            self.assertEqual(component_candidates(vehicle(engine)), ())
    def test_missing_symptoms(self):
        self.assertEqual(component_candidates(vehicle().model_copy(update={'symptom_ids':()})), ())
    def test_flashing_answer_escalates(self):
        self.assertEqual(assess_symptoms(vehicle(warning_light='flashing')).urgency, 'high')
    def test_translation_keys_and_uncertainty(self):
        self.assertEqual(set(COPY['az']), set(COPY['en']))
        self.assertIn('unconfirmed', COPY['en']['status'])
