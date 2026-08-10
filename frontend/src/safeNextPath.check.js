/** Unit-ish checks for safeNextPath (run via node). */
import { safeNextPath } from "./safeNextPath.js";

const cases = [
  ["/feed", "/feed"],
  ["/spaces", "/spaces"],
  ["/arenas/startups", "/arenas/startups"],
  ["/rewards", "/rewards"],
  ["https://evil.com", "/feed"],
  ["//evil.com", "/feed"],
  ["/\\evil.com", "/feed"],
  ["javascript:alert(1)", "/feed"],
  ["/%2F%2Fevil.com", "/feed"],
  ["", "/feed"],
  ["/admin", "/feed"],
  ["/bx-ops", "/feed"],
];

let failed = 0;
for (const [input, want] of cases) {
  const got = safeNextPath(input, "/feed");
  if (got !== want) {
    console.error("FAIL", JSON.stringify(input), "→", got, "want", want);
    failed += 1;
  }
}
if (failed) process.exit(1);
console.log("safeNextPath ok", cases.length);
