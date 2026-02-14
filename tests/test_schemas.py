"""Tests for agent result schema validation."""

import pytest

from src.schemas import AGENT_SCHEMAS, validate_agent_result


class TestValidResults:
    """Test that valid agent results pass validation."""

    def test_community_mapper_with_expected_keys(self):
        """CommunityMapper result with expected keys produces no warnings."""
        result = {
            "communities": [{"name": "r/freelance", "url": "https://reddit.com/r/freelance"}],
            "platforms": ["Reddit", "Twitter"],
        }
        warnings = validate_agent_result("CommunityMapper", result)
        assert warnings == []

    def test_voice_miner_with_expected_keys(self):
        """VoiceMiner result with expected keys produces no warnings."""
        result = {
            "quotes": ["I hate invoicing"],
            "pain_points": ["time tracking"],
            "desires": ["automation"],
        }
        warnings = validate_agent_result("VoiceMiner", result)
        assert warnings == []

    def test_pricing_intel_with_expected_keys(self):
        """PricingIntel result with expected keys produces no warnings."""
        result = {
            "competitor_pricing": [{"name": "Tool A", "price": "$29/mo"}],
            "market_rates": {"range": "$20-50/mo"},
        }
        warnings = validate_agent_result("PricingIntel", result)
        assert warnings == []

    def test_competitor_profiler_with_expected_keys(self):
        """CompetitorProfiler result with expected keys produces no warnings."""
        result = {"competitors": [{"name": "Notion", "rating": 4.5}]}
        warnings = validate_agent_result("CompetitorProfiler", result)
        assert warnings == []

    def test_local_context_with_expected_keys(self):
        """LocalContext result with expected keys produces no warnings."""
        result = {
            "economic_context": {"gdp": "$500B"},
            "digital_landscape": {"internet_penetration": "85%"},
        }
        warnings = validate_agent_result("LocalContext", result)
        assert warnings == []

    def test_trend_detector_with_expected_keys(self):
        """TrendDetector result with expected keys produces no warnings."""
        result = {"trends": [{"topic": "AI tools", "direction": "up"}]}
        warnings = validate_agent_result("TrendDetector", result)
        assert warnings == []

    def test_opportunity_synthesizer_with_expected_keys(self):
        """OpportunitySynthesizer result with expected keys produces no warnings."""
        result = {"report": "# Market Research Report\n...", "executive_summary": "Summary here"}
        warnings = validate_agent_result("OpportunitySynthesizer", result)
        assert warnings == []

    def test_source_verifier_with_expected_keys(self):
        """SourceVerifier result with expected keys produces no warnings."""
        result = {
            "verification_score": 85,
            "sources": [{"url": "https://example.com", "status": "VERIFIED"}],
            "unsupported_claims": ["Claim X lacks citation"],
        }
        warnings = validate_agent_result("SourceVerifier", result)
        assert warnings == []

    def test_all_agents_covered_in_schema(self):
        """Every agent type in the orchestrator has a schema defined."""
        expected_agents = {
            "CommunityMapper",
            "VoiceMiner",
            "PricingIntel",
            "CompetitorProfiler",
            "LocalContext",
            "TrendDetector",
            "OpportunitySynthesizer",
            "SourceVerifier",
        }
        assert set(AGENT_SCHEMAS.keys()) == expected_agents


class TestResponseFallback:
    """Test that the 'response' fallback key passes validation."""

    @pytest.mark.parametrize(
        "agent_name",
        [
            "CommunityMapper",
            "VoiceMiner",
            "PricingIntel",
            "CompetitorProfiler",
            "LocalContext",
            "TrendDetector",
            "OpportunitySynthesizer",
            "SourceVerifier",
        ],
    )
    def test_response_fallback_passes_for_all_agents(self, agent_name):
        """When API returns non-JSON text, the 'response' key passes validation."""
        result = {"response": "This is a plain text response from the API."}
        warnings = validate_agent_result(agent_name, result)
        assert warnings == []


class TestErrorResults:
    """Test that error results pass validation (they have 'error' key)."""

    def test_error_result_passes(self):
        """A result with 'error' key produces no warnings."""
        result = {"error": "Agent timed out after 180s"}
        warnings = validate_agent_result("CommunityMapper", result)
        assert warnings == []

    def test_error_result_with_details_passes(self):
        """An error result with extra detail keys still passes."""
        result = {"error": "Rate limit exceeded", "retry_after": 30}
        warnings = validate_agent_result("VoiceMiner", result)
        assert warnings == []


class TestNoExpectedKeys:
    """Test that results with no expected keys produce warnings."""

    def test_completely_unexpected_keys(self):
        """Result with no matching expected keys produces a warning."""
        result = {"foo": "bar", "baz": 42}
        warnings = validate_agent_result("CommunityMapper", result)
        assert len(warnings) == 1
        assert "no expected keys" in warnings[0]
        assert "CommunityMapper" in warnings[0]

    def test_warning_lists_expected_keys(self):
        """Warning message includes what keys were expected."""
        result = {"unexpected": True}
        warnings = validate_agent_result("CompetitorProfiler", result)
        assert len(warnings) == 1
        assert "competitors" in warnings[0]
        assert "response" in warnings[0]

    def test_warning_lists_actual_keys(self):
        """Warning message includes the keys that were actually present."""
        result = {"wrong_key": "data"}
        warnings = validate_agent_result("TrendDetector", result)
        assert len(warnings) == 1
        assert "wrong_key" in warnings[0]


