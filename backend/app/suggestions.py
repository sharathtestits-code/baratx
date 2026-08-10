"""
Top problem / question suggestions for Square + Arenas.

Sources (in order):
1. Open debate Space titles (live product context)
2. Curated India prompts per arena
3. Optional LLM rewrite/rank when AI_ASSIST_PROVIDER + AI_ASSIST_API_KEY are set

Never auto-posts. Kill switch: AI_ASSIST_PROVIDER=none (default).
"""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from typing import Optional

from sqlalchemy.orm import Session

from app import models

logger = logging.getLogger("baratx.suggestions")

ARENA_KEYS = ("sports", "politics", "entertainment", "news", "spirituality", "startups")

CURATED: dict[str, list[str]] = {
    "square": [
        "What’s one thing India gets wrong in public debate?",
        "What should this public square never become?",
        "Drop your hottest take on startups in India.",
        "Who should every BarathX user follow in your city?",
        "Is Gen Z actually faster — or are Reels just farming attention?",
        "What’s a small India habit that should be a national flex?",
        "Which India story do global feeds keep getting wrong?",
        "Would you rather fix traffic or fix exams first — and why?",
        "What’s the most overrated “hustle” advice you still hear?",
        "Name one policy your city could ship this year that isn’t a slogan.",
        "Cricket: Test purity or T20 energy — pick a side.",
        "When did online India stop arguing in good faith?",
        "What’s the best food fight between two Indian cities?",
        "If you had ₹150 and one week, what would you ship?",
        "Should offices ban AI drafts in public posts — yes or no?",
        "What’s one campus truth adults refuse to say out loud?",
        "Is “tier-2 city” a chip or a brand now?",
        "What should Founding voices get paid for — rooms or replies?",
        "Which Bollywood / regional trope needs to retire in 2026?",
        "What does ‘human takes only’ mean to you personally?",
    ],
    "sports": [
        "Test cricket still the purest format — fight me.",
        "Kohli vs the next gen: who’s actually carrying Indian batting?",
        "Should IPL auctions be more transparent to fans?",
        "Is football’s boom in India real or metro hype?",
        "Olympics: which sport deserves serious funding next?",
        "Are fantasy sports apps good for cricket culture or just gambling with branding?",
        "Women’s cricket visibility: progress or PR?",
        "Should national teams ignore social media pile-ons?",
        "Esports — real sport or content category?",
        "What’s the most underrated Indian athlete right now?",
        "Stadium food vs street food: which wins match day?",
        "Do we romanticize struggle stories in sports too much?",
        "Asia Cup / World Cup pressure: media or players?",
        "Should school sports be graded like exams?",
        "Pick a side: morning run culture vs evening gym culture.",
        "Is franchise cricket killing domestic cricket?",
        "What’s one rule change you’d make in cricket tomorrow?",
        "Kabaddi / kho-kho — mainstream or forever niche?",
        "Athletes and politics: speak up or stay quiet?",
        "What’s a sports take you’ll defend at a family dinner?",
    ],
    "politics": [
        "What’s one thing India gets wrong in public debate?",
        "Local proof > TV panel — what’s your state’s example?",
        "Should cities publish weekly traffic / flood dashboards?",
        "Freebies vs infrastructure: false choice or real tradeoff?",
        "What’s a policy lever more people should name out loud?",
        "Parliament disruption: tactic or failure?",
        "Federalism: who should own urban planning — Centre or city?",
        "What’s the most overused political slogan this year?",
        "Can social media outrage ever improve governance?",
        "Reservation debates: what question are we avoiding?",
        "Police reforms: where would you start?",
        "Should voting be a national holiday with teeth?",
        "Data privacy vs national security — where’s your line?",
        "What’s one municipal job that deserves celebrity energy?",
        "Farm / labor / gig — which worker story is most ignored?",
        "Is ‘both sides’ journalism lazy in 2026?",
        "What would make you trust a political poll again?",
        "Youth turnout: apathy or blocked pathways?",
        "Name a boring reform that would change daily life.",
        "When should platforms take down political deepfakes?",
    ],
    "entertainment": [
        "Which film trope needs to retire in 2026?",
        "OTT: too many shows, too little finish — agree?",
        "Regional cinema vs Bollywood budget — who’s winning culture?",
        "Are award shows still relevant?",
        "Music: algorithm playlists or albums — how do you listen?",
        "Should celebrities disclose brand deals more clearly?",
        "Is cancel culture real in Indian fandoms or just pile-ons?",
        "Best city for live music right now?",
        "Reels comedy vs stand-up — what’s actually funny?",
        "Nepotism debates: useful or circular?",
        "What’s an underrated Indian series people skip?",
        "Sports biopics: inspiring or same template?",
        "Should theatres get a comeback subsidy?",
        "Influencers as actors — good casting or lazy casting?",
        "What’s the last movie that changed how you argue?",
        "Dance reality TV: skill or drama product?",
        "Language dubbing: access win or culture loss?",
        "Who’s a creator you’d follow offline?",
        "Is ‘content’ killing craft?",
        "Pick a side: long films or tight 100 minutes.",
    ],
    "news": [
        "Which India story do global feeds keep getting wrong?",
        "Headline vs reality: what’s overblown this week?",
        "Should news apps kill push alerts for soft stories?",
        "Source quality: how do you decide what’s credible?",
        "Is breaking news addiction worse than doomscrolling?",
        "Local journalism: would you pay ₹99/month for your city?",
        "AI summaries of news — helpful or dangerous?",
        "What’s a story that needed slower reporting?",
        "TV debates: theatre or accountability?",
        "When should journalists refuse anonymous sources?",
        "Climate coverage: guilt trip or usable facts?",
        "Startup media vs legacy media — trust gap?",
        "Should platforms amplify PIB / PTI more?",
        "What’s the most useful beat nobody funds?",
        "Rumours vs reporting in election season — your rule?",
        "Is ‘both sides’ failing science stories?",
        "City crime coverage: fear or public service?",
        "What notification would you keep and delete the rest?",
        "Can citizen video replace reporters?",
        "Name one outlet you’ll still defend.",
    ],
    "spirituality": [
        "Faith in public life: personal or political?",
        "Are personality tests the new IQ tests for the soul?",
        "Ritual vs meaning — what still feels real to you?",
        "Should workplaces ignore religious calendars?",
        "Meditation apps: practice or product?",
        "Interfaith friendships: what’s hard to say politely?",
        "Astrology content: harmless fun or decision engine?",
        "What tradition from your family do you keep?",
        "Temples / mosques / churches as community hubs — still true?",
        "Can atheism be a respectful public stance in India?",
        "Festivals: culture first or commerce first?",
        "What’s a spiritual claim you’d challenge kindly?",
        "Pilgrimage vs vacation — where’s the line?",
        "Should schools teach comparative religion neutrally?",
        "Online gurus: who do you trust and why?",
        "Silence as a practice — ever tried it weekly?",
        "Charity: religion-coded or civic?",
        "What’s sacred to you that isn’t religious?",
        "Food rules and modern life — negotiate or drop?",
        "Pick a side: private faith, public kindness.",
    ],
    "startups": [
        "Drop your hottest take on startups in India.",
        "Pitch decks vs boring constraints — what actually decides winners?",
        "If you had ₹150 and one week, what would you ship?",
        "Layoffs: market cycle or culture debt?",
        "Tier-2 founders: advantage or romantic myth?",
        "Should India copy Silicon Valley culture at all?",
        "Fund it or pass: what’s your bar for a consumer app?",
        "AI wrappers — real business or demo theatre?",
        "What’s the most dishonest metric founders still brag about?",
        "Remote vs office for early teams?",
        "Government startup schemes: useful or paperwork?",
        "Who should earn a Founding 100 spot — rooms or replies?",
        "Hiring: pedigree or proof of work?",
        "What’s broken in Indian SaaS go-to-market?",
        "Creator → founder path: overhyped?",
        "Would you take VC if it meant moving cities?",
        "Open source in India — where’s the missing piece?",
        "Customer support as a moat — agree?",
        "What’s one regulation that helps honest startups?",
        "Build in public: bravery or marketing?",
    ],
}


