# Starting Prompt for Bolt

Copy and paste this into bolt.new, then upload the other 3 files when it asks or when you want to refine.

---

## The Prompt

```
Build a market research agent web app.

I'm uploading 3 reference files:
- 01-form-fields.md - the intake form structure
- 02-agent-prompts.md - what each research agent does
- 03-research-persona.md - quality evaluation guidelines

THE APP FLOW:

STEP 1 - INTAKE FORM
A clean form with these fields:
- What are you offering? (text)
- What problem does it solve? (textarea)
- Who is your target customer? (text)
- Target geography (text)
- Known competitors (text, comma separated)
- Research depth (dropdown: Quick Overview, Thorough, Deep Dive)
- #1 question you want answered (textarea)

STEP 2 - RESEARCH IN PROGRESS
After form submit, show a progress view with 6 research agents:
1. Community Mapper - finding where audience hangs out
2. Voice Miner - extracting customer quotes and pain points
3. Pricing Intel - competitor pricing and willingness to pay
4. Competitor Profiler - deep dive on competitors
5. Trend Detector - market momentum signals
6. Local Context - geography-specific factors

Each agent should:
- Call Claude API with its specific prompt (see 02-agent-prompts.md)
- Show status: pending → running (spinner) → complete (checkmark)
- Run in parallel for speed

After all 6 complete, run a 7th "Synthesizer" agent that combines all findings.

STEP 3 - RESULTS
- Display the final synthesized report in a nice markdown viewer
- Export buttons: Download as Markdown, Copy to Clipboard
- Option to start new research

TECHNICAL:
- Use Anthropic Claude API (claude-sonnet-4-20250514 model)
- API key stored in environment variable ANTHROPIC_API_KEY
- Clean, professional UI - consulting firm aesthetic
- Mobile responsive

Start with the intake form and basic layout, then we'll iterate.
```

---

## After Bolt Generates the First Version

You'll iterate with prompts like:
- "Make the form more polished, add better spacing"
- "Add a dark mode toggle"
- "Show estimated time remaining during research"
- "Add the ability to download as PDF"
- "The Voice Miner agent should use this exact prompt: [paste from 02-agent-prompts.md]"

Bolt works best with small iterations, not giant prompts.
