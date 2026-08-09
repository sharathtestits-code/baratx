import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api, socialApi, mediaUrl } from "../api";
import { useAuth } from "../context/AuthContext";
import PostCard from "../components/PostCard";
import Avatar from "../components/Avatar";
import { badgeOf, badgeNameClass, canManageBadges } from "../components/OfficialBadge";
import EditProfileModal from "../components/EditProfileModal";
import { IconCamera } from "../components/Icons";
import { useInfiniteScroll } from "../hooks/useInfiniteScroll";

const PAGE_SIZE = 20;
const PROTECTED_BLUE = new Set(["baratx", "sharath"]);

export default function Profile() {
  const { username } = useParams();
  const { token, user, updateUser } = useAuth();
  const navigate = useNavigate();

  const [profile, setProfile] = useState(null);
  const [posts, setPosts] = useState([]);
  const [profileLoading, setProfileLoading] = useState(true);
  const [postsLoading, setPostsLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [error, setError] = useState("");
  const [followBusy, setFollowBusy] = useState(false);
  const [badgeBusy, setBadgeBusy] = useState(false);
  const [notifyBadge, setNotifyBadge] = useState(true);
  const [moreMenuOpen, setMoreMenuOpen] = useState(false);
  const [editMenuOpen, setEditMenuOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);

  const [avatarBusy, setAvatarBusy] = useState(false);
  const [coverBusy, setCoverBusy] = useState(false);
  const avatarInputRef = useRef(null);
  const coverInputRef = useRef(null);
  const editMenuRef = useRef(null);
  const loadingMoreRef = useRef(false);

  const [profileTab, setProfileTab] = useState("square");

  useEffect(() => {
    loadProfile();
    loadPosts();
    setEditMenuOpen(false);
    setEditModalOpen(false);
    setProfileTab("square");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [username]);

  useEffect(() => {
    if (!editMenuOpen) return;
    function handlePointerDown(e) {
      if (editMenuRef.current && !editMenuRef.current.contains(e.target)) {
        setEditMenuOpen(false);
      }
    }
    document.addEventListener("pointerdown", handlePointerDown);
    return () => document.removeEventListener("pointerdown", handlePointerDown);
  }, [editMenuOpen]);

  async function loadProfile() {
    setProfileLoading(true);
    setError("");
    try {
      const data = await api.getProfile(username, token);
      setProfile(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setProfileLoading(false);
    }
  }

  async function loadPosts() {
    setPostsLoading(true);
    setHasMore(true);
    try {
      const data = await api.getUserPosts(username, token);
      setPosts(data);
      setHasMore(data.length >= PAGE_SIZE);
    } catch {
      setPosts([]);
      setHasMore(false);
    } finally {
      setPostsLoading(false);
    }
  }

  const loadMore = useCallback(async () => {
    if (!username || loadingMoreRef.current || !hasMore || posts.length === 0) return;
    loadingMoreRef.current = true;
    setLoadingMore(true);
    const before = posts[posts.length - 1]?.created_at;
    try {
      const data = await api.getUserPosts(username, token, before);
      setPosts((prev) => {
        const seen = new Set(prev.map((p) => p.id));
        const next = [...prev];
        for (const post of data) {
          if (!seen.has(post.id)) {
            seen.add(post.id);
            next.push(post);
          }
        }
        return next;
      });
      setHasMore(data.length >= PAGE_SIZE);
    } catch {
      // keep existing list
    } finally {
      loadingMoreRef.current = false;
      setLoadingMore(false);
    }
  }, [username, token, hasMore, posts]);

  const setSentinel = useInfiniteScroll({
    disabled: postsLoading || loadingMore || !hasMore || posts.length === 0,
    onLoadMore: loadMore,
  });

  async function toggleFollow() {
    if (!token || followBusy || !profile) return;
    setFollowBusy(true);
    const wasFollowing = profile.is_following;
    setProfile((p) => ({
      ...p,
      is_following: !wasFollowing,
      follower_count: wasFollowing ? p.follower_count - 1 : p.follower_count + 1,
    }));
    try {
      const updated = wasFollowing
        ? await api.unfollow(token, username)
        : await api.follow(token, username);
      setProfile(updated);
    } catch (err) {
      setError(err.message);
      loadProfile();
    } finally {
      setFollowBusy(false);
    }
  }

  async function changeBadge(nextBadge, confirmMsg) {
    if (!token || !profile || badgeBusy) return;
    if (confirmMsg && !window.confirm(confirmMsg)) return;
    setBadgeBusy(true);
    setError("");
    try {
      const updated = await api.setBadge(token, profile.username, nextBadge, notifyBadge);
      setProfile(updated);
    } catch (err) {
      setError(err.message);
    } finally {
      setBadgeBusy(false);
    }
  }

  async function handleAvatarChange(e) {
    const file = e.target.files?.[0];
    if (!file || !token) return;
    setAvatarBusy(true);
    setError("");
    setEditMenuOpen(false);
    try {
      const updated = await api.uploadAvatar(token, file);
      setProfile((p) => ({ ...p, avatar_url: updated.avatar_url }));
      updateUser({ avatar_url: updated.avatar_url });
    } catch (err) {
      setError(err.message);
    } finally {
      setAvatarBusy(false);
      if (avatarInputRef.current) avatarInputRef.current.value = "";
    }
  }

  async function handleCoverChange(e) {
    const file = e.target.files?.[0];
    if (!file || !token) return;
    setCoverBusy(true);
    setError("");
    setEditMenuOpen(false);
    try {
      const updated = await api.uploadCover(token, file);
      setProfile((p) => ({ ...p, cover_url: updated.cover_url }));
    } catch (err) {
      setError(err.message);
    } finally {
      setCoverBusy(false);
      if (coverInputRef.current) coverInputRef.current.value = "";
    }
  }

  function handleDeleted(postId) {
    setPosts((prev) => prev.filter((p) => p.id !== postId));
  }

  function handleProfileSaved(updated) {
    setProfile(updated);
    if (updated?.username && updated.username !== username) {
      navigate(`/u/${updated.username}`, { replace: true });
    }
  }

  if (profileLoading) return <div className="page-loading">Loading profile...</div>;
  if (error && !profile) return <div className="error">{error}</div>;
  if (!profile) return null;

  const isMe = user && user.username === profile.username;
  const postLabel = postsLoading ? "…" : `${posts.length}${hasMore ? "+" : ""} post${posts.length === 1 ? "" : "s"}`;

  return (
    <div className="plaza-page plaza-profile profile-cinematic">
      <div className="profile-topbar">
        <div className="profile-topbar-text">
          <h1 className="profile-topbar-name">{profile.display_name}</h1>
          <div className="profile-topbar-meta">{postLabel}</div>
        </div>
      </div>

      <div
        className={`profile-cover${profile.cover_url ? " has-photo" : ""}`}
        style={profile.cover_url ? { backgroundImage: `url(${mediaUrl(profile.cover_url)})` } : undefined}
      >
        {isMe && (
          <button
            type="button"
            className="cover-edit-btn"
            onClick={() => coverInputRef.current?.click()}
            disabled={coverBusy}
            title="Change cover photo"
          >
            <IconCamera />
          </button>
        )}
        <input
          ref={coverInputRef}
          type="file"
          accept="image/png,image/jpeg,image/gif,image/webp"
          onChange={handleCoverChange}
          hidden
        />
      </div>

      <div className="profile-card">
        <div className="profile-card-top">
          <div className="profile-avatar-wrap">
            <Avatar name={profile.display_name} username={profile.username} url={profile.avatar_url} size={88} />
            {isMe && (
              <button
                type="button"
                className="avatar-edit-btn"
                onClick={() => avatarInputRef.current?.click()}
                disabled={avatarBusy}
                title="Change profile photo"
              >
                <IconCamera />
              </button>
            )}
            <input
              ref={avatarInputRef}
              type="file"
              accept="image/png,image/jpeg,image/gif,image/webp"
              onChange={handleAvatarChange}
              hidden
            />
          </div>

          <div className="profile-actions">
            {isMe ? (
              <div className="profile-edit-wrap" ref={editMenuRef}>
                <button
                  type="button"
                  className="profile-edit-btn"
                  onClick={() => setEditMenuOpen((open) => !open)}
                  aria-expanded={editMenuOpen}
                  aria-haspopup="menu"
                >
                  Edit profile
                </button>
                {editMenuOpen && (
                  <div className="profile-edit-menu" role="menu">
                    <button
                      type="button"
                      role="menuitem"
                      onClick={() => {
                        setEditMenuOpen(false);
                        setEditModalOpen(true);
                      }}
                    >
                      Edit details
                    </button>
                    <button
                      type="button"
                      role="menuitem"
                      onClick={() => avatarInputRef.current?.click()}
                      disabled={avatarBusy}
                    >
                      Change photo
                    </button>
                    <button
                      type="button"
                      role="menuitem"
                      onClick={() => coverInputRef.current?.click()}
                      disabled={coverBusy}
                    >
                      Change cover
                    </button>
                  </div>
                )}
              </div>
            ) : (
              token && (
                <div className="profile-action-row">
                  <button
                    type="button"
                    className={`follow-btn ${profile.is_following ? "following" : ""}`}
                    onClick={toggleFollow}
                    disabled={followBusy}
                  >
                    {profile.is_following ? "Following" : "Follow"}
                  </button>
                  <Link to={`/messages/${profile.username}`} className="profile-edit-btn">
                    Message
                  </Link>
                  <div className="profile-edit-wrap">
                    <button
                      type="button"
                      className="profile-edit-btn"
                      onClick={() => setMoreMenuOpen((open) => !open)}
                      aria-expanded={moreMenuOpen}
                      aria-haspopup="menu"
                      aria-label="More actions"
                    >
                      More
                    </button>
                    {moreMenuOpen && (
                      <div className="profile-edit-menu" role="menu">
                        <button
                          type="button"
                          role="menuitem"
                          onClick={async () => {
                            setMoreMenuOpen(false);
                            try {
                              await socialApi.mute(token, profile.username);
                              window.alert(`Muted @${profile.username}`);
                            } catch (err) {
                              setError(err.message);
                            }
                          }}
                        >
                          Mute
                        </button>
                        <button
                          type="button"
                          role="menuitem"
                          onClick={async () => {
                            setMoreMenuOpen(false);
                            if (!window.confirm(`Block @${profile.username}?`)) return;
                            try {
                              await socialApi.block(token, profile.username);
                              window.alert(`Blocked @${profile.username}`);
                              navigate("/feed");
                            } catch (err) {
                              setError(err.message);
                            }
                          }}
                        >
                          Block
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              )
            )}
          </div>
        </div>

        {canManageBadges(user) && !isMe && profile && (
          <div className="badge-control-panel" aria-label="Badge controls">
            <div className="badge-control-head">
              <strong>Badge controls</strong>
              <span className="badge-control-status">
                Current: {badgeOf(profile) === "none" ? "no color" : badgeOf(profile)}
              </span>
            </div>
            <div className="badge-mod-wrap">
              {badgeOf(profile) === "none" && (
                <button
                  type="button"
                  className="profile-edit-btn badge-grant-btn gold"
                  disabled={badgeBusy}
                  onClick={() => changeBadge("gold", `Grant gold to @${profile.username}?`)}
                >
                  {badgeBusy ? "…" : "Grant gold"}
                </button>
              )}
              {badgeOf(profile) === "gold" && (
                <>
                  <button
                    type="button"
                    className="profile-edit-btn badge-grant-btn blue"
                    disabled={badgeBusy}
                    onClick={() =>
                      changeBadge("blue", `Promote @${profile.username} from gold to blue?`)
                    }
                  >
                    {badgeBusy ? "…" : "Promote to blue"}
                  </button>
                  <button
                    type="button"
                    className="profile-edit-btn badge-grant-btn demote"
                    disabled={badgeBusy}
                    onClick={() =>
                      changeBadge(
                        "none",
                        `Remove gold from @${profile.username}? Name returns to no color.`
                      )
                    }
                  >
                    {badgeBusy ? "…" : "Remove gold"}
                  </button>
                </>
              )}
              {badgeOf(profile) === "blue" &&
                !PROTECTED_BLUE.has((profile.username || "").toLowerCase()) && (
                  <button
                    type="button"
                    className="profile-edit-btn badge-grant-btn demote"
                    disabled={badgeBusy}
                    onClick={() =>
                      changeBadge(
                        "gold",
                        `Demote @${profile.username} from blue to gold for security?`
                      )
                    }
                  >
                    {badgeBusy ? "…" : "Demote to gold"}
                  </button>
                )}
              {badgeOf(profile) === "blue" &&
                PROTECTED_BLUE.has((profile.username || "").toLowerCase()) && (
                  <span className="badge-control-protected">Protected blue founder</span>
                )}
              <label className="badge-notify-opt">
                <input
                  type="checkbox"
                  checked={notifyBadge}
                  onChange={(e) => setNotifyBadge(e.target.checked)}
                />
                Notify user
              </label>
            </div>
            <p className="badge-control-hint">
              Open any other user’s profile (not your own) to grant, promote, or demote.
            </p>
          </div>
        )}

        {isMe && canManageBadges(user) && (
          <p className="badge-control-hint">
            You’re logged in as blue. Open another user’s profile to manage their badge.
          </p>
        )}
        <div className="profile-identity">
          <h2 className={badgeNameClass(profile, "profile-name")}>{profile.display_name}</h2>
          <div className={badgeNameClass(profile, "profile-username")}>@{profile.username}</div>
        </div>

        {profile.bio && <p className="profile-bio">{profile.bio}</p>}

        <div className="profile-orbit-row" aria-label="Orbits">
          <span className="profile-orbit-label">In their orbits</span>
          <div className="profile-orbit-chips">
            {["Sports", "Politics", "News", "Spirituality"].map((label) => (
              <Link key={label} to={`/search?q=${encodeURIComponent(label)}`} className="profile-orbit-chip">
                {label}
              </Link>
            ))}
            <Link to="/arenas" className="profile-orbit-chip profile-orbit-chip-more">
              Arenas
            </Link>
          </div>
        </div>

        {error && <div className="error">{error}</div>}

        <div className="profile-stats">
          <Link to={`/u/${profile.username}/following`} className="profile-stat-link">
            <b>{profile.following_count}</b> Following
          </Link>
          <Link to={`/u/${profile.username}/followers`} className="profile-stat-link">
            <b>{profile.follower_count}</b> Followers
          </Link>
        </div>
      </div>

      <div className="feed-tabs profile-tabs" role="tablist" aria-label="Profile sections">
        <button
          type="button"
          className={`feed-tab${profileTab === "square" ? " active" : ""}`}
          role="tab"
          aria-selected={profileTab === "square"}
          onClick={() => setProfileTab("square")}
        >
          Square
        </button>
        <button
          type="button"
          className={`feed-tab${profileTab === "echoes" ? " active" : ""}`}
          role="tab"
          aria-selected={profileTab === "echoes"}
          onClick={() => setProfileTab("echoes")}
        >
          Echoes
        </button>
        <button
          type="button"
          className={`feed-tab${profileTab === "media" ? " active" : ""}`}
          role="tab"
          aria-selected={profileTab === "media"}
          onClick={() => setProfileTab("media")}
        >
          Media
        </button>
        <Link to="/arenas" className="feed-tab feed-tab-link">
          Arenas
        </Link>
      </div>

      {postsLoading ? (
        <p className="hint profile-posts-hint">Loading posts...</p>
      ) : (() => {
        const visible =
          profileTab === "media"
            ? posts.filter((p) => p.image_url)
            : profileTab === "echoes"
              ? posts.filter((p) => (p.repost_count || 0) > 0 || (p.reply_count || 0) > 0)
              : posts;
        if (visible.length === 0) {
          return (
            <div className="empty-state">
              <p className="empty-state-title">
                {profileTab === "media"
                  ? "No media yet"
                  : profileTab === "echoes"
                    ? "No echoes yet"
                    : "No posts yet"}
              </p>
              <p className="hint">
                {isMe ? "Share your first post from The Square." : "Nothing here yet."}
              </p>
            </div>
          );
        }
        return (
          <>
            <div className="post-list">
              {visible.map((post) => (
                <PostCard key={post.id} post={post} onDeleted={handleDeleted} />
              ))}
            </div>
            {profileTab === "square" && (
              <>
                <div ref={setSentinel} className="scroll-sentinel" aria-hidden="true" />
                {loadingMore && <p className="hint load-more-hint">Loading more...</p>}
                {!hasMore && posts.length > 0 && <p className="hint load-more-hint">End of posts.</p>}
              </>
            )}
          </>
        );
      })()}

      {isMe && (
        <EditProfileModal
          open={editModalOpen}
          profile={profile}
          onClose={() => setEditModalOpen(false)}
          onSaved={handleProfileSaved}
        />
      )}
    </div>
  );
}
