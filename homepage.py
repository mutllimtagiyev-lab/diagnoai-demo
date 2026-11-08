"""Presentation-only homepage. The illustration is bundled for offline use."""

from base64 import b64encode
from html import escape
from pathlib import Path

import streamlit as st

from translations import translate


def render_homepage(language):
    t = lambda key: escape(translate(language, key))
    asset = Path(__file__).parent / "assets" / "vehicle-hero.webp"
    illustration = b64encode(asset.read_bytes()).decode("ascii")
    title = t("home_title").replace("\n", "<br>")
    cards = "".join(
        f'<article class="service-card"><span class="service-icon" aria-hidden="true">{icon}</span>'
        f'<h3>{t(key + "_title")}</h3><p>{t(key + "_body")}</p></article>'
        for key, icon in (("preliminary", "◎"), ("codes", "⌘"), ("care", "◇"))
    )
    steps = "".join(
        f'<div class="home-step"><span>0{i}</span><div><h3>{t(f"step{i}_title")}</h3>'
        f'<p>{t(f"step{i}_body")}</p></div></div>' for i in range(1, 4)
    )
    st.markdown(f'''<section class="home-hero" lang="{language}">
<div class="hero-copy"><div class="eyebrow">{t("home_eyebrow")}</div>
<h1>{title}</h1><p>{t("home_description")}</p>
<a class="start-link" href="#diagnosis" target="_self">{t("start_diagnosis")} <span aria-hidden="true">↗</span></a>
<small>{t("home_note")}</small></div>
<figure class="vehicle-visual"><div class="visual-label"><span aria-hidden="true">◈</span> {t("visual_label")}</div>
<img src="data:image/webp;base64,{illustration}" alt="{t("visual_alt")}" width="1279" height="800" fetchpriority="high">
<figcaption><span class="visual-line" aria-hidden="true"></span>{t("visual_note")}</figcaption></figure>
</section>
<section class="home-services" lang="{language}"><div class="eyebrow">{t("services_label")}</div>
<h2>{t("services_title")}</h2><div class="service-grid">{cards}</div>
<article class="oil-card"><div class="oil-symbol" aria-hidden="true">◉</div><div class="oil-copy">
<h3>{t("oil_title")}</h3><p>{t("oil_body")}</p></div><span class="coming-soon">{t("coming_soon")}</span></article></section>
<section class="how-section" lang="{language}"><div class="eyebrow">{t("how_label")}</div><h2>{t("how_title")}</h2>
<div class="home-steps">{steps}</div><p class="home-limitation">{t("home_limit")}</p></section>
<section id="diagnosis" class="diagnosis-heading" tabindex="-1" lang="{language}">
<div class="eyebrow">{t("form_eyebrow")}</div><h2>{t("form_title")}</h2><p>{t("form_description")}</p></section>''', unsafe_allow_html=True)


def render_footer(language):
    t = lambda key: escape(translate(language, key))
    st.markdown(f'''<div class="home-footer" lang="{language}"><div><strong>Diagno<span>AI</span></strong>
<p>{t("footer")}</p></div><div><h2>{t("contact_title")}</h2><p>{t("contact_placeholder")}</p></div></div>''', unsafe_allow_html=True)
