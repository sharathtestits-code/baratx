import { Link, Navigate, Route, Routes } from "react-router-dom";
import Landing from "./pages/Landing";
import Signup from "./pages/Signup";
import Login from "./pages/Login";
import Feed from "./pages/Feed";
import Profile from "./pages/Profile";
import Search from "./pages/Search";
import PostDetail from "./pages/PostDetail";
import Sidebar from "./components/Sidebar";
import RightRail from "./components/RightRail";
import BottomNav from "./components/BottomNav";
import Logo from "./components/Logo";
import { useAuth } from "./context/AuthContext";

export default function App() {
  const { token } = useAuth();

  if (!token) {
    return (
      <div className="page">
        <header className="topbar">
          <Link to="/" className="brand" aria-label="BaratX Home">
            <Logo variant="full" className="topbar-logo" />
          </Link>
          <nav className="topnav">
            <Link to="/login">Log in</Link>
            <Link to="/signup" className="topnav-cta">
              Sign up
            </Link>
          </nav>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/login" element={<Login />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <Sidebar />
      <main className="app-main">
        <Routes>
          <Route path="/" element={<Navigate to="/feed" replace />} />
          <Route path="/signup" element={<Navigate to="/feed" replace />} />
          <Route path="/login" element={<Navigate to="/feed" replace />} />
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
