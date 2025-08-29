from typing import List, Dict, Any, Optional, Tuple
from .blazemetrics import (
    guard_blocklist as _guard_blocklist,
    guard_regex as _guard_regex,
    guard_pii_redact as _guard_pii_redact,
    guard_safety_score as _guard_safety_score,
    guard_json_validate as _guard_json_validate,
    guard_detect_injection_spoof as _guard_detect_injection_spoof,
    guard_max_cosine_similarity as _guard_max_cosine_similarity,
)


class Guardrails:
    def __init__(
        self,
        blocklist: Optional[List[str]] = None,
        regexes: Optional[List[str]] = None,
        case_insensitive: bool = True,
        redact_pii: bool = True,
        safety: bool = True,
        json_schema: Optional[str] = None,
        unsafe_exemplars: Optional[List[List[float]]] = None,
        detect_injection_spoof: bool = True,
    ) -> None:
        self.blocklist = blocklist or []
        self.regexes = regexes or []
        self.case_insensitive = case_insensitive
        self.redact_pii = redact_pii
        self.safety = safety
        self.json_schema = json_schema
        self.unsafe_exemplars = unsafe_exemplars
        self.detect_injection_spoof = detect_injection_spoof

    def check(self, texts: List[str]) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        if self.blocklist:
            out["blocked"] = _guard_blocklist(texts, self.blocklist, self.case_insensitive)
        else:
            out["blocked"] = [False] * len(texts)
        if self.regexes:
            out["regex_flagged"] = _guard_regex(texts, self.regexes, self.case_insensitive)
        else:
            out["regex_flagged"] = [False] * len(texts)
        if self.redact_pii:
            out["redacted"] = _guard_pii_redact(texts)
        else:
            out["redacted"] = texts
        if self.safety:
            out["safety_score"] = _guard_safety_score(texts)
        else:
            out["safety_score"] = [0.0] * len(texts)
        if self.detect_injection_spoof:
            out["injection_spoof"] = _guard_detect_injection_spoof(texts)
        else:
            out["injection_spoof"] = [False] * len(texts)
        if self.json_schema is not None:
            valid, repaired = _guard_json_validate(texts, self.json_schema)
            out["json_valid"] = valid
            out["json_repaired"] = repaired
        if self.unsafe_exemplars is not None and len(self.unsafe_exemplars) > 0:
            # For demo simplicity, use text length as dim-1 embedding; in practice pass real embeddings
            # Here we skip deriving embeddings; expose separate API for embeddings similarity
            pass
        return out


def guardrails_check(
    texts: List[str],
    blocklist: Optional[List[str]] = None,
    regexes: Optional[List[str]] = None,
    case_insensitive: bool = True,
    redact_pii: bool = True,
    safety: bool = True,
    json_schema: Optional[str] = None,
) -> Dict[str, Any]:
    gr = Guardrails(
        blocklist=blocklist,
        regexes=regexes,
        case_insensitive=case_insensitive,
        redact_pii=redact_pii,
        safety=safety,
        json_schema=json_schema,
    )
    return gr.check(texts)


def max_similarity_to_unsafe(candidates: List[List[float]], exemplars: List[List[float]]) -> List[float]:
    import numpy as np
    import numpy.typing as npt
    c = np.array(candidates, dtype=np.float32)
    e = np.array(exemplars, dtype=np.float32)
    return _guard_max_cosine_similarity(c, e)  # type: ignore 