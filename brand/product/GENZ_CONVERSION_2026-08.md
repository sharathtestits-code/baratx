# Gen Z conversion + brand alignment (2026-08)

**Source of truth:** `main` (also merged to `qa` / `dev` and active feature branches).  
**Positioning:** *BarathX is India’s conversation network for people with a point of view. Take a side, meet your community, and turn your voice into opportunity.*

## Shipped in this pass

| Review ask | Status |
|---|---|
| Defer 18+ / terms before value on landing | Done — consent stays on **Signup** / optional Google; landing shows today’s question first |
| Hero: “India has opinions. Now it has a home.” + safety promise | Done (`Landing.jsx`, `NativeLaunch.jsx`) |
| CTAs: Take today’s side / Watch the debate | Done |
| Agree / Disagree / **It depends** | Done — backend + Live debate UI |
| Hide empty “0 takes” | Done — `live.firstVoice` / `liveCopy.js` |
| Founding 100 benefit card + multi-path copy | Done — landing + Rewards + chip |
| Debate question as headline (shorten SCOOP titles) | Done — `debateHeadline()` |
| Desktop activity / proof strip | Done — landing proof row |
| Circles teaser (campus, city, language…) | Teaser on landing; full Circles product still roadmap |
| Co-host / clips / new reactions / full week-1 onboarding | Roadmap (below) |

## Roadmap (next product slices)

1. **Circles** under Arenas: Campus & Careers, Builders, Creator Corner, My City, Desi Internet, Wellbeing, Regional Rooms  
2. **Substance reactions:** Best counterpoint / Helpful / Changed my mind  
3. **Live creator tools:** co-host, guest slots, clip highlights  
4. **First-week onboarding:** intent → language/city → auto-join 3 Circles → stance → one-sentence reason → fast reply loop  
5. **Founding multi-path scoring** in rewards engine (quality takes, helpful replies, hosting, referrals)  
6. **Language content lanes:** Tamil, Malayalam, Marathi, Bengali, Hinglish (UI already has EN/HI/TE)

## Branch alignment

Ship on **`main`**. Sync **`qa`**, **`dev`**, and the active agent branch after each release so orgs/environments do not drift.
