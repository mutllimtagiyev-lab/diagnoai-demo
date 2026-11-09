import json
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from urllib.error import HTTPError
from ai_symptoms import Extraction, ExtractionUnavailable, extract, safety_precheck, merge_confirmed
from ai_ui import COPY
from translations import TEXT
from streamlit.testing.v1 import AppTest

# Editorial expected labels. Mocked fixtures are NOT measured model predictions.
CASES = [
 ('en','My car shakes when stopped.', ['rough_idle'], [], False),
 ('en','It loses power while accelerating.', ['power_loss'], [], False),
 ('en','The check-engine light is flashing.', [], ['flashing_light'], False),
 ('en','My brakes barely stop the car.', ['brakes'], ['brake_performance'], False),
 ('en','I cannot control the steering.', ['steering'], ['steering_control'], False),
 ('en','It is overheating with steam.', ['overheating'], ['severe_overheating'], False),
 ('en','Fuel is leaking under the car.', [], ['fuel_leak'], False),
 ('en','There is smoke and fire.', [], ['smoke_fire'], False),
 ('en','Something feels strange.', [], [], True),
 ('en','Write a poem about flowers.', [], [], True),
 ('az','Dayananda mühərrik titrəyir.', ['rough_idle'], [], False),
 ('az','Sürətlənəndə güc itir.', ['power_loss'], [], False),
 ('az','Mühərrik işığı yanıb-sönür.', [], ['flashing_light'], False),
 ('az','Əyləc avtomobili saxlamır.', ['brakes'], ['brake_performance'], False),
 ('az','Sükanı idarə edə bilmirəm.', ['steering'], ['steering_control'], False),
 ('az','Mühərrik çox qızır və buxar çıxır.', ['overheating'], ['severe_overheating'], False),
 ('az','Yanacaq sızır.', [], ['fuel_leak'], False),
 ('az','Tüstü və yanğın var.', [], ['smoke_fire'], False),
 ('az','Nəsə qəribədir.', [], [], True),
 ('az','Mənə şeir yaz.', [], [], True),
]

def response(data):
    r = MagicMock()
    r.__enter__.return_value.read.return_value = json.dumps({'candidates':[{
        'finishReason':'STOP', 'content':{'parts':[{'text':json.dumps(data)}]}}]}).encode()
    return r

