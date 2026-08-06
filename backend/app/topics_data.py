"""BaratX topic taxonomy — ~20 subtopics per arena (unpaid Path C).

Each topic has an RSS query for Google News (IN). Used to seed debate prompts.
"""

from __future__ import annotations

# arena_key → list of {key, name, blurb, rss_query}
TOPICS_BY_ARENA: dict[str, list[dict]] = {
    "sports": [
        {"key": "ipl", "name": "IPL", "blurb": "Auction, matches, rivalries.", "rss_query": "IPL cricket"},
        {"key": "team-india", "name": "Team India", "blurb": "Tests, ODIs, T20.", "rss_query": "Team India cricket"},
        {"key": "world-cup", "name": "World Cup", "blurb": "ICC events and knockouts.", "rss_query": "ICC World Cup cricket"},
        {"key": "football-isl", "name": "Football / ISL", "blurb": "ISL and national football.", "rss_query": "Indian Super League"},
        {"key": "kabaddi", "name": "Kabaddi", "blurb": "Pro Kabaddi heat.", "rss_query": "Pro Kabaddi"},
        {"key": "olympics", "name": "Olympics", "blurb": "India at the Games.", "rss_query": "India Olympics"},
        {"key": "badminton", "name": "Badminton", "blurb": "PV Sindhu, Lakshya, and more.", "rss_query": "India badminton"},
        {"key": "tennis", "name": "Tennis", "blurb": "Grand slams and Davis Cup.", "rss_query": "India tennis"},
        {"key": "hockey", "name": "Hockey", "blurb": "National team and leagues.", "rss_query": "India hockey"},
        {"key": "athletics", "name": "Athletics", "blurb": "Track, field, Neeraj.", "rss_query": "India athletics Neeraj"},
        {"key": "wrestling", "name": "Wrestling", "blurb": "Olympics and nationals.", "rss_query": "India wrestling"},
        {"key": "boxing", "name": "Boxing", "blurb": "Amateur and pro fights.", "rss_query": "India boxing"},
        {"key": "f1", "name": "F1 / Motorsport", "blurb": "Racing and Indian fans.", "rss_query": "Formula 1"},
        {"key": "nba", "name": "NBA", "blurb": "US basketball for India fans.", "rss_query": "NBA"},
        {"key": "esports", "name": "Esports", "blurb": "BGMI, Valorant, tournaments.", "rss_query": "India esports BGMI"},
        {"key": "ucl", "name": "Champions League", "blurb": "Europe nights.", "rss_query": "UEFA Champions League"},
        {"key": "sports-business", "name": "Sports Business", "blurb": "Rights, brands, salaries.", "rss_query": "India sports business"},
        {"key": "fantasy", "name": "Fantasy Sports", "blurb": "Dream11 and hot takes.", "rss_query": "Dream11 fantasy cricket"},
        {"key": "women-sports", "name": "Women's Sports", "blurb": "WPL and beyond.", "rss_query": "WPL women cricket India"},
        {"key": "local-sports", "name": "City Sports", "blurb": "Local leagues and school sports.", "rss_query": "India local sports league"},
    ],
    "politics": [
        {"key": "national", "name": "National Politics", "blurb": "Parliament and parties.", "rss_query": "India politics Parliament"},
        {"key": "elections", "name": "Elections", "blurb": "Votes, campaigns, results.", "rss_query": "India elections"},
        {"key": "policy", "name": "Policy", "blurb": "Bills, reforms, schemes.", "rss_query": "India government policy"},
        {"key": "economy-pol", "name": "Economy & Budget", "blurb": "Budget and growth fights.", "rss_query": "India Union Budget"},
        {"key": "foreign-policy", "name": "Foreign Policy", "blurb": "Neighbours and world stage.", "rss_query": "India foreign policy"},
        {"key": "state-politics", "name": "State Politics", "blurb": "CM fights and assemblies.", "rss_query": "India state elections"},
        {"key": "judiciary", "name": "Judiciary", "blurb": "Courts and constitution.", "rss_query": "India Supreme Court"},
        {"key": "defence", "name": "Defence", "blurb": "Forces and security.", "rss_query": "India defence"},
        {"key": "farmers", "name": "Farmers", "blurb": "Agri policy and protests.", "rss_query": "India farmers protest policy"},
        {"key": "jobs", "name": "Jobs & Youth", "blurb": "Employment and exams.", "rss_query": "India unemployment jobs"},
        {"key": "education-pol", "name": "Education Policy", "blurb": "NEP, exams, campuses.", "rss_query": "India education policy NEP"},
        {"key": "health-pol", "name": "Health Policy", "blurb": "Public health and insurance.", "rss_query": "India health policy"},
        {"key": "infra", "name": "Infrastructure", "blurb": "Roads, rail, cities.", "rss_query": "India infrastructure projects"},
        {"key": "digital-india", "name": "Digital India", "blurb": "Gov tech and data.", "rss_query": "Digital India UPI"},
        {"key": "caste-religion", "name": "Social Issues", "blurb": "Identity and society debates.", "rss_query": "India social issues politics"},
        {"key": "media-pol", "name": "Media & Free Speech", "blurb": "Press, platforms, speech.", "rss_query": "India free speech media"},
        {"key": "climate-pol", "name": "Climate Policy", "blurb": "Energy and environment law.", "rss_query": "India climate policy"},
        {"key": "urban", "name": "Urban Governance", "blurb": "Cities, civic bodies.", "rss_query": "India smart cities municipal"},
        {"key": "women-pol", "name": "Women & Politics", "blurb": "Representation and rights.", "rss_query": "India women reservation politics"},
        {"key": "corruption", "name": "Corruption & Scams", "blurb": "Accountability debates.", "rss_query": "India corruption scam"},
    ],
    "entertainment": [
        {"key": "bollywood", "name": "Bollywood", "blurb": "Hindi film fights.", "rss_query": "Bollywood"},
        {"key": "tollywood", "name": "Tollywood", "blurb": "Telugu cinema.", "rss_query": "Tollywood Telugu cinema"},
        {"key": "kollywood", "name": "Kollywood", "blurb": "Tamil cinema.", "rss_query": "Kollywood Tamil cinema"},
        {"key": "mollywood", "name": "Mollywood", "blurb": "Malayalam cinema.", "rss_query": "Mollywood Malayalam cinema"},
        {"key": "sandalwood", "name": "Sandalwood", "blurb": "Kannada cinema.", "rss_query": "Sandalwood Kannada cinema"},
        {"key": "ott", "name": "OTT / Streaming", "blurb": "Netflix, Prime, hot takes.", "rss_query": "India OTT Netflix Prime"},
        {"key": "music", "name": "Music", "blurb": "Albums, concerts, charts.", "rss_query": "India music Bollywood songs"},
        {"key": "reality-tv", "name": "Reality TV", "blurb": "Bigg Boss and contests.", "rss_query": "Bigg Boss India"},
        {"key": "celebrity", "name": "Celebrity", "blurb": "Stars and controversies.", "rss_query": "Bollywood celebrity news"},
        {"key": "web-series", "name": "Web Series", "blurb": "Indian originals.", "rss_query": "Indian web series"},
        {"key": "comedy", "name": "Comedy", "blurb": "Stand-up and sketches.", "rss_query": "India stand up comedy"},
        {"key": "gaming-ent", "name": "Gaming Culture", "blurb": "Creators and streams.", "rss_query": "India gaming YouTube"},
        {"key": "fashion", "name": "Fashion", "blurb": "Style and red carpets.", "rss_query": "India fashion Bollywood"},
        {"key": "awards", "name": "Awards", "blurb": "Filmfare, National, Oscars.", "rss_query": "Filmfare Awards India"},
        {"key": "theatre", "name": "Theatre & Arts", "blurb": "Stage and culture.", "rss_query": "India theatre arts"},
        {"key": "regional-ent", "name": "Regional Stars", "blurb": "Beyond the metros.", "rss_query": "Indian regional cinema"},
        {"key": "memes", "name": "Memes & Internet", "blurb": "Viral culture.", "rss_query": "India memes viral"},
        {"key": "podcasts", "name": "Podcasts", "blurb": "Audio culture.", "rss_query": "India podcasts"},
        {"key": "dance", "name": "Dance", "blurb": "Classical to reality shows.", "rss_query": "India dance reality show"},
        {"key": "hollywood", "name": "Indie & Alternative", "blurb": "Indie film and music.", "rss_query": "India indie film music"},
    ],
    "news": [
        {"key": "breaking", "name": "Breaking", "blurb": "What just happened.", "rss_query": "India breaking news"},
        {"key": "business", "name": "Business", "blurb": "Markets and companies.", "rss_query": "India business markets"},
        {"key": "tech", "name": "Tech", "blurb": "Startups and gadgets.", "rss_query": "India tech startups"},
        {"key": "startups", "name": "Startups", "blurb": "Funding and founders.", "rss_query": "India startup funding"},
        {"key": "markets", "name": "Markets", "blurb": "Sensex, Nifty, crypto.", "rss_query": "Nifty Sensex India"},
        {"key": "science", "name": "Science", "blurb": "ISRO and research.", "rss_query": "ISRO India science"},
        {"key": "climate", "name": "Climate", "blurb": "Weather and environment.", "rss_query": "India climate weather"},
        {"key": "health", "name": "Health", "blurb": "Public health stories.", "rss_query": "India health news"},
        {"key": "education", "name": "Education", "blurb": "Exams, colleges, edtech.", "rss_query": "India education news JEE"},
        {"key": "crime", "name": "Crime", "blurb": "Law and order stories.", "rss_query": "India crime news"},
        {"key": "cities", "name": "Cities", "blurb": "Metro life and civic news.", "rss_query": "Mumbai Delhi Bangalore news"},
        {"key": "world", "name": "World", "blurb": "Global news India cares about.", "rss_query": "world news India"},
        {"key": "opinion", "name": "Opinion", "blurb": "Editorials worth fighting.", "rss_query": "India opinion editorial"},
        {"key": "factcheck", "name": "Fact Check", "blurb": "Claims vs evidence.", "rss_query": "India fact check"},
        {"key": "transport", "name": "Transport", "blurb": "Rail, air, roads.", "rss_query": "India railways aviation"},
        {"key": "energy", "name": "Energy", "blurb": "Power, oil, renewables.", "rss_query": "India energy renewable"},
        {"key": "agriculture", "name": "Agriculture", "blurb": "Farms and food prices.", "rss_query": "India agriculture news"},
        {"key": "space", "name": "Space", "blurb": "ISRO missions.", "rss_query": "ISRO space mission"},
        {"key": "ai", "name": "AI & Future", "blurb": "AI in India and work.", "rss_query": "AI India technology"},
        {"key": "cyber", "name": "Cyber & Scams", "blurb": "Fraud and digital safety.", "rss_query": "India cyber crime scam"},
    ],
}


def all_topics() -> list[dict]:
    out = []
    for arena_key, rows in TOPICS_BY_ARENA.items():
        for row in rows:
            out.append({**row, "arena_key": arena_key})
    return out