class TestEmptyValues:
    """Test that empty values produce warnings."""

    def test_none_value_warns(self):
        """A None value for an expected key produces a warning."""
        result = {"communities": None}
        warnings = validate_agent_result("CommunityMapper", result)
        assert len(warnings) == 1
        assert "empty" in warnings[0]
        assert "communities" in warnings[0]

    def test_empty_string_warns(self):
        """An empty string value for an expected key produces a warning."""
        result = {"report": ""}
        warnings = validate_agent_result("OpportunitySynthesizer", result)
        assert len(warnings) == 1
        assert "empty" in warnings[0]

    def test_empty_list_warns(self):
        """An empty list value for an expected key produces a warning."""
        result = {"competitors": []}
        warnings = validate_agent_result("CompetitorProfiler", result)
        assert len(warnings) == 1
        assert "empty" in warnings[0]

    def test_empty_dict_warns(self):
        """An empty dict value for an expected key produces a warning."""
        result = {"economic_context": {}}
        warnings = validate_agent_result("LocalContext", result)
        assert len(warnings) == 1
        assert "empty" in warnings[0]

    def test_multiple_empty_values_produce_multiple_warnings(self):
        """Multiple empty keys each produce their own warning."""
        result = {"quotes": [], "pain_points": None, "desires": "real data here"}
        warnings = validate_agent_result("VoiceMiner", result)
        assert len(warnings) == 2
        empty_keys_warned = [w for w in warnings if "empty" in w]
        assert len(empty_keys_warned) == 2

    def test_zero_value_does_not_warn(self):
        """A zero value (e.g. verification_score=0) should NOT produce an empty warning."""
        result = {"verification_score": 0, "sources": [{"url": "https://example.com"}]}
        warnings = validate_agent_result("SourceVerifier", result)
        assert warnings == []

    def test_false_value_does_not_warn(self):
        """A False value should NOT produce an empty warning."""
        result = {"trends": False}
        warnings = validate_agent_result("TrendDetector", result)
        assert warnings == []


class TestUnknownAgent:
    """Test that unknown agent names produce warnings."""

    def test_unknown_agent_warns(self):
        """An unrecognized agent name produces a warning."""
        result = {"data": "something"}
        warnings = validate_agent_result("MysteryAgent", result)
        assert len(warnings) == 1
        assert "unknown agent type" in warnings[0]
        assert "MysteryAgent" in warnings[0]


class TestNonDictResults:
    """Test that non-dict results produce warnings."""

    def test_string_result_warns(self):
        """A string result produces a warning."""
        warnings = validate_agent_result("CommunityMapper", "just a string")
        assert len(warnings) == 1
        assert "not a dict" in warnings[0]
        assert "str" in warnings[0]

    def test_list_result_warns(self):
        """A list result produces a warning."""
        warnings = validate_agent_result("VoiceMiner", ["item1", "item2"])
        assert len(warnings) == 1
        assert "not a dict" in warnings[0]
        assert "list" in warnings[0]

    def test_none_result_warns(self):
        """A None result produces a warning."""
        warnings = validate_agent_result("PricingIntel", None)
        assert len(warnings) == 1
        assert "not a dict" in warnings[0]
        assert "NoneType" in warnings[0]

    def test_int_result_warns(self):
        """An integer result produces a warning."""
        warnings = validate_agent_result("TrendDetector", 42)
        assert len(warnings) == 1
        assert "not a dict" in warnings[0]
        assert "int" in warnings[0]


class TestTokenUsageIgnored:
    """Test that _token_usage key is ignored during validation."""

    def test_token_usage_not_counted_as_unexpected(self):
        """_token_usage key should be excluded from key validation."""
        result = {
            "_token_usage": {"input_tokens": 1000, "output_tokens": 500},
            "communities": [{"name": "test"}],
        }
        warnings = validate_agent_result("CommunityMapper", result)
        assert warnings == []

    def test_token_usage_only_result_warns_no_expected_keys(self):
        """A result with ONLY _token_usage (no real data) produces a warning."""
        result = {"_token_usage": {"input_tokens": 100, "output_tokens": 50}}
        warnings = validate_agent_result("CommunityMapper", result)
        assert len(warnings) == 1
        assert "no expected keys" in warnings[0]

    def test_token_usage_with_unexpected_keys_warns(self):
        """_token_usage is ignored but other unexpected keys still trigger a warning."""
        result = {
            "_token_usage": {"input_tokens": 100, "output_tokens": 50},
            "wrong_key": "data",
        }
        warnings = validate_agent_result("CommunityMapper", result)
        assert len(warnings) == 1
        assert "no expected keys" in warnings[0]
        assert "_token_usage" not in warnings[0]
