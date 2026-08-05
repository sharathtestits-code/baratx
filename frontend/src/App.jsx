import { Link, Navigate, Route, Routes } from "react-router-dom";
import Landing from "./pages/Landing";
import Signup from "./pages/Signup";
import Login from "./pages/Login";
import VerifyEmail from "./pages/VerifyEmail";
import Feed from "./pages/Feed";
import Profile from "./pages/Profile";
import Search from "./pages/Search";
import PostDetail from "./pages/PostDetail";
import Sidebar from "./components/Sidebar";
import RightRail from "./components/RightRail";
import BottomNav from "./components/BottomNav";
import EmailVerifyBanner from "./components/EmailVerifyBanner";
import Logo from "./components/Logo";
import { useAuth } from "./context/AuthContext";

function AuthChrome({ children }) {
  return (
    <div className="page page-auth">
      <header className="topbar topbar-minimal">
        <Link to="/" className="brand" aria-label="BaratX Home">
          <Logo variant="full" className="topbar-logo" />
        </Link>
      </header>
      <main>{children}</main>
    </div>
  );
}

export default function App() {
  const { token, loading } = useAuth();

  if (loading) {
    return <div className="page-loading">Loading…</div>;
  }

  if (!token) {
    return (
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route
          path="/signup"
          element={
            <AuthChrome>
              <Signup />
            </AuthChrome>
          }
        />
        <Route
          path="/login"
          element={
            <AuthChrome>
              <Login />
            </AuthChrome>
          }
        />
        <Route
          path="/verify-email"
          element={
            <AuthChrome>
              <VerifyEmail />
            </AuthChrome>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    );
  }

  return (
    <div className="app-shell">
      <Sidebar />
      <main className="app-main">
        <EmailVerifyBanner />
        <Routes>
          <Route path="/" element={<Navigate to="/feed" replace />} />
          <Route path="/signup" element={<Navigate to="/feed" replace />} />
          <Route path="/login" element={<Navigate to="/feed" replace />} />
          <Route path="/verify-email" element={<VerifyEmail />} />
          <Route path="/feed" element={<Feed />} />
          <Route path="/search" element={<Search />} />
          <Route path="/posts/:postId" element={<PostDetail />} />
          <Route path="/u/:username" element={<Profile />} />
        </Routes>
      </main>
      <RightRail />
      <BottomNav />
    </div>
  );
}
