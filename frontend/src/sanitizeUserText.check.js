/** Quick checks for sanitizeUserText (run via node). */
import { sanitizeUserText } from "./sanitizeUserText.js";

const cases = [
  ["download \u202Egnp.exe\u202C now", "download gnp.exe now"],
  ["hello\u2066world\u2069", "helloworld"],
  ["invoice_AAA.\u202Eexe.png", "invoice_AAA.exe.png"],
  ["नमस्ते 🇮🇳", "नमस्ते 🇮🇳"],
];

let failed = 0;
for (const [input, want] of cases) {
  const got = sanitizeUserText(input);
  if (got !== want) {
    console.error("FAIL", JSON.stringify(input), "→", JSON.stringify(got), "want", JSON.stringify(want));
    failed += 1;
  }
}
if (failed) process.exit(1);
console.log("sanitizeUserText ok", cases.length);
