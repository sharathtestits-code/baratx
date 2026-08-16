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
        "Is Gen Z actually faster, or are Reels just farming attention?",
        "What’s a small India habit that should be a national flex?",
        "Which India story do global feeds keep getting wrong?",
        "Would you rather fix traffic or fix exams first, and why?",
        "What’s the most overrated “hustle” advice you still hear?",
        "Name one policy your city could ship this year that isn’t a slogan.",
        "Cricket: Test purity or T20 energy, pick a side.",
        "When did online India stop arguing in good faith?",
        "What’s the best food fight between two Indian cities?",
        "If you had ₹150 and one week, what would you ship?",
        "Should offices ban AI drafts in public posts, yes or no?",
        "What’s one campus truth adults refuse to say out loud?",
        "Is “tier-2 city” a chip or a brand now?",
        "What should Founding voices get paid for, rooms or replies?",
        "Which Bollywood / regional trope needs to retire in 2026?",
        "What does ‘human takes only’ mean to you personally?",
    ],
    "sports": [
        "Test cricket still the purest format, fight me.",
        "Kohli vs the next gen: who’s actually carrying Indian batting?",
        "Should IPL auctions be more transparent to fans?",
        "Is football’s boom in India real or metro hype?",
        "Olympics: which sport deserves serious funding next?",
        "Are fantasy sports apps good for cricket culture or just gambling with branding?",
        "Women’s cricket visibility: progress or PR?",
        "Should national teams ignore social media pile-ons?",
        "Esports, real sport or content category?",
        "What’s the most underrated Indian athlete right now?",
        "Stadium food vs street food: which wins match day?",
        "Do we romanticize struggle stories in sports too much?",
        "Asia Cup / World Cup pressure: media or players?",
        "Should school sports be graded like exams?",
        "Pick a side: morning run culture vs evening gym culture.",
        "Is franchise cricket killing domestic cricket?",
        "What’s one rule change you’d make in cricket tomorrow?",
        "Kabaddi / kho-kho, mainstream or forever niche?",
        "Athletes and politics: speak up or stay quiet?",
        "What’s a sports take you’ll defend at a family dinner?",
        "Badminton: is India still underfunding medal sports?",
        "Chess boom: Gukesh effect or lasting pipeline?",
        "Hockey: do we still treat it like a forgotten Olympic sport?",
        "Table tennis / tennis, which deserves a bigger India league?",
    ],
    "politics": [
        "What’s one thing India gets wrong in public debate?",
        "Local proof > TV panel, what’s your state’s example?",
        "Should cities publish weekly traffic / flood dashboards?",
        "Freebies vs infrastructure: false choice or real tradeoff?",
        "What’s a policy lever more people should name out loud?",
        "Parliament disruption: tactic or failure?",
        "Federalism: who should own urban planning. Centre or city?",
        "What’s the most overused political slogan this year?",
        "Can social media outrage ever improve governance?",
        "Reservation debates: what question are we avoiding?",
        "Police reforms: where would you start?",
        "Should voting be a national holiday with teeth?",
        "Data privacy vs national security, where’s your line?",
        "What’s one municipal job that deserves celebrity energy?",
        "Farm / labor / gig, which worker story is most ignored?",
        "Is ‘both sides’ journalism lazy in 2026?",
        "What would make you trust a political poll again?",
        "Youth turnout: apathy or blocked pathways?",
        "Name a boring reform that would change daily life.",
        "When should platforms take down political deepfakes?",
    ],
    "entertainment": [
        "Which film trope needs to retire in 2026?",
        "OTT: too many shows, too little finish, agree?",
        "Regional cinema vs Bollywood budget, who’s winning culture?",
        "Are award shows still relevant?",
        "Music: algorithm playlists or albums, how do you listen?",
        "Should celebrities disclose brand deals more clearly?",
        "Is cancel culture real in Indian fandoms or just pile-ons?",
        "Best city for live music right now?",
        "Reels comedy vs stand-up, what’s actually funny?",
        "Nepotism debates: useful or circular?",
        "What’s an underrated Indian series people skip?",
        "Sports biopics: inspiring or same template?",
        "Should theatres get a comeback subsidy?",
        "Influencers as actors, good casting or lazy casting?",
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
        "AI summaries of news, helpful or dangerous?",
        "What’s a story that needed slower reporting?",
        "TV debates: theatre or accountability?",
        "When should journalists refuse anonymous sources?",
        "Climate coverage: guilt trip or usable facts?",
        "Startup media vs legacy media, trust gap?",
        "Should platforms amplify PIB / PTI more?",
        "What’s the most useful beat nobody funds?",
        "Rumours vs reporting in election season, your rule?",
        "Is ‘both sides’ failing science stories?",
        "City crime coverage: fear or public service?",
        "What notification would you keep and delete the rest?",
        "Can citizen video replace reporters?",
        "Name one outlet you’ll still defend.",
    ],
    "spirituality": [
        "Faith in public life: personal or political?",
        "Are personality tests the new IQ tests for the soul?",
        "Ritual vs meaning, what still feels real to you?",
        "Should workplaces ignore religious calendars?",
        "Meditation apps: practice or product?",
        "Interfaith friendships: what’s hard to say politely?",
        "Astrology content: harmless fun or decision engine?",
        "What tradition from your family do you keep?",
        "Temples / mosques / churches as community hubs, still true?",
        "Can atheism be a respectful public stance in India?",
        "Festivals: culture first or commerce first?",
        "What’s a spiritual claim you’d challenge kindly?",
        "Pilgrimage vs vacation, where’s the line?",
        "Should schools teach comparative religion neutrally?",
        "Online gurus: who do you trust and why?",
        "Silence as a practice, ever tried it weekly?",
        "Charity: religion-coded or civic?",
        "What’s sacred to you that isn’t religious?",
        "Food rules and modern life, negotiate or drop?",
        "Pick a side: private faith, public kindness.",
    ],
    "startups": [
        "Drop your hottest take on startups in India.",
        "Pitch decks vs boring constraints, what actually decides winners?",
        "If you had ₹150 and one week, what would you ship?",
        "Layoffs: market cycle or culture debt?",
        "Tier-2 founders: advantage or romantic myth?",
        "Should India copy Silicon Valley culture at all?",
        "Fund it or pass: what’s your bar for a consumer app?",
        "AI wrappers, real business or demo theatre?",
        "What’s the most dishonest metric founders still brag about?",
        "Remote vs office for early teams?",
        "Government startup schemes: useful or paperwork?",
        "Who should earn a Founding 100 spot, rooms or replies?",
        "Hiring: pedigree or proof of work?",
        "What’s broken in Indian SaaS go-to-market?",
        "Creator → founder path: overhyped?",
        "Would you take VC if it meant moving cities?",
        "Open source in India, where’s the missing piece?",
        "Customer support as a moat, agree?",
        "What’s one regulation that helps honest startups?",
        "Build in public: bravery or marketing?",
    ],
}

