"""Small rendering helpers keep the main app easy to follow."""

from html import escape

import streamlit as st

from translations import translate
from vehicle import ENGINE_TYPES, VehicleIntake


def clear_submission():
    """Editing an input invalidates the previous summary and validation messages."""
    st.session_state.pop("submitted_vehicle", None)
    st.session_state.pop("validation_errors", None)


def update_engine(widget_key):
    """Keep the engine value independent of the widget's displayed language."""
    st.session_state["selected_engine"] = st.session_state[widget_key]
    clear_submission()


def render_header():
    st.markdown('''<div class="brand"><span class="brand-icon" aria-hidden="true">D</span>
        <span>Diagno<span class="brand-accent">AI</span></span><span class="version">0.3</span></div>''', unsafe_allow_html=True)


def render_intro(language):
    t = lambda key: translate(language, key)
    st.markdown(f'''<section class="hero">
        <div class="eyebrow">{t("eyebrow")}</div>
        <h1>{t("hero_title")}</h1><p>{t("hero_description")}</p>
        <div class="status-pill"><span aria-hidden="true"></span>{t("status")}</div>
        </section>''', unsafe_allow_html=True)


def section_heading(number, title, subtitle):
    st.markdown(f'''<div class="section-heading"><span class="section-number">{number}</span>
        <div><h2>{title}</h2><p>{subtitle}</p></div></div>''', unsafe_allow_html=True)


def render_vehicle_form(language):
    t = lambda key: translate(language, key)
    values = {}

    def text_field(key, label, placeholder, limit):
        values[key] = st.text_input(label, placeholder=t(placeholder), key=key,
                                    max_chars=limit, on_change=clear_submission)

    # Regular keyed widgets preserve drafts across language changes. A batched
    # st.form could discard unsubmitted edits when the language control reruns it.
    with st.container(border=True, key="vehicle_card"):
        section_heading("01", t("vehicle_title"), t("vehicle_subtitle"))
        st.caption(t("required_note"))
        left, right = st.columns(2, gap="medium")
        with left:
            text_field("manufacturer", t("manufacturer") + " *", "manufacturer_placeholder", 80)
        with right:
            text_field("model", t("model") + " *", "model_placeholder", 80)
        left, right = st.columns(2, gap="medium")
        with left:
            text_field("year", t("year") + " *", "year_placeholder", 10)
        with right:
            # Rebuild the display when language changes: Streamlit can retain the
            # previous formatted label for a selected option with a constant key.
            engine_key = f"engine_type_{language}"
            st.session_state.setdefault("selected_engine", "")
            st.session_state[engine_key] = st.session_state.selected_engine
            values["engine_type"] = st.selectbox(
                t("engine_type") + " *", options=("", *ENGINE_TYPES),
                format_func=lambda value: t(value) if value else t("engine_placeholder"),
                key=engine_key, filter_mode=None, on_change=update_engine, args=(engine_key,))
        left, right = st.columns(2, gap="medium")
        with left:
            text_field("displacement", t("displacement_label"), "displacement_placeholder", 20)
        with right:
            text_field("mileage", t("mileage_label"), "mileage_placeholder", 15)
    with st.container(border=True, key="symptoms_card"):
        section_heading("02", t("symptoms_title"), t("symptoms_subtitle"))
        values["symptoms"] = st.text_area(
            t("symptoms") + " *", placeholder=t("symptoms_placeholder"),
            height=150, max_chars=5000, key="symptoms", on_change=clear_submission)
        st.caption(t("symptoms_hint"))
        text_field("obd_code", t("obd_label"), "obd_placeholder", 100)
        st.caption(t("obd_hint"))
    submitted = st.button(t("analyze"), type="primary", width="stretch", key="analyze")
    st.caption(t("submit_hint"))
    return values, submitted


def render_guide(language):
    t = lambda key: translate(language, key)
    steps = "".join(
        f'<div class="guide-step"><span class="step-dot">{i:02}</span><div>'
        f'<h3>{t(f"step{i}_title")}</h3><p>{t(f"step{i}_body")}</p></div></div>'
        for i in range(1, 4))
    st.markdown(f'''<aside class="guide-card"><div class="guide-symbol" aria-hidden="true">↗</div>
        <h2>{t("guide_title")}</h2>{steps}</aside>
        <aside class="scope-card"><span class="mini-label">V0.3</span>
        <h3>{t("scope_title")}</h3><p>{t("scope_body")}</p></aside>
        <aside class="privacy-card"><h3>{t("privacy_title")}</h3><p>{t("privacy_body")}</p></aside>''', unsafe_allow_html=True)


def render_summary(vehicle: VehicleIntake, language: str):
    t = lambda key: translate(language, key)
    missing = t("not_provided")
    displacement = f"{vehicle.displacement:g}" if vehicle.displacement is not None else None
    if displacement is not None and language == "az":
        displacement = displacement.replace(".", ",")
    mileage = f"{vehicle.mileage:,}".replace(",", " ") if vehicle.mileage is not None else None
    fields = [
        ("manufacturer", vehicle.manufacturer), ("model", vehicle.model),
        ("year", str(vehicle.year)), ("engine_type", t(vehicle.engine_type)),
        ("displacement", f"{displacement} L" if displacement is not None else missing),
        ("mileage", f"{mileage} km" if mileage is not None else missing),
        ("obd_code", vehicle.obd_code or missing),
    ]
    # Escape user input before placing it in HTML, including multiline symptoms.
    tiles = "".join(f'<div class="summary-item"><dt>{t(key)}</dt><dd>{escape(value)}</dd></div>' for key, value in fields)
    st.success(t("summary_success"))
    st.markdown(f'''<section class="summary-card"><div class="eyebrow">03</div>
        <h2>{t("summary_title")}</h2><p>{t("summary_subtitle")}</p>
        <dl class="summary-grid">{tiles}</dl><h3>{t("symptoms")}</h3>
        <div class="symptom-summary">{escape(vehicle.symptoms)}</div>
        <p class="summary-edit">{t("summary_edit")}</p></section>''', unsafe_allow_html=True)
