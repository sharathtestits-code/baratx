/**
 * Shared page header so Square / Explore / Arenas / Live naming matches.
 */
export default function PlazaPageHeader({ kicker = "India's public square", title, sub }) {
  return (
    <section className="plaza-hero plaza-hero-page">
      <p className="plaza-hero-kicker">{kicker}</p>
      <h1 className="plaza-hero-title">{title}</h1>
      {sub ? <p className="plaza-hero-sub">{sub}</p> : null}
    </section>
  );
}
