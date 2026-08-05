import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";
import Avatar from "../components/Avatar";

export default function FollowList() {
  const { username, kind } = useParams();
  const { token, user } = useAuth();
  const navigate = useNavigate();
  const [people, setPeople] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [busyId, setBusyId] = useState("");

  const title = kind === "following" ? "Following" : "Followers";

  useEffect(() => {
    let cancelled = false;
    async function load() {
      if (kind !== "followers" && kind !== "following") {
        navigate(`/u/${username}`, { replace: true });
        return;
      }
      setLoading(true);
      setError("");
      try {
        const data =
          kind === "following"
            ? await api.getFollowing(username, token)
            : await api.getFollowers(username, token);
        if (!cancelled) setPeople(data);
      } catch (err) {
        if (!cancelled) setError(err.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [username, kind, token, navigate]);

  async function toggleFollow(person) {
    if (!token || busyId || person.username === user?.username) return;
    setBusyId(person.id);
    const wasFollowing = person.is_following;
    setPeople((prev) =>
      prev.map((p) =>
        p.id === person.id
          ? {
              ...p,
              is_following: !wasFollowing,
              follower_count: wasFollowing ? p.follower_count - 1 : p.follower_count + 1,
            }
          : p
      )
    );
    try {
      const updated = wasFollowing
        ? await api.unfollow(token, person.username)
        : await api.follow(token, person.username);
      setPeople((prev) => prev.map((p) => (p.id === person.id ? { ...p, ...updated } : p)));
    } catch (err) {
      setError(err.message);
    } finally {
      setBusyId("");
    }
  }

  return (
    <div className="feed-wrap">
      <div className="feed-header follow-list-header">
        <button type="button" className="back-btn" onClick={() => navigate(`/u/${username}`)}>
          ←
        </button>
        <div>
          <h1>{title}</h1>
          <div className="hint">@{username}</div>
        </div>
      </div>

      {loading ? (
        <p className="hint">Loading…</p>
      ) : error ? (
        <div className="error">{error}</div>
      ) : people.length === 0 ? (
        <div className="empty-state">
          <p className="empty-state-title">
            {kind === "following" ? "Not following anyone yet" : "No followers yet"}
          </p>
        </div>
      ) : (
        <div className="people-list">
          {people.map((person) => (
            <div key={person.id} className="people-row">
              <Link to={`/u/${person.username}`} className="people-main">
                <Avatar
                  name={person.display_name}
                  username={person.username}
                  url={person.avatar_url}
                  size={48}
                />
                <div>
                  <div className="people-name">{person.display_name}</div>
                  <div className="people-username">@{person.username}</div>
                  {person.bio && <div className="people-bio">{person.bio}</div>}
                </div>
              </Link>
              {user && person.username !== user.username && (
                <button
                  type="button"
                  className={`follow-btn ${person.is_following ? "following" : ""}`}
                  onClick={() => toggleFollow(person)}
                  disabled={busyId === person.id}
                >
                  {person.is_following ? "Following" : "Follow"}
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
