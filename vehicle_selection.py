"""Dependent identity widgets backed by language-independent draft values."""

import streamlit as st

from translations import translate
from vehicle import MIN_YEAR, MAX_YEAR
from vehicle_catalog import CATALOG, OTHER


def initialize_selection(state):
    """Migrate an existing v0.4 draft once, including unlisted vehicle names."""
    if "vehicle_make" in state:
        return
    make = state.get("manufacturer", "").strip()
    model = state.get("model", "").strip()
    state["vehicle_make"] = make if make in CATALOG else OTHER if make else ""
    state["manual_make"] = make if make not in CATALOG else ""
    state["vehicle_model"] = model if model in CATALOG.get(make, ()) else OTHER if make and model else ""
    state["manual_model"] = model if model not in CATALOG.get(make, ()) else ""
    year = str(state.get("year", ""))
    state["vehicle_year"] = year if year in year_options() else ""


def year_options():
    # Preserve the validator's full historical range; newer years appear first.
    return tuple(str(year) for year in range(MAX_YEAR, MIN_YEAR - 1, -1))


def reset_model(state):
    state["vehicle_model"] = ""
    state["manual_model"] = ""


def render_identity(language, invalidate):
    t = lambda key: translate(language, key)
    state = st.session_state
    initialize_selection(state)

    def changed(widget_key, value_key):
        old = state.get(value_key)
        state[value_key] = state[widget_key]
        if value_key in ("vehicle_make", "manual_make") and old != state[value_key]:
            reset_model(state)
        invalidate()

    def select(value_key, label, options, placeholder, disabled=False):
        widget_key = f"{value_key}_{language}"
        state[widget_key] = state.get(value_key) or None
        value = st.selectbox(
            t(label) + " *", options=options, index=None, key=widget_key,
            format_func=lambda option: t("not_listed") if option == OTHER else option,
            placeholder=t(placeholder), disabled=disabled,
            on_change=changed, args=(widget_key, value_key),
        )
        return value or ""

    def manual(value_key, label, placeholder):
        widget_key = f"{value_key}_{language}"
        state[widget_key] = state.get(value_key, "")
        return st.text_input(t(label) + " *", key=widget_key,
                             placeholder=t(placeholder), max_chars=80,
                             on_change=changed, args=(widget_key, value_key))

    left, right = st.columns(2, gap="medium")
    with left:
        make = select("vehicle_make", "manufacturer", (*CATALOG, OTHER), "select_manufacturer")
        manufacturer = manual("manual_make", "manual_manufacturer", "manufacturer_placeholder") if make == OTHER else make
    options = (*CATALOG.get(make, ()), OTHER) if make else ()
    if state.get("vehicle_model") and state.vehicle_model not in options:
        reset_model(state)
        invalidate()
    with right:
        model_choice = select("vehicle_model", "model", options,
                              "select_model" if make else "select_manufacturer_first", disabled=not make)
        model = manual("manual_model", "manual_model_label", "model_placeholder") if model_choice == OTHER else model_choice
    return {"manufacturer": manufacturer, "model": model}, select
