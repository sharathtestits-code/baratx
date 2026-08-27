/** Age / DOB helpers for 18+ gate (India DPDP children + US COPPA-safe floor). */

export const AGE_CONSENT_VERSION = "2026-08-27-age";
export const MIN_AGE_YEARS = 18;

/** @returns {{ ok: true, iso: string, age: number } | { ok: false, error: string }} */
export function parseDobAndAge(dobValue) {
  const raw = String(dobValue || "").trim();
  if (!/^\d{4}-\d{2}-\d{2}$/.test(raw)) {
    return { ok: false, error: "Enter a valid date of birth." };
  }
  const [y, m, d] = raw.split("-").map(Number);
  const dob = new Date(Date.UTC(y, m - 1, d));
  if (
    dob.getUTCFullYear() !== y ||
    dob.getUTCMonth() !== m - 1 ||
    dob.getUTCDate() !== d
  ) {
    return { ok: false, error: "Enter a valid date of birth." };
  }
  const now = new Date();
  let age = now.getUTCFullYear() - y;
  const hadBirthday =
    now.getUTCMonth() > m - 1 || (now.getUTCMonth() === m - 1 && now.getUTCDate() >= d);
  if (!hadBirthday) age -= 1;
  if (age > 120) {
    return { ok: false, error: "Enter a valid date of birth." };
  }
  if (age < MIN_AGE_YEARS) {
    return {
      ok: false,
      error: `BarathX is for people ${MIN_AGE_YEARS}+. If you are under ${MIN_AGE_YEARS}, you cannot create an account.`,
    };
  }
  return { ok: true, iso: raw, age };
}
