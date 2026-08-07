# BaratX AI Assist — what it is now vs what we can give

## What it does **today**
`AI Assist` on Square compose is **not** connected to any model (no OpenAI / Gemini / Claude).

Current behavior (`Feed.jsx`):
- Tapping **AI Assist** fills an empty compose box with a **local starter line**, e.g.
  - “In my city, the real take is …”
  - “Hot take: India needs to stop pretending …”
- No API call. No generated answer from news, debates, or user history.

## Where answers would come from (options we can ship)
| Mode | Source | Good for |
|------|--------|----------|
| **A. Prompt starters** (now) | Hardcoded / curated India hooks | Instant, free, no privacy risk |
| **B. BaratX context** | User’s arenas/topics + open debates + their last posts | “Continue this debate”, side-aware drafts |
| **C. Credible news** | Same RSS allowlist as daily digest | Civic / News takes grounded in real headlines |
| **D. Full LLM** | OpenAI / Gemini / Claude with BaratX system prompt | Rewrite, shorten, argue For/Against, translate EN↔HI |

Recommended product path: **A → B → C**, then optional **D** behind a toggle (“AI rewrite”).

## What we can give users (product copy)
1. **Starter** — empty-box hooks (live now)
2. **Rewrite** — polish user’s draft (tone: sharp / civic / funny)
3. **Argue my side** — 1-sentence For/Against for the open debate
4. **From today’s Square** — draft tied to a digest headline
5. **Translate** — English ↔ Hindi (later Telugu)

## Guardrails if we add a model
- Never invent facts for civic posts; cite digest headline when used
- Don’t auto-post — only fill the composer
- Label AI-assisted drafts clearly if required
- Keep a kill switch + cost cap

## Env (when wiring a real model)
```
AI_ASSIST_PROVIDER=openai|gemini|none
AI_ASSIST_API_KEY=...
AI_ASSIST_MODEL=...
```
Default `none` keeps today’s starter behavior.
