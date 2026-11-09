"""Optional, consent-based extraction, rendered before manual widgets."""
import os
import streamlit as st
from ai_symptoms import extract, safety_precheck, merge_confirmed, ExtractionUnavailable
from symptom_analysis import HIGH_RISK_SYMPTOMS
from translations import translate

COPY = {
 'en': {
  'title':'AI-assisted symptom understanding · optional',
  'intro':'AI suggests structured selections from this text only. Confirm them before use. Diagnosis and safety priority remain rule-based. Manual selection works offline.',
  'text':'Describe symptoms for AI (no names, VIN, plates, contact details or other identifiers)',
  'consent':'I checked this text contains no identifying information and agree to send it to Google Gemini.',
  'run':'Suggest symptom selections', 'confirm':'Confirm and add these selections',
  'disabled':'AI is disabled or unavailable. Continue with manual selections below.',
  'error':'AI could not return a valid response. No selections were changed. Use manual selections or try again later.',
  'uncertain':'Clarification needed: describe what happened, when, and any dashboard warning. Review selections manually; this output cannot be transferred.',
  'review':'AI contribution: suggested categories below. Nothing has been transferred yet. Verify each item against your observations.',
  'none':'No supported category extracted. Use manual selection or clarify the description.',
  'limit':'No detected hazard does not mean the vehicle is safe. The local keyword check can miss wording or flag negated statements. Other free-text observations remain unanalyzed.',
  'precheck':'Local keyword safety precheck (independent of AI; may include false alarms):',
  'added':'Confirmed AI categories were added to the manual form. Review the form before submitting.',
 },
 'az': {
  'title':'AI ilə əlamətlərin anlaşılması · istəyə bağlı',
  'intro':'AI yalnız bu mətndən strukturlaşdırılmış seçimlər təklif edir. İstifadədən əvvəl təsdiqləyin. Diaqnostika və təhlükəsizlik prioriteti sabit qaydalara əsaslanır. Əl ilə seçim internetsiz işləyir.',
  'text':'AI üçün əlamətləri yazın (ad, VIN, nömrə nişanı, əlaqə və digər şəxsi məlumatlar olmadan)',
  'consent':'Mətndə şəxsi məlumat olmadığını yoxladım və onun Google Gemini xidmətinə göndərilməsinə razıyam.',
  'run':'Əlamət seçimləri təklif et', 'confirm':'Bu seçimləri təsdiqlə və əlavə et',
  'disabled':'AI söndürülüb və ya əlçatan deyil. Aşağıda əl ilə seçim edin.',
  'error':'AI düzgün cavab qaytara bilmədi. Seçimlər dəyişməyib. Əl ilə seçin və ya sonra yenidən sınayın.',
  'uncertain':'Dəqiqləşdirmə lazımdır: nə baş verdiyini, vaxtını və panel xəbərdarlığını təsvir edin. Seçimləri əl ilə yoxlayın; bu nəticə köçürülə bilməz.',
  'review':'AI töhfəsi: aşağıdakı kateqoriyaları təklif etdi. Hələ heç nə köçürülməyib. Hər birini müşahidələrinizlə yoxlayın.',
  'none':'Dəstəklənən kateqoriya tapılmadı. Əl ilə seçin və ya təsviri dəqiqləşdirin.',
  'limit':'Təhlükənin aşkarlanmaması avtomobilin təhlükəsiz olduğunu bildirmir. Yerli açar söz yoxlaması bəzi ifadələri qaçıra və inkar edilən halları işarələyə bilər. Digər sərbəst mətn qeydləri təhlil edilmir.',
  'precheck':'Yerli açar söz təhlükəsizlik yoxlaması (AI-dan müstəqil; yanlış siqnal mümkündür):',
  'added':'Təsdiqlənmiş AI kateqoriyaları əl ilə seçim formasına əlavə edildi. Göndərməzdən əvvəl formanı yoxlayın.',
 }
}


def setting(key):
    value = os.environ.get(key)
    if value is not None:
        return value
    try:
        return str(st.secrets.get(key, ''))
    except Exception:
        return ''


def render_ai(language):
    c = COPY[language]
    with st.container(border=True):
        st.subheader(c['title'])
        st.caption(c['intro'])
        text = st.text_area(c['text'], max_chars=2000, key='ai_text')
        # Never retain an extraction or consent after its source text changes.
        if st.session_state.get('ai_source') != text:
            st.session_state.pop('ai_result', None)
            st.session_state['ai_consent'] = False
            st.session_state['ai_source'] = text
            st.session_state.pop('submitted_vehicle', None)
        hazards = safety_precheck(text)
        if hazards:
            st.error(translate(language, 'priority_high'))
            st.caption(c['precheck'] + ' ' + ', '.join(translate(language, h) for h in hazards))
        st.caption(c['limit'])
        consent = st.checkbox(c['consent'], key='ai_consent')
        enabled = setting('DIAGNOAI_AI_ENABLED').lower() == 'true'
        key = setting('GEMINI_API_KEY') if enabled else ''
        if not enabled or not key:
            st.info(c['disabled'])
        if st.button(c['run'], key='ai_extract', disabled=not (enabled and key and consent and text.strip())):
            st.session_state.pop('ai_result', None)
            try:
                st.session_state.ai_result = extract(text, api_key=key, enabled=enabled)
            except ExtractionUnavailable:
                st.warning(c['error'])
        result = st.session_state.get('ai_result')
        if result is not None:
            if (result.hazards or set(result.symptoms) & HIGH_RISK_SYMPTOMS) and not hazards:
                st.error(translate(language, 'priority_high'))
            st.info(c['review'])
            st.write(', '.join(translate(language, s) for s in (*result.symptoms, *result.hazards)) or c['none'])
            if result.uncertain:
                st.warning(c['uncertain'])
            elif result.symptoms or result.hazards:
                if st.button(c['confirm'], key='ai_confirm'):
                    merge_confirmed(st.session_state, result)
                    st.session_state.pop('ai_result', None)
                    st.success(c['added'])
        return hazards
