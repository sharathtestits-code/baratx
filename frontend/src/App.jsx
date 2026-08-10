import { Link, Navigate, Route, Routes, useLocation } from "react-router-dom";
import Landing from "./pages/Landing";
import Signup from "./pages/Signup";
import Login from "./pages/Login";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import VerifyEmail from "./pages/VerifyEmail";
import Privacy from "./pages/Privacy";
import Terms from "./pages/Terms";
import Guidelines from "./pages/Guidelines";
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
import Arenas from "./pages/Arenas";
import ArenaDetail from "./pages/ArenaDetail";
import Spaces from "./pages/Spaces";
import SpaceRoom from "./pages/SpaceRoom";
import OnboardingTopics from "./pages/OnboardingTopics";
import Rewards from "./pages/Rewards";
import NotFound from "./pages/NotFound";
import BottomNav from "./components/BottomNav";
import PlazaTopBar from "./components/PlazaTopBar";
import PlazaSideMenu from "./components/PlazaSideMenu";
import EmailVerifyBanner from "./components/EmailVerifyBanner";
import Logo from "./components/Logo";
import ThemeOnboarding from "./components/ThemeOnboarding";
import ComposeFab from "./components/ComposeFab";
import { useAuth } from "./context/AuthContext";
import { PlazaMenuProvider, usePlazaMenu } from "./context/PlazaMenuContext";
import { canAccessOpsConsole, opsConsolePath } from "./opsAccess";

function AuthChrome({ children, legal = false }) {
  return (
    <div className="page page-auth">
      <header className="topbar topbar-minimal">
        <Link to="/" className="brand" aria-label="BaratX Home">
          <Logo variant="full" className="topbar-logo" />
        </Link>
      </header>
      {/* Legal docs use an explicit layout class — never rely on :has() alone. */}
      <main className={`page-auth-main${legal ? " page-auth-main--legal" : ""}`}>{children}</main>
    </div>
  );
}

function AdminChrome({ children }) {
  return (
    <div className="page page-admin">
      <header className="admin-topbar">
        <Link to="/" className="admin-brand" aria-label="BarathX Home">
          <Logo variant="full" className="admin-topbar-logo" />
          <span className="admin-topbar-badge">Admin</span>
        </Link>
        <Link to="/" className="admin-topbar-back">
          Back to BarathX
        </Link>
      </header>
      <main className="admin-main">{children}</main>
    </div>
  );
}

function PlazaShell() {
  const { open } = usePlazaMenu();
  return (
    <div className={`app-shell app-shell-plaza${open ? " is-menu-open" : ""}`}>
      <div className="plaza-shell-body">
        <PlazaTopBar />
        <main className="app-main app-main-plaza">
          <EmailVerifyBanner />
          <ThemeOnboarding />
          <AppRoutes />
        </main>
        <ComposeFab />
        <BottomNav />
      </div>
      <PlazaSideMenu />
    </div>
  );
}

function AppRoutes() {
  return (
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
      <Route path="/arenas" element={<Arenas />} />
      <Route path="/arenas/:arenaKey" element={<ArenaDetail />} />
      <Route path="/spaces" element={<Spaces />} />
      <Route path="/spaces/:spaceId" element={<SpaceRoom />} />
      <Route path="/onboarding/topics" element={<OnboardingTopics />} />
      <Route path="/rewards" element={<Rewards />} />
      <Route path="/guidelines" element={<Guidelines />} />
      <Route path="/privacy" element={<Privacy />} />
      <Route path="/terms" element={<Terms />} />
      <Route path="*" element={<NotFound homeTo="/feed" homeLabel="Back to Square" />} />
    </Routes>
  );
}

export default function App() {
  const { token, user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <div className="page-loading">Starting BarathX…</div>;
  }

  // Private ops console — owner account only. Everyone else (incl. logged-out) gets a
  // normal 404 so the unlock screen is not public. Path defaults to /bx-ops.
  const opsPath = opsConsolePath();
  const onOpsPath =
    location.pathname === opsPath || location.pathname.startsWith(`${opsPath}/`);
  if (onOpsPath) {
    if (!canAccessOpsConsole(user)) {
      return (
        <AuthChrome>
          <NotFound homeTo={token ? "/feed" : "/"} homeLabel={token ? "Back to Square" : "Back to BarathX"} />
        </AuthChrome>
      );
    }
    return (
      <AdminChrome>
        <Admin />
      </AdminChrome>
    );
  }
  if (location.pathname === "/admin" || location.pathname.startsWith("/admin/")) {
    return (
      <AuthChrome>
        <NotFound homeTo={token ? "/feed" : "/"} homeLabel={token ? "Back to Square" : "Back to BarathX"} />
      </AuthChrome>
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
  if (location.pathname === "/privacy") {
    return (
      <AuthChrome legal>
        <Privacy />
      </AuthChrome>
    );
  }
  if (location.pathname === "/terms") {
    return (
      <AuthChrome legal>
        <Terms />
      </AuthChrome>
    );
  }
  if (location.pathname === "/guidelines") {
    return (
      <AuthChrome legal>
        <Guidelines />
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
        <Route path="/login" element={<Login />} />
        <Route
          path="/forgot-password"
          element={
            <AuthChrome>
              <ForgotPassword />
            </AuthChrome>
          }
        />
        <Route
          path="/privacy"
          element={
            <AuthChrome legal>
              <Privacy />
            </AuthChrome>
          }
        />
        <Route
          path="/terms"
          element={
            <AuthChrome legal>
              <Terms />
            </AuthChrome>
          }
        />
        <Route
          path="/guidelines"
          element={
            <AuthChrome legal>
              <Guidelines />
            </AuthChrome>
          }
        />
        {/* Unknown logged-out URLs → explicit 404 (not a silent landing bounce) */}
        <Route path="*" element={<NotFound homeTo="/" homeLabel="Back to BarathX" />} />
      </Routes>
    );
  }

  return (
    <PlazaMenuProvider>
      <PlazaShell />
    </PlazaMenuProvider>
  );
}
