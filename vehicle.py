"""Data validation only: no diagnosis, network calls, or persistent storage."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, ValidationError, field_validator


MIN_YEAR = 1886
MAX_YEAR = date.today().year + 1
ENGINE_TYPES = ("gasoline", "diesel", "hybrid", "electric")


class VehicleIntake(BaseModel):
    manufacturer: str = Field(min_length=1, max_length=80)
    model: str = Field(min_length=1, max_length=80)
    year: int = Field(ge=MIN_YEAR, le=MAX_YEAR)
    engine_type: Literal["gasoline", "diesel", "hybrid", "electric"]
    displacement: float | None = Field(default=None, gt=0, le=100, allow_inf_nan=False)
    mileage: int | None = Field(default=None, ge=0)
    symptoms: str = Field(min_length=1, max_length=5000)
    obd_code: str = Field(default="", max_length=100)

    @field_validator("year", "mileage", mode="before")
    @classmethod
    def whole_numbers_only(cls, value):
        # Reject fractional values rather than silently rounding or truncating.
        if value is not None and (not str(value).isascii() or not str(value).isdigit()):
            raise ValueError("whole_number_required")
        return value


def validate_vehicle(values: dict) -> tuple[VehicleIntake | None, list[str]]:
    """Normalize form strings and return translation keys for any errors."""
    cleaned = {key: value.strip() if isinstance(value, str) else value for key, value in values.items()}
    for key in ("displacement", "mileage"):
        if cleaned.get(key) == "":
            cleaned[key] = None
    if isinstance(cleaned.get("displacement"), str):
        cleaned["displacement"] = cleaned["displacement"].replace(",", ".")
    cleaned["obd_code"] = cleaned.get("obd_code", "").upper()
    try:
        return VehicleIntake(**cleaned), []
    except ValidationError as exc:
        errors = []
        for error in exc.errors():
            field = error["loc"][0]
            prefix = "required" if cleaned.get(field) in (None, "") else "invalid"
            errors.append(f"{prefix}_{field}")
        return None, errors