class AITests(unittest.TestCase):
    def test_twenty_mocked_bilingual_contract_cases(self):
        self.assertEqual(sum(c[0]=='az' for c in CASES),10)
        for lang,text,symptoms,hazards,uncertain in CASES:
            with self.subTest(text=text), patch('ai_symptoms.urllib.request.urlopen', return_value=response(dict(symptoms=symptoms,hazards=hazards,uncertain=uncertain))) as call:
                result = extract(text,api_key='test-only',enabled=True)
                self.assertEqual(result.symptoms,symptoms)
                self.assertEqual(result.hazards,hazards)
                self.assertEqual(result.uncertain,uncertain)
                self.assertEqual(call.call_count,1)
                body=json.loads(call.call_args.args[0].data)
                self.assertEqual(body['contents'][0]['parts'],[{'text':text}])
                self.assertEqual(call.call_args.kwargs['timeout'],15)

    def test_no_network_without_explicit_enable_or_key(self):
        with patch('ai_symptoms.urllib.request.urlopen') as call:
            for key,enabled in [('x',False),('',True)]:
                with self.assertRaises(ExtractionUnavailable): extract('rough idle',api_key=key,enabled=enabled)
            call.assert_not_called()

    def test_invalid_output_rejected(self):
        for data in [dict(symptoms=['replace_engine'],hazards=[],uncertain=False),dict(symptoms=[],hazards=[],uncertain=False,advice='drive safely'),dict(symptoms=[],hazards=[],uncertain='false')]:
            with patch('ai_symptoms.urllib.request.urlopen',return_value=response(data)):
                with self.assertRaises(ExtractionUnavailable): extract('text',api_key='x',enabled=True)

    def test_network_errors_are_generic_no_retries(self):
        for error in [TimeoutError('secret'),HTTPError('url',429,'secret',{},None),OSError('secret')]:
            with patch('ai_symptoms.urllib.request.urlopen',side_effect=error) as call:
                with self.assertRaisesRegex(ExtractionUnavailable,'^AI unavailable$'): extract('text',api_key='x',enabled=True)
                self.assertEqual(call.call_count,1)

    def test_precheck_urgent_fixture_coverage(self):
        for lang,text,symptoms,hazards,uncertain in CASES:
            if hazards:
                with self.subTest(text=text): self.assertTrue(set(hazards)<=set(safety_precheck(text)))

    def test_documented_keyword_limits(self):
        self.assertIn('smoke_fire',safety_precheck('There is no smoke.'))
        self.assertFalse(safety_precheck('The pedal sinks and the car will not slow down.'))

    def test_confirmation_preserves_manual_hazards(self):
        state={'selected_red_flags':['fuel_leak'],'selected_powertrain':['hard_start'],'submitted_vehicle':'old'}
        merge_confirmed(state,Extraction(symptoms=['rough_idle'],hazards=['flashing_light'],uncertain=False))
        self.assertEqual(state['selected_red_flags'],['fuel_leak','flashing_light'])
        self.assertEqual(state['selected_powertrain'],['hard_start','rough_idle'])
        self.assertNotIn('submitted_vehicle',state)

    def test_bilingual_copy_complete(self):
        self.assertEqual(set(COPY['az']),set(COPY['en']))
        self.assertTrue(all(COPY['az'].values()))

    def test_disabled_ui_still_warns_without_network(self):
        with patch.dict('os.environ',{'DIAGNOAI_AI_ENABLED':'false'}),patch('ai_symptoms.urllib.request.urlopen') as call:
            app=AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run()
            app.text_area(key='ai_text').set_value('Fuel is leaking').run()
            self.assertFalse(app.exception)
            self.assertTrue(app.error)
            self.assertTrue(app.button(key='ai_extract').disabled)
            app.radio(key='language').set_value('en').run()
            self.assertTrue(any('stop using' in e.value for e in app.error))
            call.assert_not_called()

    def test_enabled_without_key_keeps_manual_form(self):
        with patch('ai_ui.setting', side_effect=lambda k: 'true' if k == 'DIAGNOAI_AI_ENABLED' else ''), patch('ai_symptoms.urllib.request.urlopen') as call:
            app=AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run()
            self.assertFalse(app.exception)
            self.assertTrue(app.button(key='ai_extract').disabled)
            self.assertTrue(any(COPY['az']['disabled'] == item.value for item in app.info))
            self.assertTrue(app.selectbox(key='vehicle_make_az'))
            call.assert_not_called()

    def test_ui_confirmation_and_stale_text(self):
        result=Extraction(symptoms=['rough_idle','power_loss'],hazards=['flashing_light'],uncertain=False)
        with patch('ai_ui.setting',side_effect=lambda k: 'true' if k=='DIAGNOAI_AI_ENABLED' else 'test-only'),patch('ai_ui.extract',return_value=result) as call:
            app=AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run()
            app.text_area(key='ai_text').set_value('Shakes at idle and loses power; light flashing').run()
            app.checkbox(key='ai_consent').check().run()
            app.button(key='ai_extract').click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.multiselect(key='symptoms_powertrain_az').value,[])
            app.radio(key='language').set_value('en').run()
            app.button(key='ai_confirm').click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.multiselect(key='symptoms_powertrain_en').value,['rough_idle','power_loss'])
            self.assertIn('flashing_light',app.multiselect(key='red_flags_en').value)
            self.assertEqual(call.call_count,1)
            app.text_area(key='ai_text').set_value('different observation').run()
            self.assertFalse(app.checkbox(key='ai_consent').value)
            self.assertFalse(any(b.key=='ai_confirm' for b in app.button))

    def test_mocked_unrecognized_brake_wording_warns_before_confirmation(self):
        result=Extraction(symptoms=['brakes'],hazards=['brake_performance'],uncertain=False)
        with patch('ai_ui.setting',side_effect=lambda k: 'true' if k=='DIAGNOAI_AI_ENABLED' else 'test-only'), patch('ai_ui.extract',return_value=result) as call:
            app=AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run()
            app.text_area(key='ai_text').set_value('The pedal sinks and the car will not slow down.').run()
            self.assertFalse(app.error)
            app.checkbox(key='ai_consent').check().run()
            app.button(key='ai_extract').click().run()
            self.assertIn(TEXT['az']['priority_high'],[item.value for item in app.error])
            self.assertEqual(app.multiselect(key='symptoms_chassis_az').value,[])
            app.radio(key='language').set_value('en').run()
            self.assertIn(TEXT['en']['priority_high'],[item.value for item in app.error])
            self.assertEqual(app.multiselect(key='symptoms_chassis_en').value,[])
            self.assertEqual(call.call_count,1)