# Per-topic prompts (arena subtopics). Used when client passes topic=badminton etc.
CURATED_BY_TOPIC: dict[str, list[str]] = {
    "ipl": [
        "IPL auctions: skill market or drama product?",
        "Should overseas players still dominate IPL bowling?",
        "Which IPL franchise culture is most toxic, and why?",
        "Impact player rule: smart cricket or gimmick?",
        "Is IPL killing Test cricket or funding it?",
        "Pick a side: purple cap chase vs team first bowling.",
        "What’s one IPL rule you’d scrap tomorrow?",
        "Are IPL cheer/entertainment bits past their time?",
        "Retention vs auction: which builds stronger sides?",
        "IPL finals pressure: captains or coaches?",
        "Should IPL expand more teams or protect quality?",
        "Fantasy points vs real cricket, are fans watching the wrong game?",
        "Women’s IPL energy vs men’s circus, what’s the gap?",
        "Neutral venues: fairness or boring cricket?",
        "Name one underrated IPL role that decides titles.",
    ],
    "team-india": [
        "Team India batting depth: real or social-media myth?",
        "Should Team India rotate more aggressively in bilaterals?",
        "White-ball vs red-ball specialists, do we still need both?",
        "Captaincy: data first or dressing-room feel?",
        "Overseas wins: what’s still missing for Team India?",
        "Fast bowling stocks, peak or temporary spike?",
        "Selection transparency: publish more or protect process?",
        "What’s one Team India habit fans excuse too easily?",
        "Home pitches: fair advantage or weak prep for abroad?",
        "Young batters vs experience, who gets the long rope?",
        "Fielding standards: world class or still patchy?",
        "Should Team India ban phones in the dressing room?",
        "Asia Cup / World Cup: media pressure or player ownership?",
        "All-rounder obsession, useful or lazy selection?",
        "Pick a side: aggressive cricket vs smart cricket.",
    ],
    "world-cup": [
        "World Cup knockout cricket: luck or preparation?",
        "Should World Cups stay in India more often?",
        "Super Over forever, fair or lottery?",
        "What’s the most overrated World Cup narrative?",
        "Host advantage: real edge or excuse?",
        "Squad size at World Cups, too big or too small?",
        "Net run rate drama: good theatre or bad sport?",
        "Pick a side: league form means nothing in World Cups.",
        "Which World Cup format is purest, 50-over or T20?",
        "Pressure catching: training issue or character issue?",
        "Should captains be judged only on World Cups?",
        "Neutral umpires / DRS, still trusted?",
        "What’s one World Cup rule you’d rewrite?",
        "Fan travel for World Cups: dream or only for metros?",
        "Underdogs at World Cups, romance or pattern?",
    ],
    "wpl": [
        "WPL: breakthrough for women’s cricket or still a side show?",
        "Should WPL get equal prime-time energy as IPL?",
        "Auction prices in WPL, signal of value or FOMO?",
        "What’s missing for WPL to feel mainstream in tier-2 cities?",
        "Overseas stars in WPL: lift or squeeze local pathways?",
        "Pick a side: more WPL teams vs deeper existing squads.",
        "Media coverage of WPL, progress or PR spikes?",
        "Should school cricket push girls pathways as hard as boys?",
        "Best WPL rivalry building right now?",
        "Franchise branding in WPL: smart or copy-paste IPL?",
        "What’s one rule that would make WPL more watchable?",
        "Pay gaps: cricket board problem or market problem?",
        "Would you watch WPL over a random men’s bilateral?",
        "Role models: who’s carrying WPL culture offline?",
        "WPL finals: better cricket than early IPL eras?",
    ],
    "football-isl": [
        "Is ISL growth real outside metros, or still bubble talk?",
        "Should India prioritize ISL clubs or national team camps?",
        "Football infrastructure: stadiums or grassroots first?",
        "Pick a side: ISL foreign stars help or block Indian talent.",
        "Why does India still struggle to produce elite strikers?",
        "Durand / I-League pathways, respected or ignored?",
        "National team coaching: foreign hire or Indian continuity?",
        "What’s one football rule / format change ISL needs?",
        "Fan culture in Indian football vs cricket, fixable gap?",
        "Women’s football: funding failure or visibility failure?",
        "Should schools treat football equal to cricket academies?",
        "AFC ambitions: delusion or delayed destiny?",
        "Derbies that actually feel like derbies in India?",
        "Refereeing standards in ISL, trust issue?",
        "Name an Indian footballer who deserved bigger career odds.",
    ],
    "kabaddi": [
        "Pro Kabaddi: sport product or entertainment franchise?",
        "Should kabaddi get school-level push equal to cricket?",
        "Raid vs defence, which decides PKL titles more?",
        "Is kabaddi still niche outside TV season?",
        "Pick a side: traditional kabaddi vs league kabaddi.",
        "Athlete pay in kabaddi, fair for the risk?",
        "What’s missing for kabaddi to go global from India?",
        "Women’s kabaddi visibility, where’s the gap?",
        "Should cities build kabaddi-first arenas?",
        "PKL auctions: drama useful or distracting?",
        "Best kabaddi rivalry right now?",
        "Do commentators overhype every super tackle?",
        "Kabaddi fitness vs cricket fitness, underrated?",
        "Would you pick kabaddi over football for a national flex?",
        "One rule change to make kabaddi clearer for new fans?",
    ],
    "olympics": [
        "Which Olympic sport should India fund hardest next?",
        "Medals vs mass participation, what should India optimize?",
        "Are Olympics still the peak dream for Indian athletes?",
        "Pick a side: more sports federations or fewer, better ones.",
        "Hosting Olympics: vanity project or infrastructure unlock?",
        "What’s the most underfunded Olympic pathway in India?",
        "Should corporates get tax credits for Olympic athletes?",
        "Neeraj effect: lasting pipeline or one-hero spike?",
        "Olympic trials transparency, do fans deserve more?",
        "Mental health support for Olympic campaigns, real or PR?",
        "Age-group burnouts before Olympics, who’s accountable?",
        "Should India target Asian Games as the real ladder?",
        "Facilities outside metros: Olympics possible without that?",
        "One federation you’d rebuild from scratch.",
        "Do we celebrate Olympic medals then forget athletes?",
    ],
    "badminton": [
        "Badminton: is India still underfunding a proven medal sport?",
        "PV Sindhu / Lakshya era, what’s the next pipeline?",
        "Should India build more public badminton courts than cricket nets?",
        "Pick a side: singles glory vs doubles investment.",
        "BWF circuit grind, are Indian players over-travelled?",
        "Coaching: foreign experts necessary or Indian system ready?",
        "What’s one badminton rule / scoring take you defend?",
        "School badminton vs academy badminton, who wins talent?",
        "Are Indian shuttlers treated as second-class vs cricketers?",
        "Thomas / Uber Cup priority vs individual titles?",
        "Sponsorship for badminton: brand fit or leftover budget?",
        "Indoor arenas for badminton, cities that get it right?",
        "Women’s badminton visibility in Indian media, enough?",
        "Would you watch a Super League for badminton weekly?",
        "Name the most underrated Indian badminton rivalry.",
    ],
    "tennis": [
        "Indian tennis: doubles success masking singles drought?",
        "Should India fund junior clay / hard-court pathways harder?",
        "Davis Cup energy, still matters or ceremonial?",
        "Pick a side: Grand Slam focus vs Asian swing volume.",
        "Why don’t we produce more top-100 singles players?",
        "Private academies vs institutional tennis, who delivers?",
        "Media coverage of tennis in India, fair or cricket leftover?",
        "Best surface for Indian players to specialize in?",
        "Sponsorship: lifestyle brands or sports brands for tennis?",
        "Would a proper India Open change the pipeline?",
        "What’s one tennis culture problem we don’t admit?",
        "Mixed doubles / doubles, undervalued glory?",
        "Parents in junior tennis: fuel or pressure cooker?",
        "Should schools treat tennis as elite-only forever?",
        "Name an Indian tennis moment that still motivates you.",
    ],
    "hockey": [
        "Hockey: forgotten Olympic pride or comeback story?",
        "Should hockey get equal school push as cricket?",
        "Turf access outside metros, hockey’s real bottleneck?",
        "Pick a side: traditional hockey identity vs modern high press.",
        "FIH leagues vs national camps, what builds India better?",
        "Media silence on hockey between Olympics, fixable?",
        "Women’s hockey: momentum or still under-supported?",
        "What’s one selection debate hockey fans are tired of?",
        "Stadium crowds for hockey, how do we grow them?",
        "Corporate ownership of hockey teams: good or hollow?",
        "Penalty corner specialists, over-indexed strategy?",
        "Should India host more FIH events at home?",
        "Grassroots hockey in tribal / small-town India, ignored?",
        "Coach tenure: patience or results-only?",
        "One rule / format tweak to make hockey TV-friendlier.",
    ],
    "athletics": [
        "Athletics funding: medals first or mass tracks first?",
        "Neeraj / javelin boom, can other events copy it?",
        "Are Indian athletics camps too centralized?",
        "Pick a side: more Diamond League exposure vs domestic depth.",
        "Doping controls: strict enough for Indian athletics?",
        "School athletics day, serious pathway or annual ritual?",
        "What’s the most underrated athletics event for India?",
        "Should states compete harder for athletics budgets?",
        "Women’s athletics visibility, where’s the gap?",
        "Sports science in athletics: real labs or slogans?",
        "Age fraud / paperwork, still a quiet problem?",
        "Would city track clubs beat federation bureaucracy?",
        "Asian Games vs Olympics prep, priorities confused?",
        "One athletics federation change you’d force tomorrow.",
        "Name an Indian track story media underplayed.",
    ],
    "wrestling": [
        "Wrestling: India’s medal machine or governance mess?",
        "Should wrestlers get the same star treatment as cricketers?",
        "Akharas vs modern high-performance centers, both needed?",
        "Pick a side: freestyle focus vs more Greco investment.",
        "Protests and federation politics, did fans stay engaged?",
        "Women’s wrestling pathway, strong enough beyond Olympics?",
        "Weight cutting culture, athlete safety ignored?",
        "What’s one wrestling rule fans still find confusing?",
        "Media only shows wrestling every four years, agree?",
        "Should schools revive wrestling alongside kabaddi?",
        "International camps: essential or expensive tourism?",
        "Sponsorship for wrestling, why so thin?",
        "State rivalries in wrestling, healthy or toxic?",
        "One reform that would protect athletes over officials.",
        "Name a wrestler who changed how India watches the sport.",
    ],
    "boxing": [
        "Boxing in India: Olympic hope or neglected combat sport?",
        "Should India build more community boxing gyms than malls?",
        "Pro boxing vs amateur pathway, which should we prioritize?",
        "Pick a side: more women’s boxing investment now.",
        "Weight categories drama, sport or politics?",
        "Are Indian boxers under-coached for world level?",
        "Media coverage of boxing, only when medals arrive?",
        "What’s missing for an Indian boxing superstar era?",
        "School boxing: safety concerns vs talent funnel?",
        "Sponsorship: energy drinks or serious sports brands?",
        "International exposure for boxers, enough volume?",
        "One federation change boxing needs urgently.",
        "Combat sports stigma in families, still real?",
        "Would a domestic pro league help Indian boxing?",
        "Name an Indian boxing moment that deserved bigger spotlight.",
    ],
    "chess": [
        "Chess boom in India: Gukesh effect or deep pipeline?",
        "Should schools teach chess like a core elective?",
        "Online blitz culture, helping or hurting classical chess?",
        "Pick a side: more Olympiad focus vs individual titles.",
        "Are Indian chess kids burned out too early?",
        "Sponsorship for chess: finally catching up?",
        "Women’s chess in India, visibility still lagging?",
        "What’s one chess federation priority you’d fund first?",
        "OTB vs online ratings, do fans understand the gap?",
        "Should India host more elite classical events at home?",
        "Parental pressure in chess, inspiration or damage?",
        "Esports crossover with chess streaming, net good?",
        "One rule / time-control take you’d defend.",
        "Tier-2 chess academies, real or marketing?",
        "Name the most exciting Indian chess rivalry right now.",
    ],
    "f1": [
        "F1 in India: real fanbase or highlight-clip fandom?",
        "Should India push for a Grand Prix return?",
        "Pick a side: driver skill story vs constructor money story.",
        "Motorsport pathways in India, where do kids even start?",
        "Is F1 too expensive a culture flex for Indian sports budgets?",
        "Streaming F1: accessibility win or paywall problem?",
        "What’s one F1 rule debate you actually care about?",
        "Indian drivers / engineers, under-supported?",
        "Safety vs spectacle in modern F1, balanced?",
        "Would you fund karting tracks over another cricket stadium?",
        "Team radios and drama, good TV or too much soap?",
        "Sustainability claims in F1, believable?",
        "Best entry sport before F1 for Indian talent?",
        "One motorsport event India should host annually.",
        "Name a non-F1 racing series India should watch more.",
    ],
    "nba": [
        "NBA fandom in India: deep or just finals season?",
        "Should India invest in basketball courts as seriously as cricket nets?",
        "Pick a side: NBA culture helps local basketball vs distracts from it.",
        "ISL-style league for basketball, would you watch weekly?",
        "School basketball pathways, missing middle class access?",
        "What’s stopping Indian players from higher global visibility?",
        "Streaming NBA at odd hours, fandom tax?",
        "Women’s basketball in India, ignored?",
        "One rule / format that makes NBA more friendly to new fans.",
        "Jersey culture vs playing culture, which are we?",
        "Should brands fund Indian basketball academies harder?",
        "Asian basketball success stories we should copy?",
        "Fantasy NBA vs watching full games, problem?",
        "Best city to build India’s basketball capital?",
        "Name an NBA debate you’ll defend at dinner.",
    ],
    "esports": [
        "Esports in India: real sport or content category?",
        "Should schools treat BGMI / Valorant like after-school sport?",
        "Pick a side: more prize money vs more grassroots cafes.",
        "Are Indian orgs building careers or just influencers?",
        "Mental health in esports, ignored until burnout?",
        "Government bans / rules, protecting youth or killing scenes?",
        "What’s one esports title India can actually dominate?",
        "LAN culture vs online-only, what builds better players?",
        "Sponsorship ethics in youth gaming, where’s the line?",
        "Women in Indian esports, structural gap or pipeline gap?",
        "Should cricket money cross-fund esports arenas?",
        "Streaming skill vs competitive skill, fans confuse them?",
        "One federation / association esports still needs.",
        "College tournaments: serious pathway or fest filler?",
        "Name an Indian esports moment that felt mainstream.",
    ],
    "ucl": [
        "UCL nights in India: football culture or TV ritual?",
        "Does watching UCL help ISL, or make local football look small?",
        "Pick a side: super clubs ruined UCL romance.",
        "Should Indian kickoff times get more fan-friendly windows?",
        "Fantasy UCL vs actually following a club, what’s healthier?",
        "What’s the most overrated UCL narrative every season?",
        "Young Indian fans: club first or country first?",
        "One UCL rule you’d change tomorrow.",
        "Is VAR helping UCL fairness or killing flow?",
        "Should Indian channels teach tactics more, not only goals?",
        "Best UCL underdog story template still works?",
        "Club merchandise culture in India, identity or flex?",
        "Would you skip ISL for a UCL midweek, honest answer?",
        "Women’s UCL visibility in India, enough?",
        "Name a UCL debate you’ll never concede.",
    ],
    "sports-business": [
        "Sports rights money in India: growing pie or cricket monopoly?",
        "Should athlete salaries be more transparent?",
        "Pick a side: more leagues vs deeper investment in fewer sports.",
        "Are Indian sports startups solving fans or just ads?",
        "Stadium PPPs, public win or private capture?",
        "What’s the most dishonest sports business metric?",
        "Broadcast packages: accessibility vs revenue, your line?",
        "Should federations professionalize like startups?",
        "Athlete equity / ownership, overdue in India?",
        "One regulation that would help clean sports business.",
        "Tier-2 hosting economics, viable without cricket?",
        "Sponsorship morals: betting brands in sports, ok?",
        "Women’s sports commercial value, underrated?",
        "Would you pay for a multi-sport season pass?",
        "Name a sports business take that sounds cynical but true.",
    ],
    "fantasy": [
        "Fantasy sports: fandom tool or gambling with branding?",
        "Should fantasy apps be allowed to sponsor junior cricket?",
        "Pick a side: skill game vs chance game for Dream11-style apps.",
        "Do fantasy points change how we watch real matches?",
        "Regulation of fantasy sports, too soft or too vague?",
        "What’s the most toxic fantasy culture habit?",
        "Should teams / leagues share in fantasy revenue more openly?",
        "Youth using fantasy apps, where’s the duty of care?",
        "One feature fantasy apps should be forced to show.",
        "Does fantasy help smaller sports or only cricket?",
        "Ads everywhere in fantasy, trust killer?",
        "Would you ban fantasy during World Cups?",
        "Skill contests vs pay-to-win boosters, line?",
        "Fantasy for women’s sports, growth opportunity?",
        "Name a fantasy take fans won’t say out loud.",
    ],
    "women-sports": [
        "Women’s sports in India: progress or PR cycles?",
        "Should equal airtime be a policy for public broadcasters?",
        "Pick a side: fund medals first vs fund school girls sports first.",
        "Pay gaps: market reality or institutional failure?",
        "What’s the most under-covered women’s sport right now?",
        "Do sponsors only appear after Olympic medals?",
        "Safe training spaces for women athletes, enough?",
        "One rule / league change that would grow women’s sports fandom.",
        "Media language around women athletes, still biased?",
        "Should men’s leagues be required to platform women’s fixtures?",
        "Parents / schools: still blocking girls from sport?",
        "Role models beyond cricket, who should be amplified?",
        "Would you watch a women’s league over a random men’s bilateral?",
        "Facilities sharing, fair access or leftovers?",
        "Name a women’s sports story India undercelebrated.",
    ],
    "local-sports": [
        "City sports leagues: real culture or weekend hobby?",
        "Should municipalities fund local grounds before flyovers?",
        "Pick a side: more local tournaments vs one big state meet.",
        "What’s dying first in your city, maidans or interest?",
        "School vs club sports, who owns talent discovery?",
        "Local referees / coaches, invisible infrastructure?",
        "One neighborhood sports fix you’d fund with ₹10 lakh.",
        "Are apartment societies killing open play culture?",
        "Women’s access to local grounds after dark, solved?",
        "Should corporates adopt city sports clubs?",
        "Street sports vs formal academies, both needed?",
        "Local rivalry culture, how do we grow it without toxicity?",
        "Public courts booking systems, useful or broken?",
        "Would you pay a small fee for maintained ward grounds?",
        "Name a local sports hero your city ignores.",
    ],
    "fitness": [
        "Gym culture vs outdoor running, what’s healthier for India cities?",
        "Are marathons civic pride or lifestyle flex?",
        "Pick a side: wearable obsession helps or stresses people out.",
        "Should offices treat fitness time as real work policy?",
        "What’s the most oversold fitness trend this year?",
        "Public parks for workouts, welcoming or gated vibes?",
        "Women’s safety on morning / evening runs, priority?",
        "One fitness habit schools should teach for life.",
        "Influencer fitness advice, useful or dangerous?",
        "Yoga as fitness vs yoga as spirituality, your line?",
        "Should cities build more tracks than malls?",
        "Recovery culture: privilege or necessary education?",
        "Community runs: belonging or branding?",
        "Would you tax sugary drinks to fund public fitness?",
        "Name a fitness take you’ll defend at a family dinner.",
    ],
    "cricket-domestic": [
        "Domestic cricket: foundation or afterthought?",
        "Is franchise cricket killing Ranji urgency?",
        "Pick a side: more red-ball window vs endless white-ball.",
        "Should Ranji get prime-time streaming love?",
        "Selection from domestic form, still trustworthy?",
        "State associations: talent engines or political clubs?",
        "What’s one domestic format you’d protect forever?",
        "Player workloads: domestic grind respected?",
        "Pitches in domestic cricket, preparation problem?",
        "Should IPL contracts require domestic appearance minimums?",
        "Fans: why don’t we show up for Ranji?",
        "Women’s domestic cricket pathways, strong enough?",
        "One reform to make domestic cricket financially viable.",
        "Umpiring / standards in domestic, underrated crisis?",
        "Name a domestic hero who never got enough India caps.",
    ],
    "coaching": [
        "Selectors vs coaches: who actually owns Team outcomes?",
        "Should coaching tenures be longer in Indian sport?",
        "Pick a side: foreign coaches necessary for non-cricket sports.",
        "Transparency in selection, publish more criteria?",
        "Are Indian coaches underpaid relative to pressure?",
        "What’s the most toxic coaching culture habit?",
        "Age-group coaching: development or win-at-all-costs?",
        "One coaching certification reform you’d force.",
        "Data analysts in coaching boxes, overrated?",
        "Player-coach trust: how do fans misread it?",
        "Should ex-stars get automatic coaching fast tracks?",
        "Mental skills coaches, essential staff or luxury?",
        "State coaching pathways, equal access?",
        "Would you rather a tough coach or a popular coach?",
        "Name a coaching decision India still argues about.",
    ],
    "stadiums": [
        "Stadiums: fan temples or empty concrete?",
        "Should ticket prices prioritize full houses over VIP?",
        "Pick a side: more boutique venues vs mega stadiums.",
        "Food and toilets, why do Indian stadiums still fail basics?",
        "Safe standing / fan zones, overdue?",
        "Women and families at stadiums, access or optics?",
        "One stadium rule that kills atmosphere.",
        "Should cities reuse stadiums for non-cricket sports weekly?",
        "Travel and last-mile to stadiums, civic failure?",
        "Dynamic pricing: fair market or fan hostility?",
        "Noise, drums, choreography, culture or disruption?",
        "Accessibility for disabled fans, ignored?",
        "Would you ban phones on big screens for key moments?",
        "Public money for stadiums, when is it justified?",
        "Name a stadium experience India gets uniquely right.",
    ],
    "para-sports": [
        "Para sports: inclusion success story or still invisible?",
        "Should Paralympic medals get equal celebration budgets?",
        "Pick a side: more para pathways in schools now.",
        "Facilities access for para athletes, metro-only problem?",
        "Media coverage of para sports, respectful or token?",
        "What’s the biggest funding myth around para sports?",
        "Corporate sponsorship: charity framing vs serious sport?",
        "One policy that would unlock para sports participation.",
        "Classification debates, fair or confusing to fans?",
        "Should broadcasters mandate para event windows?",
        "Transport / venue accessibility at events, still broken?",
        "Role models in para sports, amplified enough?",
        "Grassroots discovery for para talent, who owns it?",
        "Would you attend a para sports final over a random bilateral?",
        "Name a para sports story India should teach in schools.",
    ],
    "ufc": [
        "Combat sports in India: rising culture or niche import?",
        "Should MMA get clearer regulation and pathways?",
        "Pick a side: UFC fandom helps local combat sports.",
        "Safety standards in combat gyms, enforced enough?",
        "Women in combat sports, stigma still blocking talent?",
        "What’s missing for an Indian MMA star pipeline?",
        "Media sensationalism vs sport education in combat?",
        "One rule / matchmaking take you’d defend.",
        "Should schools ever teach combat sports safely?",
        "Sponsorship morals for combat events, where’s the line?",
        "Traditional martial arts vs modern MMA, coexistence?",
        "Fan toxicity around fight sports, worse than cricket?",
        "Would you fund community combat gyms over another mall?",
        "Weight cutting culture, athlete risk ignored?",
        "Name a combat sports moment that changed your mind.",
    ],
    "golf": [
        "Golf in India: elitist forever or opening up?",
        "Should public courses matter more than private clubs?",
        "Pick a side: fund junior golf harder for Olympic pathways.",
        "Why don’t Indian golfers get mainstream sports coverage?",
        "Corporate golf culture, networking or real sport?",
        "What’s one access reform golf needs in Indian cities?",
        "Women’s golf visibility, enough?",
        "Hosting big tours in India, worth the cost?",
        "Junior equipment / coaching costs, barrier #1?",
        "Should schools treat golf as unreachable forever?",
        "Environmental use of land for golf, justified?",
        "One golf rule / format that would grow fandom.",
        "Fantasy / sim golf, gateway or distraction?",
        "Would you watch golf weekly if it was free-to-air?",
        "Name an Indian golf story that deserved bigger headlines.",
    ],
    "table-tennis": [
        "Table tennis: India’s quiet medal sport or forever side table?",
        "Should every school have proper TT tables before cricket nets envy?",
        "Pick a side: more domestic leagues vs more China/Asia exposure.",
        "Why is TT still under-televised in India?",
        "Coaching depth for TT, enough outside metros?",
        "What’s one rule / scoring take that would help casual fans?",
        "Women’s TT pathways, supported?",
        "Equipment costs, barrier for talent?",
        "Should residential societies build TT rooms as default amenity?",
        "International training blocks, essential?",
        "Sponsorship for TT, why so thin vs cricket?",
        "One federation priority for Indian TT growth.",
        "Asian dominance, can India realistically break in?",
        "Would you watch a weekly TT league on stream?",
        "Name an Indian paddler who deserved bigger fame.",
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
        "Return JSON {\"items\":[\"...\"]}, up to 20 short debate questions, "
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


def _live_debate_titles(
    db: Session,
    arena_key: Optional[str],
    topic_key: Optional[str] = None,
    limit: int = 8,
) -> list[str]:
    q = (
        db.query(models.Space)
        .filter(models.Space.status == "open")
        .filter(models.Space.kind == "debate")
    )
    topic_key = (topic_key or "").strip().lower() or None
    if topic_key:
        q = q.join(models.Topic, models.Topic.id == models.Space.topic_id).filter(
            models.Topic.key == topic_key
        )
        if arena_key and arena_key in ARENA_KEYS:
            q = q.filter(models.Topic.arena_key == arena_key)
    elif arena_key and arena_key in ARENA_KEYS:
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


def _topic_meta(arena_key: Optional[str], topic_key: str) -> Optional[dict]:
    try:
        from app.topics_data import TOPICS_BY_ARENA
    except Exception:  # noqa: BLE001
        return None
    topic_key = (topic_key or "").strip().lower()
    if not topic_key:
        return None
    arenas = [arena_key] if arena_key else list(TOPICS_BY_ARENA.keys())
    for ak in arenas:
        for row in TOPICS_BY_ARENA.get(ak) or []:
            if row.get("key") == topic_key:
                return {**row, "arena_key": ak}
    # Search all arenas if not found under provided arena.
    for ak, rows in TOPICS_BY_ARENA.items():
        for row in rows:
            if row.get("key") == topic_key:
                return {**row, "arena_key": ak}
    return None


def _template_prompts_for_topic(name: str, blurb: str = "") -> list[str]:
    label = (name or "this topic").strip() or "this topic"
    hint = (blurb or "").strip()
    base = [
        f"{label}: what’s your hottest take right now?",
        f"Is {label} getting enough mainstream attention in India?",
        f"What’s one rule / format change you’d make in {label}?",
        f"Pick a side on {label}, and defend it at a family dinner.",
        f"Who’s the most underrated name in {label} today?",
        f"Funding for {label}: medals first or grassroots first?",
        f"Media coverage of {label}, fair or cricket leftover?",
        f"Should schools push {label} as hard as cricket?",
        f"What’s a {label} debate fans are tired of?",
        f"One {label} moment that changed how you watch sport.",
        f"Are we romanticizing struggle stories in {label} too much?",
        f"Would you watch a weekly league for {label} over a random bilateral?",
        f"Coaching / selection in {label}, transparent enough?",
        f"What’s missing for {label} to feel mainstream outside metros?",
        f"Name a {label} take you’ll never concede.",
    ]
    if hint:
        base.insert(1, f"{label}: {hint.rstrip('.')}, agree or fight me?")
    return base


def _curated_for_topic(arena_key: Optional[str], topic_key: str) -> list[str]:
    topic_key = (topic_key or "").strip().lower()
    if not topic_key:
        return []
    if topic_key in CURATED_BY_TOPIC:
        return list(CURATED_BY_TOPIC[topic_key])
    meta = _topic_meta(arena_key, topic_key)
    if meta:
        return _template_prompts_for_topic(meta.get("name") or topic_key, meta.get("blurb") or "")
    return _template_prompts_for_topic(topic_key.replace("-", " ").title())


def list_suggestions(
    db: Session,
    *,
    surface: str = "square",
    arena_key: Optional[str] = None,
    topic_key: Optional[str] = None,
    limit: int = 20,
) -> dict:
    limit = max(5, min(int(limit or 20), 20))
    surface = (surface or "square").strip().lower()
    arena = (arena_key or "").strip().lower() or None
    topic = (topic_key or "").strip().lower() or None

    if surface == "arena" and arena in CURATED:
        bucket = arena
    elif arena in CURATED:
        bucket = arena
    else:
        bucket = "square"

    if topic:
        curated = _curated_for_topic(arena, topic)
        live = _live_debate_titles(
            db,
            arena if surface == "arena" else None,
            topic_key=topic,
        )
        item_prefix = f"{bucket}-{topic}"
        rank_label = f"{bucket}/{topic}"
    else:
        curated = list(CURATED.get(bucket) or CURATED["square"])
        live = _live_debate_titles(db, arena if surface == "arena" else None)
        item_prefix = bucket
        rank_label = bucket

    merged: list[str] = []
    for item in live + curated:
        if item not in merged:
            merged.append(item)

    source = "curated+live"
    if topic:
        source = "topic+live"
    provider = _provider()
    if provider in ("openai", "openai-compatible") and merged:
        ranked = _openai_rank(merged, arena=rank_label)
        if ranked:
            merged = ranked
            source = f"llm:{provider}"

    return {
        "ok": True,
        "surface": surface,
        "arena_key": arena,
        "topic_key": topic,
        "source": source,
        "items": [{"text": t, "id": f"{item_prefix}-{i}"} for i, t in enumerate(merged[:limit])],
    }