def _provider() -> str:
    return (os.environ.get("AI_ASSIST_PROVIDER") or "none").strip().lower()


def _openai_rank(prompts: list[str], *, arena: str) -> Optional[list[str]]:
    key = (os.environ.get("AI_ASSIST_API_KEY") or "").strip()
    if not key:
        return None
    model = (os.environ.get("AI_ASSIST_MODEL") or "gpt-4o-mini").strip()
    system = (
        "You help BarathX, India's public square. "
        "Return JSON {\"items\":[\"...\"]} — up to 20 short debate questions, "
        "human, India-specific, no AI-slop tone, no hashtags. "
        "Prefer concrete civic/culture/startup tension over generic advice."
    )
    user = (
        f"Arena/surface: {arena}\n"
        f"Seed questions:\n- " + "\n- ".join(prompts[:24]) + "\n"
        "Rewrite/rank the best 15–20. Keep them askable as posts."
    )
    payload = {
        "model": model,
        "temperature": 0.4,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "User-Agent": "BarathX/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
        content = raw["choices"][0]["message"]["content"]
        data = json.loads(content)
        items = data.get("items") or data.get("questions") or []
        out = [str(x).strip() for x in items if str(x).strip()]
        return out[:20] or None
    except Exception:  # noqa: BLE001
        logger.exception("AI suggestion rank failed")
        return None


def _live_debate_titles(db: Session, arena_key: Optional[str], limit: int = 8) -> list[str]:
    q = (
        db.query(models.Space)
        .filter(models.Space.status == "open")
        .filter(models.Space.kind == "debate")
    )
    if arena_key and arena_key in ARENA_KEYS:
        q = q.outerjoin(models.Topic, models.Topic.id == models.Space.topic_id).filter(
            models.Topic.arena_key == arena_key
        )
    rows = q.order_by(models.Space.created_at.desc()).limit(limit).all()
    out = []
    for s in rows:
        title = (s.title or "").strip()
        if title and title not in out:
            out.append(title if "?" in title else f"Take: {title}")
    return out


def list_suggestions(
    db: Session,
    *,
    surface: str = "square",
    arena_key: Optional[str] = None,
    limit: int = 20,
) -> dict:
    limit = max(5, min(int(limit or 20), 20))
    surface = (surface or "square").strip().lower()
    arena = (arena_key or "").strip().lower() or None

    if surface == "arena" and arena in CURATED:
        bucket = arena
    elif arena in CURATED:
        bucket = arena
    else:
        bucket = "square"

    curated = list(CURATED.get(bucket) or CURATED["square"])
    live = _live_debate_titles(db, arena if surface == "arena" else None)
    merged: list[str] = []
    for item in live + curated:
        if item not in merged:
            merged.append(item)

    source = "curated+live"
    provider = _provider()
    if provider in ("openai", "openai-compatible") and merged:
        ranked = _openai_rank(merged, arena=bucket)
        if ranked:
            merged = ranked
            source = f"llm:{provider}"

    return {
        "ok": True,
        "surface": surface,
        "arena_key": arena,
        "source": source,
        "items": [{"text": t, "id": f"{bucket}-{i}"} for i, t in enumerate(merged[:limit])],
    }
