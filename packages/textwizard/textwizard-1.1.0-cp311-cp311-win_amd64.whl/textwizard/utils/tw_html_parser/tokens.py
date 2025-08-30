# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


CHARACTER  = 1
START_TAG  = 2
END_TAG    = 3
COMMENT    = 4
DOCTYPE    = 5
EOF        = 6

TOKEN_TYPE_STR = {
    CHARACTER:  "Characters",
    START_TAG:  "StartTag",
    END_TAG:    "EndTag",
    COMMENT:    "Comment",
    DOCTYPE:    "DOCTYPE",
    EOF:        "EOF"
}

_TOKEN_FIELDS = {
    CHARACTER: ["data", "null_character", "space_character"],
    START_TAG: ["name", "attributes", "self_closing"],
    END_TAG:   ["name", "attributes", "self_closing"],
    COMMENT:   ["data"],
    DOCTYPE:   ["name", "public_id", "system_id", "quirks_mode"],
    EOF:       [],
}

@dataclass(slots=True)
class Attribute:
    name: str
    value: str
    namespace: Optional[str] = None
    prefix: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "value": self.value,
            "namespace": self.namespace,
            "prefix": self.prefix,
        }


@dataclass(slots=True)
class Token:
    type: int
    name: Optional[str] = ''
    data: Optional[str] = ''
    attributes: List[Attribute] = field(default_factory=list)
    public_id: Optional[str] = ''
    system_id: Optional[str] = ''
    quirks_mode: Optional[bool] = None
    self_closing: bool = False
    null_character: bool = False
    space_character: bool = False

    @property
    def lower_name(self) -> str:
        return self.name.lower() if self.name else ''

    def to_dict(self) -> dict:
        token_dict = {
            "type": TOKEN_TYPE_STR[self.type],
        }
        fields = _TOKEN_FIELDS.get(self.type, [])
        for field_name in fields:
            value = getattr(self, field_name)
            if field_name == "attributes" and value:
                token_dict[field_name] = [attr.to_dict() for attr in value]
            else:
                token_dict[field_name] = value
        return token_dict


    def get_attribute_value(self, attr_name: str) -> Optional[str]:
        attr_name_lower = attr_name.lower()
        for attr in self.attributes:
            if attr.name.lower() == attr_name_lower:
                return attr.value
        return None

    def acknowledge_self_closing(self) -> None:
        self.self_closing = True

def __repr__(self) -> str:
    return (f"<Token type={TOKEN_TYPE_STR[self.type]!r} "
            f"name={self.name!r} "
            f"data={self.data!r} "
            f"attrs={len(self.attributes)} "
            f"self_closing={self.self_closing}>")