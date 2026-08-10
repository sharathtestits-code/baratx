import { Link } from "react-router-dom";
import Logo from "../components/Logo";

/**
 * Unknown top-level routes — do not silently redirect to Square/landing.
 */
export default function NotFound({ homeTo = "/feed", homeLabel = "Back to Square" }) {
  return (
    <div className="not-found-page">
      <Logo variant="mark" className="not-found-logo" />
      <h1>Page not found</h1>
      <p className="hint">That link doesn’t match anything on BarathX.</p>
      <Link to={homeTo} className="btn btn-primary">
        {homeLabel}
      </Link>
    </div>
  );
}
