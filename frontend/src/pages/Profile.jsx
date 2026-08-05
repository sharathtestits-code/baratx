import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { API_BASE, api, socialApi } from "../api";
import { useAuth } from "../context/AuthContext";
import PostCard from "../components/PostCard";
import Avatar from "../components/Avatar";
import EditProfileModal from "../components/EditProfileModal";
import { IconCamera } from "../components/Icons";
import { useInfiniteScroll } from "../hooks/useInfiniteScroll";

const PAGE_SIZE = 20;

const LANGUAGE_LABELS = {
  en: "English",
  hi: "Hindi",
  te: "Telugu",
};

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
  const [editMenuOpen, setEditMenuOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);

  const [avatarBusy, setAvatarBusy] = useState(false);
  const [coverBusy, setCoverBusy] = useState(false);
  const avatarInputRef = useRef(null);
  const coverInputRef = useRef(null);
  const editMenuRef = useRef(null);
  const loadingMoreRef = useRef(false);

  useEffect(() => {
    loadProfile();
    loadPosts();
    setEditMenuOpen(false);
    setEditModalOpen(false);
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
  }

  if (profileLoading) return <div className="page-loading">Loading profile...</div>;
  if (error && !profile) return <div className="error">{error}</div>;
  if (!profile) return null;

  const isMe = user && user.username === profile.username;
  const postLabel = postsLoading ? "…" : `${posts.length}${hasMore ? "+" : ""} post${posts.length === 1 ? "" : "s"}`;
  const languageLabel = LANGUAGE_LABELS[profile.language] || profile.language;

  return (
    <div className="feed-wrap">
      <div className="profile-topbar">
        <div className="profile-topbar-text">
          <h1 className="profile-topbar-name">{profile.display_name}</h1>
          <div className="profile-topbar-meta">{postLabel}</div>
        </div>
      </div>

      <div
        className={`profile-cover${profile.cover_url ? " has-photo" : ""}`}
        style={profile.cover_url ? { backgroundImage: `url(${API_BASE}${profile.cover_url})` } : undefined}
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
                  <button
                    type="button"
                    className="profile-edit-btn"
                    onClick={async () => {
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
                    className="profile-edit-btn"
                    onClick={async () => {
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
              )
            )}
          </div>
        </div>

        <div className="profile-identity">
          <h2 className="profile-name">{profile.display_name}</h2>
          <div className="profile-username">@{profile.username}</div>
        </div>

        {profile.bio && <p className="profile-bio">{profile.bio}</p>}

        <div className="profile-meta">
          <span className="profile-meta-item">{languageLabel}</span>
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
        <button type="button" className="feed-tab active" role="tab" aria-selected="true">
          Posts
        </button>
      </div>

      {postsLoading ? (
        <p className="hint profile-posts-hint">Loading posts...</p>
      ) : posts.length === 0 ? (
        <div className="empty-state">
          <p className="empty-state-title">No posts yet</p>
          <p className="hint">{isMe ? "Share your first post from Home." : "This account hasn’t posted yet."}</p>
        </div>
      ) : (
        <>
          <div className="post-list">
            {posts.map((post) => (
              <PostCard key={post.id} post={post} onDeleted={handleDeleted} />
            ))}
          </div>
          <div ref={setSentinel} className="scroll-sentinel" aria-hidden="true" />
          {loadingMore && <p className="hint load-more-hint">Loading more...</p>}
          {!hasMore && posts.length > 0 && <p className="hint load-more-hint">End of posts.</p>}
        </>
      )}

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
