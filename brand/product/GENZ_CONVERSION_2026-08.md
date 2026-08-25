# Gen Z conversion + brand alignment (2026-08)

**Source of truth:** `main` (also merged to `qa` / `dev` and active feature branches).  
**Positioning:** *BarathX is India’s conversation network for people with a point of view. Take a side, meet your community, and turn your voice into opportunity.*

## Shipped in this pass

| Review ask | Status |
|---|---|
| Defer 18+ / terms before value on landing | Done — landing is value-first; Privacy/Terms on signup |
| Soft-launch: remove 18+ age checkbox | Done — 18+ deferred to a later release; Privacy/Terms stay |
| Bot gate (Turnstile) + phone OTP preferred | Done — email/Google require Turnstile when keys set; phone skips |
| First-session human welcome replies | Done — ON by default (`DISABLE_FIRST_SESSION_ENGAGE=1` to off) |
| Human ranking (side + substance > AI) | Done — Square feed boosts sided + reacted takes; AI sinks |
| Report reasons + ops signup review flags | Done — post report chips; admin newest review flags |
| Invite real people (WA / IG / X + Circles) | Done — Home + Landing invite surface |
| Hero: “India has opinions. Now it has a home.” + safety promise | Done (`Landing.jsx`, `NativeLaunch.jsx`) |
| CTAs: Take today’s side / Watch the debate | Done |
| Agree / Disagree / **It depends** | Done — backend + Live debate UI |
| Hide empty “0 takes” | Done — `live.firstVoice` / `liveCopy.js` |
| Founding 100 benefit card + multi-path copy | Done — landing + Rewards + chip |
| Debate question as headline (shorten SCOOP titles) | Done — `debateHeadline()` |
| Desktop activity / proof strip | Done — landing proof row |
| Circles v1 (Campus & Careers, My City, Builders) | Done — under Arenas + seed + first-session join |
| First-session guarantee (side → take) | Done — reads `bx_landing_take`; requires stance before post |
| Substance reactions | Done — Helpful / Best counterpoint / Changed my mind |
| Native shareable cards | Done — canvas share after debate stance |
| Debate streak + high-value alerts | Done — IST streak on stance; Rewards + notifs at 3/7/14/30 |
| Co-host / clips / full week-1 onboarding | Still roadmap (below) |

## Roadmap (next product slices)

1. **More Circles:** Creator Corner, Desi Internet, Wellbeing, Regional Rooms  
2. **Live creator tools:** co-host, guest slots, clip highlights  
3. **First-week onboarding:** intent → language → auto-join 3 Circles → stance → fast reply loop  
4. **Founding multi-path scoring** in rewards engine (quality takes, helpful replies, hosting, referrals)  
5. **Language content lanes:** Tamil, Malayalam, Marathi, Bengali, Hinglish (UI already has EN/HI/TE)

## Branch alignment

Ship on `main`, then sync `qa` and `dev`. Hard-refresh the live site after Pages deploy so hashed assets are not stuck on SPA fallback cache.
