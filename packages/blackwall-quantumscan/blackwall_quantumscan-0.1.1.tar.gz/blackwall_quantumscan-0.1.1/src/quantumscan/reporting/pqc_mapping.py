"""PQC replacement mapping utilities."""

from __future__ import annotations

from typing import Dict, List, Optional

from ..parser.utils import normalize_algo_name

# NIST PQC standard reference URLs
NIST_URLS = {
    "FIPS_203": "https://csrc.nist.gov/pubs/fips/203/final",  # ML-KEM
    "FIPS_204": "https://csrc.nist.gov/pubs/fips/204/final",  # ML-DSA
    "FIPS_205": "https://csrc.nist.gov/pubs/fips/205/final",  # SLH-DSA
    "SELECTED_ALGOS": "https://csrc.nist.gov/projects/post-quantum-cryptography/selected-algorithms",
    "FIPS_NEWS": "https://csrc.nist.gov/news/2024/postquantum-cryptography-fips-approved",
}

FIPS_203 = NIST_URLS["FIPS_203"]
FIPS_204 = NIST_URLS["FIPS_204"]
FIPS_205 = NIST_URLS["FIPS_205"]
FIPS_202 = "https://csrc.nist.gov/pubs/fips/202/final"

HYBRID_HINT = "현행(EC)과 PQC의 하이브리드 전환 옵션 권고 (예: X25519+ML-KEM-768)"


class MappingResult(Dict[str, object]):
    """Typed dict placeholder for mapping result."""


def _base_result(algo: str, detail: str) -> MappingResult:
    return MappingResult(
        legacy={"algo": algo, "detail": detail},
        recommended=[],
        hybrid_hint=HYBRID_HINT,
        risk={"quantum_vulnerable": True, "notes": "Shor에 취약/해시 충돌 위험(MD5/SHA-1)"},
        status="stable",
        links=[],
    )


def get_pqc_replacement(
    legacy_algo: str,
    key_bits: Optional[int] = None,
    curve: Optional[str] = None,
    use_case: str = "key-establishment",
) -> MappingResult:
    """Return PQC replacement mapping for a legacy algorithm."""
    if key_bits is not None and not isinstance(key_bits, int):
        raise ValueError("key_bits must be int or None")

    algo = normalize_algo_name(legacy_algo)
    detail_parts: List[str] = []
    if key_bits:
        detail_parts.append(f"{algo}-{key_bits}")
    if curve:
        detail_parts.append(curve)
    detail = "/".join(detail_parts) or algo
    result = _base_result(algo, detail)

    if algo == "RSA":
        result["recommended"].append({
            "family": "CRYSTALS-Kyber",
            "name": "CRYSTALS-Kyber",
            "short": "ML-KEM",
            "reason": "양자 내성 키 교환",
            "nist_ref": FIPS_203,
        })
        result["links"].append(FIPS_203)
    elif algo == "ECC":
        result["recommended"].append({
            "family": "CRYSTALS-Dilithium",
            "name": "CRYSTALS-Dilithium",
            "short": "ML-DSA",
            "reason": "양자 내성 전자서명",
            "nist_ref": FIPS_204,
        })
        result["links"].append(FIPS_204)
    elif algo in {"MD5", "SHA-1"}:
        result["recommended"].append({
            "family": "SHA-3",
            "name": "SHA-3(256/512)",
            "reason": "충돌 방지",
            "nist_ref": FIPS_202,
        })
        result["links"].append(FIPS_202)
        result["status"] = "legacy-hash"
    else:
        result["status"] = "unknown"
        result["risk"]["quantum_vulnerable"] = False
        result["links"] = []
    return result
