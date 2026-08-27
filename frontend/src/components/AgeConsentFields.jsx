import { Link } from "react-router-dom";
import { MIN_AGE_YEARS } from "../ageConsent";

/**
 * DOB + 18+ attestation used on signup (email / phone / Google).
 */
export default function AgeConsentFields({
  dateOfBirth,
  onDateOfBirthChange,
  confirmAge18,
  onConfirmAge18Change,
  idPrefix = "age",
}) {
  return (
    <div className="bx-age-consent-fields">
      <label htmlFor={`${idPrefix}-dob`}>
        Date of birth
        <input
          id={`${idPrefix}-dob`}
          type="date"
          value={dateOfBirth}
          onChange={(e) => onDateOfBirthChange(e.target.value)}
          autoComplete="bday"
          required
          max={new Date().toISOString().slice(0, 10)}
        />
      </label>
      <p className="hint">
        Used only to confirm you are {MIN_AGE_YEARS}+. Never shown on your profile. We save it for
        eligibility only — we do not sell it.{" "}
        <Link to="/age-consent" target="_blank" rel="noopener noreferrer">
          Why we ask
        </Link>
      </p>
      <label className="age-gate">
        <input
          type="checkbox"
          checked={confirmAge18}
          onChange={(e) => onConfirmAge18Change(e.target.checked)}
        />
        <span>
          I confirm I am {MIN_AGE_YEARS} or older and that this date of birth is accurate. I have read
          the{" "}
          <Link to="/age-consent" target="_blank" rel="noopener noreferrer">
            age &amp; DOB consent notice
          </Link>
          .
        </span>
      </label>
    </div>
  );
}
