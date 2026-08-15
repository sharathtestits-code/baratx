# Hindi / Telugu language options — what it takes

BarathX is **English-first** at soft launch. The product already stores a per-user language preference (`en` | `hi` | `te`) on the profile API. Settings now exposes that picker.

## Already in place

| Piece | Status |
| --- | --- |
| User `language` column + API (`en` / `hi` / `te`) | Done (backend) |
| Settings → Language picker | Done (saves preference + `html[lang]`) |
| Full Hindi / Telugu UI strings | **Not built** — English chrome remains |
| Translated Square questions / suggestions | **Not built** |
| Moderation + LLM prompts per language | **Not built** |

## To ship real Hindi / Telugu UI

1. **i18n framework** — Add a message catalog (e.g. `react-i18next` or a tiny custom dictionary) keyed by string id. Wrap chrome: nav, Settings, Empty states, compose labels, errors, FAQ, legal summaries.
2. **String extraction** — Inventory ~400–800 UI strings across plaza pages; translate to Hindi and Telugu with a native reviewer (machine draft + human edit).
3. **Fonts** — Ensure Devanagari (Hindi) and Telugu glyphs render in display + body fonts; fall back stacks that include Noto Sans Devanagari / Noto Sans Telugu.
4. **Layout** — Some Hindi/Telugu labels are longer; check BottomNav, buttons, and rail chips for wrap/overflow.
5. **Content rails** — Today’s Square, Top questions, starter prompts, Arena topics, and suggestion ranking need language-aware sources (or bilingual items), not only chrome translation.
6. **UGC** — Users already post in any script; no force. Optional: language tag on posts for filtering later.
7. **Ops / AI** — Moderation classifiers and reply assistants need hi/te coverage or explicit “English-only assist” until then.
8. **QA** — Spot-check Square, Arenas, Live, Settings, auth, and soft-launch landing in each locale on mobile + desktop.

## Phased recommendation

| Phase | Scope |
| --- | --- |
| **P0 (this ship)** | Preference picker + `lang` attribute + docs. English UI stays. |
| **P1** | Translate plaza chrome (Square / Arenas / Live / Settings / nav) for `hi` + `te`. **Done — selecting language updates UI live.** |
| **P2** | Language-aware suggestions + Today’s Square + empty-state copy. |
| **P3** | Landing / FAQ / legal + moderation assist. |

English remains the default for anyone who never picks a language.
