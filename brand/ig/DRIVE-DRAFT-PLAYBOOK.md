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
- **Never** default to the same grunge pack every run — follow `brand/ig/FORMAT-ROTATION.md`.
- Pick format from what’s working for **product-launch** marketing *and* fits BarathX (Reels for reach, carousel for saves, UGC/raw for trust).
- If the Drive doc includes or links to assets / names a format → use that.
- Spelling on every pixel: **BarathX** (never BaratX).

## Access (resolved 2026-08-10)

- [x] Google Drive SA `barathx@baratx.iam.gserviceaccount.com` + folder shared Editor
- [x] Key path: `~/.config/baratx/google-drive.json` (also upload path under workspace uploads)
- [ ] Automation cloud runs still need the same key + IG token in **Cursor environment secrets** (not only this VM)
- [ ] Caption-only drafts → default visual: approved grunge pack unless draft links assets
- [x] Drive posts are **extra** when a draft exists; Railway 09:00 / 13:30 / 20:00 still runs unless disabled

## Local ops notes

- IG credentials: `~/.config/baratx/instagram.env` / Railway vars
- Standing peak schedule remains separate unless founder says Drive drafts supersede it
- Spelling: **BarathX**
