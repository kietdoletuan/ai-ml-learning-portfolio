from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .contract import ContractError, PartSpec


@dataclass(frozen=True)
class Registry:
    parts: dict[str, PartSpec] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)

    def get(self, part_id: str) -> PartSpec:
        try:
            return self.parts[part_id]
        except KeyError:
            raise KeyError(f"unknown or unavailable part {part_id!r}; available: {sorted(self.parts)}") from None


def load_registry(parts_dir: Path) -> Registry:
    parts: dict[str, PartSpec] = {}
    errors: dict[str, str] = {}
    for path in sorted(Path(parts_dir).glob("*.yaml")):
        part_id = path.stem
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                raise ContractError(f"{part_id}: yaml root must be a mapping")
            parts[part_id] = PartSpec.from_dict(part_id, raw)
        except (ContractError, yaml.YAMLError, TypeError, ValueError) as exc:
            errors[part_id] = str(exc)
    return Registry(parts=parts, errors=errors)
