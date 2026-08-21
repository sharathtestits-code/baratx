/** BarathX Arenas + Circles — sided talk with Agree / Disagree / It depends (or Fund it / Pass) */

export const ARENA_TOPICS = [
  {
    key: "startups",
    name: "Startups",
    blurb: "Funding, founders, and the India builder economy. Fund it, Pass, or It depends.",
    accent: "#059669",
    debateFor: "Fund it",
    debateAgainst: "Pass",
    debateDepends: "It depends",
    composeHint: "Fund it, Pass, or It depends — make your case…",
    openDebateLabel: "Open Fund it / Pass / It depends",
  },
  {
    key: "sports",
    name: "Sports",
    blurb: "Cricket, football, and every match India talks about.",
    accent: "#0d9488",
    debateDepends: "It depends",
  },
  {
    key: "politics",
    name: "Politics",
    blurb: "Policy, parties, and the fights that shape the country — with room for nuance.",
    accent: "#c2410c",
    debateDepends: "It depends",
  },
  {
    key: "entertainment",
    name: "Entertainment",
    blurb: "Film, music, and celebrity culture — pick a side or say it depends.",
    accent: "#7c3aed",
    debateDepends: "It depends",
  },
  {
    key: "news",
    name: "News",
    blurb: "Breaking stories and the takes India can’t ignore.",
    accent: "#0369a1",
    debateDepends: "It depends",
  },
  {
    key: "spirituality",
    name: "Spirituality",
    blurb: "Faith, yoga, festivals, and the searches shaping modern India.",
    accent: "#0f766e",
    debateFor: "Resonates",
    debateAgainst: "Skeptical",
    debateDepends: "It depends",
    composeHint: "Start a spirituality debate…",
    openDebateLabel: "Open Resonates / Skeptical / It depends",
  },
];

/** Belonging lanes under Arenas — Campus, City, Builders. */
export const CIRCLE_TOPICS = [
  {
    key: "campus-careers",
    name: "Campus & Careers",
    blurb: "Placements, first jobs, WFH, salary talk, study abroad.",
    accent: "#b45309",
    kind: "circle",
    debateDepends: "It depends",
  },
  {
    key: "my-city",
    name: "My City",
    blurb: "Bengaluru, Hyderabad, Mumbai, Chennai, Delhi, Pune — local belonging.",
    accent: "#0369a1",
    kind: "circle",
    debateDepends: "It depends",
  },
  {
    key: "builders",
    name: "Builders",
    blurb: "Startup feedback, AI tools, product critique, hiring.",
    accent: "#047857",
    kind: "circle",
    debateDepends: "It depends",
  },
];

export const ALL_TOPIC_LANES = [...ARENA_TOPICS, ...CIRCLE_TOPICS];

export function arenaMeta(key) {
  return ALL_TOPIC_LANES.find((a) => a.key === key) || null;
}

export function isCircleKey(key) {
  return CIRCLE_TOPICS.some((c) => c.key === key);
}
