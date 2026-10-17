from dataclasses import dataclass
from typing import Mapping, Sequence

TOKENS_PER_MILLION = 1_000_000


@dataclass(frozen=True)
class ModelRate:
    input_micros_per_mtok: int
    output_micros_per_mtok: int


@dataclass(frozen=True)
class PriceVersion:
    effective_from: str
    rates: Mapping[str, ModelRate]


def active_version(versions: Sequence[PriceVersion], day: str) -> PriceVersion:
    effective = [version for version in versions if version.effective_from <= day]
    if not effective:
        raise ValueError(f"no price version effective on {day}")
    return max(effective, key=lambda version: version.effective_from)


def price_micros(
    versions: Sequence[PriceVersion],
    day: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> int:
    version = active_version(versions, day)
    rate = version.rates.get(model)
    if rate is None:
        raise ValueError(f"no price for model {model} in version {version.effective_from}")
    total = (
        input_tokens * rate.input_micros_per_mtok
        + output_tokens * rate.output_micros_per_mtok
    )
    return total // TOKENS_PER_MILLION


DEFAULT_PRICE_VERSIONS = [
    PriceVersion(
        effective_from="2026-01-01",
        rates={
            "model-small": ModelRate(input_micros_per_mtok=250_000, output_micros_per_mtok=1_000_000),
            "model-large": ModelRate(input_micros_per_mtok=3_000_000, output_micros_per_mtok=12_000_000),
        },
    ),
    PriceVersion(
        effective_from="2026-08-01",
        rates={
            "model-small": ModelRate(input_micros_per_mtok=200_000, output_micros_per_mtok=800_000),
            "model-large": ModelRate(input_micros_per_mtok=2_500_000, output_micros_per_mtok=10_000_000),
        },
    ),
]
