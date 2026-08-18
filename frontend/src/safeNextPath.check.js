/** Unit-ish checks for safeNextPath (run via node). */
import { safeNextPath } from "./safeNextPath.js";

const cases = [
  ["/home", "/home"],
  ["/feed", "/feed"],
  ["/spaces", "/spaces"],
  ["/arenas/startups", "/arenas/startups"],
  ["/rewards", "/rewards"],
  ["/child-safety", "/child-safety"],
  ["https://evil.com", "/home"],
  ["//evil.com", "/home"],
  ["/\\evil.com", "/home"],
  ["javascript:alert(1)", "/home"],
  ["/%2F%2Fevil.com", "/home"],
  ["", "/home"],
  ["/admin", "/home"],
  ["/bx-ops", "/home"],
];

let failed = 0;
for (const [input, want] of cases) {
  const got = safeNextPath(input, "/home");
  if (got !== want) {
    console.error("FAIL", JSON.stringify(input), "→", got, "want", want);
    failed += 1;
  }
}
if (failed) process.exit(1);
console.log("safeNextPath ok", cases.length);
