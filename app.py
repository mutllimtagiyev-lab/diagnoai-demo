"""DiagnoAI v0.3: bilingual, offline OBD-II reference assistant."""

from pathlib import Path

import streamlit as st

from translations import LANGUAGES, translate
from ui import render_header, render_intro, render_vehicle_form, render_guide, render_summary
from vehicle import validate_vehicle
from diagnostics import build_report
from report_ui import render_report


st.set_page_config(page_title="DiagnoAI", page_icon="🚘", layout="wide")
st.html(f"<style>{Path(__file__).with_name('styles.css').read_text(encoding='utf-8')}</style>")

# Store language-independent values so switching languages preserves the draft.
st.session_state.setdefault("language", "az")
header, language_control = st.columns([3, 1], vertical_alignment="center")
with header:
    render_header()
with language_control:
    st.radio(
        translate(st.session_state.language, "language"),
        options=list(LANGUAGES), format_func=LANGUAGES.get,
        key="language", horizontal=True,
    )

language = st.session_state.language
render_intro(language)
form_column, guide_column = st.columns([2.1, 1], gap="large")
with form_column:
    values, submitted = render_vehicle_form(language)
    if submitted:
        vehicle, errors = validate_vehicle(values)
        st.session_state["validation_errors"] = errors
        st.session_state["submitted_vehicle"] = vehicle
    if st.session_state.get("validation_errors"):
        st.error(translate(language, "fix_errors"))
        for error_key in st.session_state.validation_errors:
            st.error(translate(language, error_key))
with guide_column:
    render_guide(language)
if st.session_state.get("submitted_vehicle") is not None:
    render_summary(st.session_state.submitted_vehicle, language)
    try:
        report = build_report(st.session_state.submitted_vehicle)
    except (OSError, ValueError):
        st.error(translate(language, "library_error"))
    else:
        render_report(report, language)
st.markdown(f'<div class="page-footer">DiagnoAI <span>·</span> {translate(language, "footer")}</div>', unsafe_allow_html=True)
