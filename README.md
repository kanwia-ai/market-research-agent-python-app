# Market Research App

A Python/Streamlit application that conducts comprehensive market research using AI-powered sub-agents. Built with Claude API integration for professional-grade research reports.

## Features

- **15-Question Intake Process**: Comprehensive research brief collection
- **8 Specialized Research Agents**:
  - Community Mapper - Finds where your audience hangs out online
  - Voice Miner - Extracts verbatim quotes and pain points
  - Pricing Intel - Analyzes pricing landscape and willingness-to-pay
  - Competitor Profiler - Deep-dives on competitor offerings
  - Local Context - Geography-specific market factors
  - Trend Detector - Identifies momentum and timing signals
  - Opportunity Synthesizer - Creates the final comprehensive report
  - Source Verifier - Validates all citations and sources

- **5-Wave Orchestrated Execution**: Agents run in optimized parallel waves
- **Mandatory Source Citations**: Every claim includes verifiable URLs
- **Professional Reports**: 15-30 page McKinsey-quality deliverables

## Installation

```bash
# Clone the repository
git clone https://github.com/kanwia-ai/market-research-app.git
cd market-research-app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

## Usage

Run the Streamlit app:

```bash
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

## Project Structure

```
market-research-app/
├── app.py                 # Streamlit UI
├── src/
│   ├── models.py          # ResearchBrief data model
│   ├── agents.py          # 8 research sub-agents
│   └── orchestrator.py    # 5-wave execution orchestrator
├── tests/                 # pytest test suite
├── .streamlit/
│   └── config.toml        # Streamlit theme configuration
├── requirements.txt       # Python dependencies
└── pyproject.toml         # Project configuration
```

## Running Tests

```bash
pytest tests/ -v
```

## Research Depth Options

- **Quick Overview**: Key insights and market snapshot
- **Thorough Analysis**: Comprehensive findings with strategic recommendations
- **Deep Dive**: Exhaustive research leaving no stone unturned

## License

MIT

## Related

- [Claude Code Skill Version](https://github.com/kanwia-ai/market-research-agent) - The original Claude Code skill implementation
