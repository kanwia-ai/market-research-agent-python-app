"""Agent result schema validation."""

import logging

logger = logging.getLogger(__name__)

# Expected top-level keys per agent type.
# "response" is the fallback key when the API returns non-JSON text.
AGENT_SCHEMAS: dict[str, set[str]] = {
    "CommunityMapper": {"communities", "platforms", "response"},
    "VoiceMiner": {"quotes", "pain_points", "desires", "language_patterns", "response"},
    "PricingIntel": {"competitor_pricing", "market_rates", "willingness_to_pay", "response"},
    "CompetitorProfiler": {"competitors", "response"},
    "LocalContext": {"economic_context", "digital_landscape", "cultural_factors", "response"},
    "TrendDetector": {"trends", "search_trends", "funding", "response"},
    "OpportunitySynthesizer": {"report", "executive_summary", "response"},
    "SourceVerifier": {"verification_score", "sources", "unsupported_claims", "response"},
}


def validate_agent_result(agent_name: str, result: dict) -> list[str]:
    """Validate an agent result against its expected schema.

    Returns a list of warnings (empty if valid). Does NOT raise ---
    we log warnings but allow partial results to proceed.
    """
    warnings = []

    if not isinstance(result, dict):
        warnings.append(f"{agent_name}: result is not a dict (got {type(result).__name__})")
        return warnings

    # Check for error results (these are valid, just failed)
    if "error" in result:
        return warnings

    expected = AGENT_SCHEMAS.get(agent_name)
    if expected is None:
        warnings.append(f"{agent_name}: unknown agent type, cannot validate")
        return warnings

    # Check if result has at least one expected key
    result_keys = set(result.keys()) - {"_token_usage"}
    matching = result_keys & expected
    if not matching:
        warnings.append(
            f"{agent_name}: result has no expected keys. "
            f"Got {sorted(result_keys)}, expected at least one of {sorted(expected)}"
        )

    # Check for empty results
    for key in matching:
        value = result[key]
        if value is None or value == "" or value == [] or value == {}:
            warnings.append(f"{agent_name}: key '{key}' is empty")

    return warnings
