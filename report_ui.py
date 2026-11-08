"""Render the report without changing any diagnostic rules or user input."""

from html import escape

import streamlit as st

from diagnostics import DiagnosticReport
from translations import translate


def render_report(report: DiagnosticReport, language: str, urgent_safety: bool = False):
    def t(key):
        return translate(language, key)

    def localized(text):
        return text.in_language(language)

    def bullet_list(items):
        st.markdown("\n".join(f"- {localized(item)}" for item in items))

    st.markdown(f"## {t('report_title')}")
    if urgent_safety:
        st.error(t("priority_high"))
        st.info(t("urgent_deferred"))
    st.caption(t("report_intro"))
    if not urgent_safety:
        st.markdown(f"### {t('urgency_heading')}")
        st.warning(t(f"urgency_{report.urgency}"))
        if report.priority_codes:
            st.write(t("priority_codes") + ": " + ", ".join(report.priority_codes))
            reasons = dict.fromkeys(localized(f.definition.urgency_reason)
                                    for f in report.findings if f.code in report.priority_codes)
            for reason in reasons:
                st.write(reason)
        else:
            st.write(t("no_urgency"))
        st.caption(t("urgency_rule"))
    if report.unknown_codes or report.invalid_entries:
        st.warning(t("unknown_urgency"))

    with st.container(border=True, key="safety_card"):
        st.markdown(f"### {t('safety_heading')}")
        st.write(t("safety_stop"))
        st.caption(t("safety_work"))

    if report.no_codes:
        st.info(t("missing_heading") + " — " + t("missing_message"))
    if report.unknown_codes:
        st.markdown(f"### {t('unknown_heading')}")
        st.markdown(f'<div class="symptom-summary">{escape(", ".join(report.unknown_codes))}</div>', unsafe_allow_html=True)
        st.write(t("unknown_message"))
    if report.invalid_entries:
        st.markdown(f"### {t('invalid_heading')}")
        # Never render scanner/user text as Markdown or executable HTML.
        st.markdown(f'<div class="symptom-summary">{escape(", ".join(report.invalid_entries))}</div>', unsafe_allow_html=True)
        st.write(t("invalid_message"))
    if not report.applicable:
        st.info(t("ev_heading") + " — " + t("ev_message"))

    if report.findings:
        st.markdown(f"### {t('recognized_heading')}")
    for finding in report.findings:
        definition = finding.definition
        with st.container(border=True, key=f"code_{finding.code}"):
            st.markdown(f"#### {finding.code} · {localized(definition.meaning)}")
            st.caption(t("meaning_label"))
            st.write(localized(definition.explanation))
            if report.applicable and not urgent_safety:
                st.markdown(f"**{t('causes_heading')}**")
                bullet_list(definition.possible_causes)
                st.markdown(f"**{t('checks_heading')}**")
                bullet_list(definition.safe_checks)
                st.markdown(f"**{t('warnings_heading')}**")
                bullet_list(definition.warnings)
                st.caption(t("code_priority") + ": " + localized(definition.urgency_reason))
            st.markdown(f"**{t('reference_heading')}**")
            for reference in definition.references:
                source = report.library.sources[reference.source]
                st.markdown(f"[{localized(source.title)}]({source.url}) · {localized(reference.location)}")

    with st.container(border=True, key="limitations_card"):
        st.markdown(f"### {t('limitations_heading')}")
        st.write(t("limitations"))
        st.caption(t("source_note"))
        source = report.library.sources["malibu2021"]
        st.markdown(f"[{t('safety_reference')}]({source.url})")
