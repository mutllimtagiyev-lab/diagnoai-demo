"""Curated model names only: not a production-year or compatibility database."""

import json
from pathlib import Path

OTHER = "__other__"


def load_catalog():
    data = json.loads((Path(__file__).parent / "data" / "vehicle_catalog.json").read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not data:
        raise ValueError("Vehicle catalog must be a nonempty object")
    for make, models in data.items():
        if not isinstance(make, str) or not make.strip() or make == OTHER:
            raise ValueError("Invalid manufacturer name")
        if not isinstance(models, list) or not models or any(
            not isinstance(model, str) or not model.strip() or model == OTHER for model in models
        ) or len(models) != len(set(models)):
            raise ValueError("Invalid or duplicate model names")
    return {make: tuple(sorted(models, key=str.casefold))
            for make, models in sorted(data.items(), key=lambda item: item[0].casefold())}


CATALOG = load_catalog()
