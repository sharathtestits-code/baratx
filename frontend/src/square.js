/** Daily “Today’s Square” question — shared mission so the feed isn’t empty homework. */

const QUESTIONS = [
  "What’s one unpopular opinion you have about work culture in India?",
  "Which Indian city is most underrated — and why?",
  "What should BaratX never become?",
  "Remote work made Indian careers better or worse?",
  "What’s one thing Indian startups copy that they shouldn’t?",
  "Drop your hottest take on cricket without starting a war.",
  "What’s a ‘respectable’ career advice you wish more people ignored?",
  "Which India story do global feeds keep getting wrong?",
  "What’s the best public debate you’ve had this month?",
  "If you could fix one thing about online discourse in India, what is it?",
  "College prepared you for work — true or false? Defend it.",
  "What’s a small India habit that should be a national flex?",
  "Who should every BaratX user from your city follow?",
  "What’s overrated in Indian tech Twitter / LinkedIn?",
  "One sentence: why did you join BaratX today?",
];

export function todaysSquareQuestion(date = new Date()) {
  const start = Date.UTC(date.getUTCFullYear(), 0, 0);
  const now = Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate());
  const dayOfYear = Math.floor((now - start) / 86400000);
  return QUESTIONS[dayOfYear % QUESTIONS.length];
}

export function todaysSquareKey(date = new Date()) {
  return date.toISOString().slice(0, 10);
}
