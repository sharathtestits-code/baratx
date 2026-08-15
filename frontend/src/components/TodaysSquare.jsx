import { useState } from "react";
import { todaysSquareKey, todaysSquareQuestion } from "../square";
import { useT } from "../context/LocaleContext";

/**
 * Daily mission strip — one shared India question so newcomers have something to join.
 */
export default function TodaysSquare({ onAnswer }) {
  const t = useT();
  const question = todaysSquareQuestion();
  const dayKey = todaysSquareKey();
  const [skipped, setSkipped] = useState(
    () => typeof localStorage !== "undefined" && localStorage.getItem(`bx_square_skip_${dayKey}`) === "1"
  );

  if (skipped) return null;

  function skip() {
    localStorage.setItem(`bx_square_skip_${dayKey}`, "1");
    setSkipped(true);
  }

  return (
    <section className="todays-square" aria-label={t("todays.label")}>
      <span className="for-you-chip" aria-hidden="true">
        {t("todays.chip")}
      </span>
      <div className="todays-square-head">
        <div>
          <p className="todays-square-label">{t("todays.label")}</p>
          <h2 className="todays-square-title">{question}</h2>
          <p className="todays-square-sub">{t("todays.sub")}</p>
        </div>
        <button type="button" className="todays-square-skip" onClick={skip}>
          {t("todays.later")}
        </button>
      </div>
      <button type="button" className="todays-square-cta" onClick={() => onAnswer?.(question)}>
        {t("todays.cta")}
      </button>
    </section>
  );
}
