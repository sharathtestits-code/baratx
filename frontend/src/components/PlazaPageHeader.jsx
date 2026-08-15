import { useT } from "../context/LocaleContext";

/**
 * Shared page header so Square / Explore / Arenas / Live naming matches.
 */
export default function PlazaPageHeader({ kicker, title, sub }) {
  const t = useT();
  return (
    <section className="plaza-hero plaza-hero-page">
      <p className="plaza-hero-kicker">{kicker ?? t("brand.tagline")}</p>
      <h1 className="plaza-hero-title">{title}</h1>
      {sub ? <p className="plaza-hero-sub">{sub}</p> : null}
    </section>
  );
}
