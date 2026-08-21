/** BarathX Arenas — sided talk with Agree / Disagree / It depends (or Fund it / Pass) */

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

export function arenaMeta(key) {
  return ARENA_TOPICS.find((a) => a.key === key) || null;
}
