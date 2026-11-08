"""Streamlit controls and presentation for symptom guidance."""

from html import escape

import streamlit as st

from symptom_analysis import assess_symptoms
from symptom_data import CONDITIONS, GROUPS, RED_FLAGS
from translations import translate
from ui import clear_submission


def _changed(widget_key, storage_key):
    st.session_state[storage_key] = st.session_state[widget_key]
    clear_submission()


def render_symptom_inputs(language):
    t = lambda key: translate(language, key)
    st.session_state.setdefault("diagnostic_mode", "no_code_mode")
    mode_key = f"mode_{language}"
    st.session_state[mode_key] = st.session_state.diagnostic_mode
    mode = st.radio(t("mode_label"), ("no_code_mode", "have_code_mode"),
                    format_func=t, key=mode_key, horizontal=True,
                    on_change=_changed, args=(mode_key, "diagnostic_mode"))
    selected = []
    for group, options in GROUPS.items():
        storage_key = f"selected_{group}"
        widget_key = f"symptoms_{group}_{language}"
        st.session_state.setdefault(storage_key, [])
        st.session_state[widget_key] = st.session_state[storage_key]
        chosen = st.multiselect(t(f"group_{group}"), options, placeholder=t("select_options"),
                                format_func=t, key=widget_key,
                                on_change=_changed, args=(widget_key, storage_key))
        selected.extend(chosen)
    condition_key = f"condition_{language}"
    st.session_state.setdefault("selected_condition", "")
    st.session_state[condition_key] = st.session_state.selected_condition
    condition = st.selectbox(t("condition_label"), ("", *CONDITIONS),
                             format_func=lambda value: t(value) if value else t("condition_none"),
                             key=condition_key, on_change=_changed,
                             args=(condition_key, "selected_condition"))
    frequency = st.text_input(t("frequency_label"), placeholder=t("frequency_placeholder"),
                              key="issue_frequency", max_chars=200, on_change=clear_submission)
    flag_key = f"red_flags_{language}"
    st.session_state.setdefault("selected_red_flags", [])
    st.session_state[flag_key] = st.session_state.selected_red_flags
    flags = st.multiselect(t("red_flags_label"), RED_FLAGS, format_func=t, placeholder=t("select_red_flags"),
                           key=flag_key, on_change=_changed,
                           args=(flag_key, "selected_red_flags"))
    st.caption(t("red_flags_hint"))
    from component_guidance import COPY
    copy = COPY[language]
    light_key = f'warning_light_{language}'
    st.session_state.setdefault('selected_warning_light', 'unknown')
    st.session_state[light_key] = st.session_state.selected_warning_light
    light = st.selectbox(copy['light'], ('unknown', 'off', 'steady', 'flashing'),
                         format_func=copy.get, key=light_key,
                         on_change=_changed, args=(light_key, 'selected_warning_light'))
    return {"diagnostic_mode": mode, "symptom_ids": tuple(selected),
            "warning_light": light,
            "issue_condition": condition, "issue_frequency": frequency,
            "red_flags": tuple(flags)}


def render_symptom_report(vehicle, language):
    t = lambda key: translate(language, key)
    assessment = assess_symptoms(vehicle)
    st.header(t("symptom_report_title"))
    st.caption(t("symptom_report_intro"))
    st.subheader(t("priority_heading"))
    priority = t("priority_unknown" if assessment.urgency == "unassessed" else f"priority_{assessment.urgency}")
    if assessment.urgency == "high":
        st.error(priority)
    elif assessment.urgency == "soon":
        st.warning(priority)
    else:
        st.info(priority)
    if assessment.safety_indicators:
        st.write(t("priority_reason").format(items=", ".join(t(item) for item in assessment.safety_indicators)))
    elif not assessment.insufficient:
        st.write(t("priority_general"))
    if assessment.urgency == "high":
        st.info(t("urgent_deferred"))
    else:
        st.info(t("safe_general"))
    st.subheader(t("reported_heading"))
    names = ", ".join(t(item) for item in vehicle.symptom_ids) or t("not_selected")
    st.write(names)
    if vehicle.issue_condition:
        st.write(f"{t('condition_label')}: {t(vehicle.issue_condition)}")
    if vehicle.issue_frequency:
        st.text(f"{t('frequency_label')}: {vehicle.issue_frequency}")
    if vehicle.symptoms:
        st.text(f"{t('observations_label')}: {vehicle.symptoms}")
    if assessment.withheld_for_ev:
        st.info(t("unavailable_ev"))
    if assessment.insufficient:
        st.info(t("insufficient"))
    elif assessment.urgency != "high":
        st.subheader(t("systems_heading"))
        for rule in assessment.findings:
            system, reason, causes, mechanic, safe, prevention, more = rule[language]
            with st.container(border=True, key=f"symptom_rule_{rule['id']}"):
                st.markdown(f"#### {escape(system)}")
                for heading, content in (("reason_heading", reason), ("possible_heading", causes),
                                         ("mechanic_heading", mechanic), ("safe_heading", safe),
                                         ("prevention_heading", prevention), ("more_info_heading", more)):
                    st.markdown(f"**{escape(t(heading))}**")
                    st.write(content)
    from component_guidance import render_components
    if assessment.urgency != "high":
        render_components(vehicle, language)
    st.subheader(t("symptom_limit_heading"))
    st.write(t("symptom_limit"))
    if vehicle.obd_code:
        st.caption(t("code_separation"))
