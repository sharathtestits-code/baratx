/** BaratX Arenas — Sports, Politics, Entertainment, News */

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
];

export function arenaMeta(key) {
  return ARENA_TOPICS.find((a) => a.key === key) || null;
}
