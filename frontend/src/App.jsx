import { Link, Navigate, Route, Routes, useLocation } from "react-router-dom";
import Landing from "./pages/Landing";
import Signup from "./pages/Signup";
import Login from "./pages/Login";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import VerifyEmail from "./pages/VerifyEmail";
import Feed from "./pages/Feed";
import Profile from "./pages/Profile";
import Search from "./pages/Search";
import PostDetail from "./pages/PostDetail";
import Notifications from "./pages/Notifications";
import FollowList from "./pages/FollowList";
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

function AppShell() {
  return (
    <div className="app-shell">
      <Sidebar />
      <main className="app-main">
        <EmailVerifyBanner />
        <Routes>
          <Route path="/" element={<Navigate to="/feed" replace />} />
          <Route path="/signup" element={<Navigate to="/feed" replace />} />
          <Route path="/login" element={<Navigate to="/feed" replace />} />
          <Route path="/feed" element={<Feed />} />
          <Route path="/search" element={<Search />} />
          <Route path="/notifications" element={<Notifications />} />
          <Route path="/posts/:postId" element={<PostDetail />} />
          <Route path="/u/:username" element={<Profile />} />
          <Route path="/u/:username/:kind" element={<FollowList />} />
          <Route path="*" element={<Navigate to="/feed" replace />} />
        </Routes>
      </main>
      <RightRail />
      <BottomNav />
    </div>
  );
}

export default function App() {
  const { token, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <div className="page-loading">Loading…</div>;
  }

  // Email confirm / password reset stay outside the app shell even when logged in.
  if (location.pathname === "/verify-email") {
    return (
      <AuthChrome>
        <VerifyEmail />
      </AuthChrome>
    );
  }
  if (location.pathname === "/reset-password") {
    return (
      <AuthChrome>
        <ResetPassword />
      </AuthChrome>
    );
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
          path="/forgot-password"
          element={
            <AuthChrome>
              <ForgotPassword />
            </AuthChrome>
          }
        />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }

  return <AppShell />;
}
