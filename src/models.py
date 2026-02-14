"""Data models for market research agent."""

from dataclasses import asdict, dataclass, field
from typing import Optional


@dataclass
class ResearchBrief:
    """Captures all intake information for a research project.

    Based on the 15 intake questions across 6 phases:
    - Phase 1: The Offering (4 questions)
    - Phase 2: Customer Hypothesis (3 questions)
    - Phase 3: Market Context (3 questions)
    - Phase 4: Business Reality (2 questions)
    - Phase 5: Research Priorities (3 questions)
    """

    # Required fields (no defaults)
    offering_what: str
    offering_problem: str
    target_customer: str
    geography: str
    primary_question: str

    # Optional fields (with defaults)
    # Phase 1: The Offering
    offering_delivery: Optional[str] = None
    offering_pricing_model: Optional[str] = None

    # Phase 2: Customer Hypothesis
    customer_conversations: Optional[str] = None
    segments_include_exclude: Optional[str] = None

    # Phase 3: Market Context
    known_competitors: list[str] = field(default_factory=list)
    opportunity_thesis: Optional[str] = None

    # Phase 4: Business Reality
    stage: Optional[str] = None  # exploring, committed, expanding, entering
    resources: Optional[str] = None

    # Phase 5: Research Priorities
    kill_criteria: Optional[str] = None
    already_known: Optional[str] = None

    # Metadata
    depth: str = "thorough"  # overview, thorough, deep_dive

    def __post_init__(self):
        """Validate fields after initialization."""
        # Validate required string fields are non-empty
        required_fields = {
            "offering_what": "What you're building",
            "offering_problem": "Problem it solves",
            "target_customer": "Target customer",
            "geography": "Geography/market",
            "primary_question": "Primary research question",
        }
        for field_name, label in required_fields.items():
            value = getattr(self, field_name)
            if not isinstance(value, str):
                raise TypeError(f"{label} must be a string, got {type(value).__name__}")
            stripped = value.strip()
            if not stripped:
                raise ValueError(f"{label} cannot be empty")
            # Store stripped version
            object.__setattr__(self, field_name, stripped)

        # Validate depth
        valid_depths = {"overview", "thorough", "deep_dive"}
        if self.depth not in valid_depths:
            raise ValueError(
                f"depth must be one of {valid_depths}, got '{self.depth}'"
            )

        # Strip whitespace from optional string fields
        optional_str_fields = [
            "offering_delivery", "offering_pricing_model",
            "customer_conversations", "segments_include_exclude",
            "opportunity_thesis", "stage", "resources",
            "kill_criteria", "already_known",
        ]
        for field_name in optional_str_fields:
            value = getattr(self, field_name)
            if isinstance(value, str):
                object.__setattr__(self, field_name, value.strip() or None)

        # Validate known_competitors is a list
        if not isinstance(self.known_competitors, list):
            raise TypeError(
                f"known_competitors must be a list, got {type(self.known_competitors).__name__}"
            )

    def to_dict(self) -> dict:
        """Serialize to dictionary for passing to agents."""
        return asdict(self)

    def to_markdown(self) -> str:
        """Render as markdown for saving to file."""
        lines = [
            "# Research Brief",
            "",
            "## The Offering",
            f"- **What:** {self.offering_what}",
            f"- **Problem Solved:** {self.offering_problem}",
        ]

        if self.offering_delivery:
            lines.append(f"- **Delivery Model:** {self.offering_delivery}")
        if self.offering_pricing_model:
            lines.append(f"- **Pricing Model:** {self.offering_pricing_model}")

        lines.extend([
            "",
            "## Customer Hypothesis",
            f"- **Target Customer:** {self.target_customer}",
        ])

        if self.customer_conversations:
            lines.append(f"- **Customer Conversations:** {self.customer_conversations}")
        if self.segments_include_exclude:
            lines.append(f"- **Include/Exclude:** {self.segments_include_exclude}")

        lines.extend([
            "",
            "## Market Context",
            f"- **Geography:** {self.geography}",
        ])

        if self.known_competitors:
            lines.append(f"- **Known Competitors:** {', '.join(self.known_competitors)}")
        if self.opportunity_thesis:
            lines.append(f"- **Opportunity Thesis:** {self.opportunity_thesis}")

        lines.extend([
            "",
            "## Business Reality",
        ])

        if self.stage:
            lines.append(f"- **Stage:** {self.stage}")
        if self.resources:
            lines.append(f"- **Resources:** {self.resources}")

        lines.extend([
            "",
            "## Research Priorities",
            f"- **#1 Question:** {self.primary_question}",
        ])

        if self.kill_criteria:
            lines.append(f"- **Kill Criteria:** {self.kill_criteria}")
        if self.already_known:
            lines.append(f"- **Already Known:** {self.already_known}")

        return "\n".join(lines)
