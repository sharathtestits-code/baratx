/** BharatX Arenas — public squares with For/Against (or Fund it/Pass) debates */

export const ARENA_TOPICS = [
  {
    key: "sports",
    name: "Sports",
    blurb: "Cricket, football, and every match India argues about.",
    accent: "#0d9488",
  },
  {
    key: "politics",
    name: "Politics",
    blurb: "Policy, parties, and the fights that shape the country.",
    accent: "#c2410c",
  },
  {
    key: "entertainment",
    name: "Entertainment",
    blurb: "Film, music, and celebrity culture — pick a side.",
    accent: "#7c3aed",
  },
  {
    key: "news",
    name: "News",
    blurb: "Breaking stories and the takes India can’t ignore.",
    accent: "#0369a1",
  },
  {
    key: "startups",
    name: "Startups",
    blurb: "India’s idea square — pitch like YC, crowd votes Fund it or Pass.",
    accent: "#b45309",
    debateFor: "Fund it",
    debateAgainst: "Pass",
    composeHint: "Pitch your startup idea for India to Fund it or Pass…",
    openDebateLabel: "Open Fund it vs Pass",
  },
  {
    key: "spirituality",
    name: "Spirituality",
    blurb: "Faith, yoga, festivals, and the searches shaping modern India.",
    accent: "#0f766e",
    debateFor: "Resonates",
    debateAgainst: "Skeptical",
    composeHint: "Start a spirituality debate…",
    openDebateLabel: "Open Resonates vs Skeptical",
  },
];

export function arenaMeta(key) {
  return ARENA_TOPICS.find((a) => a.key === key) || null;
}
