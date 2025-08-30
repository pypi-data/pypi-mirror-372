from dataclasses import dataclass
from typing import Any, List, Optional

from ..api.noun_phrase import NounPhrase
from .types import ConceptOptionalType, ConceptType


@dataclass
class ConceptDescriptor:
    noun_phrases: List[NounPhrase]
    _type: ConceptType
    default_value: Any
    description: Optional[str] = None

    @property
    def is_optional(self) -> bool:
        return isinstance(self._type, ConceptOptionalType) or self.default_value is not None

    @property
    def type(self) -> ConceptType:
        return ConceptOptionalType(inner=self._type) if not isinstance(self._type, ConceptOptionalType) and self.default_value is not None else self._type
