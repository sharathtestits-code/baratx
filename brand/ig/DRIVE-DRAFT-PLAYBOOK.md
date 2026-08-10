# Drive → Instagram publish playbook

**Folder:** [BarathX — AI Team](https://drive.google.com/drive/folders/16q4vDZWnIn4wFr5IEAXlswVHUH2lw6aF)  
**Parent brief:** `brand/SOCIAL-MARKETING-LEAD.md`

## Automation rule (follow exactly)

On each run:

1. List docs in that Drive folder whose title matches `Social Draft — ...`
2. **Ignore** any title that already starts with `[POSTED]`
3. If **one or more** unposted drafts exist, take the **oldest** (or only) one:
   - Read content — finished, real-data-based. **Do not rewrite or paraphrase.**
   - Only reformat for Instagram if needed (line breaks / hashtags) to match our pack style.
   - Post through existing IG publisher (`backend/app/instagram_publish.py` / admin carousel path), same pipeline as approved slots.
   - After a successful publish, **rename** that Drive doc title to prefix `[POSTED] ` so it is never picked up again.
4. If **no** matching unposted `Social Draft — ...` exists → **do nothing**. Do not invent or substitute a post.

## Visual / template variety

- Draft copy is sacred (no rewrite).
- Creative should **not** be the identical 6-slide grunge pack every time when a new draft arrives.
- Prefer: best current IG format for that draft’s job (carousel story, single still, or Reel *of a real debate* when footage exists).
- Pull a fresh template direction from what’s working online that week — still on-brand (street / human / not corporate), still BarathX spelling.
- If the Drive doc already includes or links to assets, use those.

## Blockers (must be resolved before this run can execute)

- [ ] Google Drive read + rename access for this agent (MCP, shared service account, or OAuth token in secrets)
- [ ] Confirm: caption-only drafts → which default visual pack / rotation rules
- [ ] Confirm: Drive posts **replace** a peak slot that day, or are **extra** on top of 09:00 / 13:30 / 20:00 Railway schedule

## Local ops notes

- IG credentials: `~/.config/baratx/instagram.env` / Railway vars
- Standing peak schedule remains separate unless founder says Drive drafts supersede it
- Spelling: **BarathX**
