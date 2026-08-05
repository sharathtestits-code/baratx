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
import Bookmarks from "./pages/Bookmarks";
import Messages from "./pages/Messages";
import MessageThread from "./pages/MessageThread";
import Hashtag from "./pages/Hashtag";
import Admin from "./pages/Admin";
import Settings from "./pages/Settings";
import Lists from "./pages/Lists";
import ListDetail from "./pages/ListDetail";
import Communities from "./pages/Communities";
import CommunityDetail from "./pages/CommunityDetail";
import Spaces from "./pages/Spaces";
import SpaceRoom from "./pages/SpaceRoom";
import Sidebar from "./components/Sidebar";
import RightRail from "./components/RightRail";
import BottomNav from "./components/BottomNav";
import EmailVerifyBanner from "./components/EmailVerifyBanner";
import Logo from "./components/Logo";
import ThemeOnboarding from "./components/ThemeOnboarding";
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

function AdminChrome({ children }) {
  return (
    <div className="page page-admin">
      <header className="admin-topbar">
        <Link to="/" className="admin-brand" aria-label="BaratX Home">
          <Logo variant="full" className="admin-topbar-logo" />
          <span className="admin-topbar-badge">Admin</span>
        </Link>
        <Link to="/" className="admin-topbar-back">
          Back to BaratX
        </Link>
      </header>
      <main className="admin-main">{children}</main>
    </div>
  );
}

function AppShell() {
  return (
    <div className="app-shell">
      <Sidebar />
      <main className="app-main">
        <EmailVerifyBanner />
        <ThemeOnboarding />
        <Routes>
          <Route path="/" element={<Navigate to="/feed" replace />} />
          <Route path="/signup" element={<Navigate to="/feed" replace />} />
          <Route path="/login" element={<Navigate to="/feed" replace />} />
          <Route path="/feed" element={<Feed />} />
          <Route path="/search" element={<Search />} />
          <Route path="/notifications" element={<Notifications />} />
          <Route path="/bookmarks" element={<Bookmarks />} />
          <Route path="/messages" element={<Messages />} />
          <Route path="/messages/:username" element={<MessageThread />} />
          <Route path="/hashtag/:tag" element={<Hashtag />} />
          <Route path="/posts/:postId" element={<PostDetail />} />
          <Route path="/u/:username" element={<Profile />} />
          <Route path="/u/:username/:kind" element={<FollowList />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/lists" element={<Lists />} />
          <Route path="/lists/:listId" element={<ListDetail />} />
          <Route path="/communities" element={<Communities />} />
          <Route path="/communities/:slug" element={<CommunityDetail />} />
          <Route path="/spaces" element={<Spaces />} />
          <Route path="/spaces/:spaceId" element={<SpaceRoom />} />
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
    return <div className="page-loading">Starting BaratX…</div>;
  }

  // Admin + email confirm / password reset stay outside the app shell.
  if (location.pathname === "/admin") {
    return (
      <AdminChrome>
        <Admin />
      </AdminChrome>
    );
  }
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
        {/* Unknown logged-out URLs → public landing (GTM share target), not a bare login bounce */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    );
  }

  return <AppShell />;
}
