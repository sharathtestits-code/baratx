const REGIONS = [
  { code: "IN", dial: "+91", label: "India (+91)" },
  { code: "US", dial: "+1", label: "USA / Canada (+1)" },
];

/**
 * Country select + national number. Emits phone string via onPhoneChange.
 */
export default function PhoneField({ region, phone, onRegionChange, onPhoneChange, required = true }) {
  const meta = REGIONS.find((r) => r.code === region) || REGIONS[0];

  function handleRegion(code) {
    onRegionChange(code);
    const next = REGIONS.find((r) => r.code === code);
    const digits = (phone || "").replace(/\D/g, "");
    if (!digits || phone === "+91" || phone === "+1" || phone === meta.dial) {
      onPhoneChange(next.dial);
    }
  }

  return (
    <label className="phone-field-label">
      Phone number
      <div className="phone-field">
        <select
          className="phone-region"
          value={region}
          onChange={(e) => handleRegion(e.target.value)}
          aria-label="Country"
        >
          {REGIONS.map((r) => (
            <option key={r.code} value={r.code}>
              {r.label}
            </option>
          ))}
        </select>
        <input
          className="phone-number"
          type="tel"
          inputMode="tel"
          autoComplete="tel"
          value={phone}
          onChange={(e) => onPhoneChange(e.target.value)}
          placeholder={region === "US" ? "+12025550123" : "+919876543210"}
          required={required}
        />
      </div>
      <span className="hint phone-hint">
        {region === "US"
          ? "US/Canada: 10-digit number or full +1…"
          : "India: 10-digit mobile or full +91…"}
      </span>
    </label>
  );
}

export { REGIONS };
