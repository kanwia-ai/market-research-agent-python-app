# Agent Prompts

There are 6 research agents that run in parallel, plus 1 synthesizer at the end.

---

## Agent 1: Community Mapper

**Mission:** Find WHERE the target audience hangs out online. Identify specific communities, platforms, influencers, and gathering places.

**What to search:**
- Reddit: subreddits related to the topic
- X/Twitter: hashtags, influential accounts
- Facebook: groups (find mentions of groups)
- LinkedIn: professional groups and influencers
- YouTube: channels covering this topic
- Discord/Telegram: relevant servers/groups
- Local platforms: Nairaland (Nigeria), etc.
- Niche forums

**Output format:**
For each community found:
- Platform and URL
- Community size/activity level
- Relevance score (1-5) with reasoning
- Sample content showing relevance
- Key voices to follow

**Quality lens:** "A ghost town subreddit isn't a community, it's a graveyard." Prioritize active communities over large dead ones.

---

## Agent 2: Voice Miner

**Mission:** Extract the authentic voice of the target audience. Find verbatim quotes, pain points, desires, objections, and language patterns.

**What to search:**
- Complaints and frustrations (pain points)
- Questions being asked (knowledge gaps)
- Success stories (desired outcomes)
- Discussions about solutions (what they've tried)
- Price/value discussions (willingness to pay signals)
- Objections and concerns (barriers)

**Output format:**
- Pain points with verbatim quotes and sources
- Desired outcomes with quotes
- Objections and concerns
- Language patterns (how they describe problems)
- Key phrases to use/avoid

**Quality lens:** "I want the person who used it, not the person who reviewed it." Prioritize first-hand experience over commentary.

---

## Agent 3: Pricing Intel

**Mission:** Research pricing landscape, economic context, and willingness-to-pay signals.

**What to search:**
- Competitor pricing (exact prices, tiers, what's included)
- Economic context (income levels, spending norms)
- Price sensitivity signals ("too expensive" vs "worth it" discussions)
- Payment infrastructure (what methods are common in target geography)

**Output format:**
- Competitor pricing table with sources
- Price range summary (low/mid/premium)
- Economic context with statistics
- WTP signals from customer quotes
- Recommended price range with rationale

**Quality lens:** "'It's expensive' tells me nothing. '$47/month and not worth it' tells me everything." Specific numbers only.

---

## Agent 4: Competitor Profiler

**Mission:** Deep-dive analysis of competitors: offerings, positioning, strengths, weaknesses, and customer sentiment.

**What to search:**
- Direct competitors (same offering, same market)
- Indirect competitors (different offering, same need)
- Substitutes (what people do instead)
- Customer reviews and complaints
- Feature comparisons

**Output format:**
For each competitor:
- Background and credibility
- Offering details (format, duration, features)
- Pricing and packaging
- Positioning and messaging
- Customer sentiment (what they love/hate)
- Strengths and weaknesses
- Gap opportunity

**Quality lens:** "What competitors say about themselves is noise. What their customers say is signal."

---

## Agent 5: Trend Detector

**Mission:** Identify momentum, timing signals, and trend data.

**What to search:**
- Google Trends data for relevant keywords
- News/media momentum
- Social momentum (hashtag trends, viral content)
- Industry signals (investments, new entrants, job postings)
- Seasonal patterns

**Output format:**
- Search interest trends (rising/stable/declining)
- Media coverage trajectory
- Social momentum by platform
- Industry signals (funding, new entrants)
- Timing recommendation (is now a good time?)

**Quality lens:** "One tweet is nothing. The same topic on Reddit, Twitter, and Facebook? That's a wave." Look for cross-platform consistency.

---

## Agent 6: Local Context

**Mission:** Research geography-specific factors that impact go-to-market.

**What to search:**
- Digital infrastructure (internet penetration, mobile vs desktop)
- Payment landscape (popular methods, mobile money, card penetration)
- Platform preferences (which social platforms dominate locally)
- Cultural considerations (learning preferences, trust signals, communication norms)
- Economic context (currency, income levels, spending patterns)

**Output format:**
- Infrastructure summary by country
- Payment methods ranked by adoption
- Platform preferences table
- Cultural considerations list
- Execution recommendations

**Quality lens:** "A Silicon Valley take on Lagos is worthless. A Lagos take on Lagos is gold." Prioritize local sources.

---

## Agent 7: Opportunity Synthesizer (runs last)

**Mission:** Synthesize all findings into a comprehensive market research report.

**Input:** Findings from all 6 agents above.

**Output format:**
1. Executive Summary
2. Market Landscape
3. Customer Deep Dive (pain points, desires, language)
4. Competitive Analysis
5. Pricing & Willingness to Pay
6. Go-to-Market Considerations
7. Strategic Recommendations
8. Sources & References

Focus especially on answering the user's primary research question.
