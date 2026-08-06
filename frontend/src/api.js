const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";
const DEFAULT_TIMEOUT_MS = 15000;

async function request(path, options = {}) {
  const { timeoutMs = DEFAULT_TIMEOUT_MS, headers: extraHeaders, signal: externalSignal, ...rest } =
    options;
  const controller = new AbortController();
  const onExternalAbort = () => controller.abort();
  if (externalSignal) {
    if (externalSignal.aborted) controller.abort();
    else externalSignal.addEventListener("abort", onExternalAbort, { once: true });
  }
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  const headers = { ...(extraHeaders || {}) };
  // Only set JSON content-type when sending a body — bare DELETE/GET with
  // Content-Type: application/json can confuse some proxies.
  if (rest.body != null && !headers["Content-Type"] && !headers["content-type"]) {
    headers["Content-Type"] = "application/json";
  }

  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...rest,
      signal: controller.signal,
      headers,
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      const detail = Array.isArray(data.detail)
        ? data.detail.map((d) => d.msg).join(", ")
        : data.detail || "Something went wrong";
      throw new Error(detail);
    }

    return data;
  } catch (err) {
    if (err?.name === "AbortError") {
      throw new Error("Request timed out. Check your connection and try again.");
    }
    if (err instanceof TypeError || /failed to fetch/i.test(err?.message || "")) {
      throw new Error("Could not reach BaratX. Check your connection and try again.");
    }
    throw err;
  } finally {
    clearTimeout(timer);
    if (externalSignal) externalSignal.removeEventListener("abort", onExternalAbort);
  }
}

function authHeaders(token) {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export const api = {
  signupEmail: (body) =>
    request("/auth/signup/email", { method: "POST", body: JSON.stringify(body) }),
  loginEmail: (body) =>
    request("/auth/login/email", { method: "POST", body: JSON.stringify(body) }),

  loginGoogle: (body) =>
    request("/auth/google", { method: "POST", body: JSON.stringify(body) }),

  verifyEmail: (token) =>
    request("/auth/verify-email", { method: "POST", body: JSON.stringify({ token }) }),
  resendVerification: (token) =>
    request("/auth/resend-verification", {
      method: "POST",
      headers: authHeaders(token),
    }),

  forgotPassword: (email) =>
    request("/auth/forgot-password", { method: "POST", body: JSON.stringify({ email }) }),
  resetPassword: (body) =>
    request("/auth/reset-password", { method: "POST", body: JSON.stringify(body) }),

  signupPhoneRequestOtp: (phone, region) =>
    request("/auth/signup/phone/request-otp", {
      method: "POST",
      body: JSON.stringify({ phone, region: region || undefined }),
    }),
  signupPhoneVerify: (body) =>
    request("/auth/signup/phone/verify", { method: "POST", body: JSON.stringify(body) }),

  loginPhoneRequestOtp: (phone, region) =>
    request("/auth/login/phone/request-otp", {
      method: "POST",
      body: JSON.stringify({ phone, region: region || undefined }),
    }),
  loginPhoneVerify: (body) =>
    request("/auth/login/phone/verify", { method: "POST", body: JSON.stringify(body) }),

  me: (token) => request("/users/me", { headers: authHeaders(token), timeoutMs: 12000 }),

  updateMe: (token, body) =>
    request("/users/me", {
      method: "PATCH",
      headers: authHeaders(token),
      body: JSON.stringify(body),
    }),

  getProfile: (username, token) =>
    request(`/users/${encodeURIComponent(username)}`, { headers: authHeaders(token) }),

  getUserPosts: (username, token, before) =>
    request(
      `/users/${encodeURIComponent(username)}/posts${before ? `?before=${encodeURIComponent(before)}` : ""}`,
      { headers: authHeaders(token) }
    ),

  follow: (token, username) =>
    request(`/users/${encodeURIComponent(username)}/follow`, {
      method: "POST",
      headers: authHeaders(token),
    }),

  unfollow: (token, username) =>
    request(`/users/${encodeURIComponent(username)}/follow`, {
      method: "DELETE",
      headers: authHeaders(token),
    }),

  bootstrapFollows: (token) =>
    request("/users/me/bootstrap-follows", {
      method: "POST",
      headers: authHeaders(token),
    }),

  uploadAvatar: async (token, file) => {
    const form = new FormData();
    form.append("image", file);
    const res = await fetch(`${API_BASE}/users/me/avatar`, {
      method: "POST",
      headers: authHeaders(token),
      body: form,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || "Could not upload profile photo");
    return data;
  },

  removeAvatar: (token) =>
    request("/users/me/avatar", { method: "DELETE", headers: authHeaders(token) }),

  uploadCover: async (token, file) => {
    const form = new FormData();
    form.append("image", file);
    const res = await fetch(`${API_BASE}/users/me/cover`, {
      method: "POST",
      headers: authHeaders(token),
      body: form,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || "Could not upload cover photo");
    return data;
  },

  removeCover: (token) =>
    request("/users/me/cover", { method: "DELETE", headers: authHeaders(token) }),

  getFollowers: (username, token) =>
    request(`/users/${encodeURIComponent(username)}/followers`, { headers: authHeaders(token) }),

  getFollowing: (username, token) =>
    request(`/users/${encodeURIComponent(username)}/following`, { headers: authHeaders(token) }),
};

export const postsApi = {
  list: (token, { feed = "global", before } = {}) => {
    const params = new URLSearchParams();
    params.set("feed", feed);
    if (before) params.set("before", before);
    return request(`/posts?${params.toString()}`, { headers: authHeaders(token) });
  },

  get: (id, token) => request(`/posts/${id}`, { headers: authHeaders(token) }),

  create: async (token, { text, image, quotePostId }) => {
    const form = new FormData();
    form.append("text", text);
    if (image) form.append("image", image);
    if (quotePostId) form.append("quote_post_id", quotePostId);

    const res = await fetch(`${API_BASE}/posts`, {
      method: "POST",
      headers: authHeaders(token),
      body: form,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const detail = Array.isArray(data.detail)
        ? data.detail.map((d) => d.msg).join(", ")
        : data.detail || "Could not create post";
      throw new Error(detail);
    }
    return data;
  },

  remove: (token, id) =>
    request(`/posts/${id}`, { method: "DELETE", headers: authHeaders(token) }),
};

export { API_BASE };

export const socialApi = {
  like: (token, postId) =>
    request(`/posts/${postId}/like`, { method: "POST", headers: authHeaders(token) }),

  unlike: (token, postId) =>
    request(`/posts/${postId}/like`, { method: "DELETE", headers: authHeaders(token) }),

  repost: (token, postId) =>
    request(`/posts/${postId}/repost`, { method: "POST", headers: authHeaders(token) }),

  unrepost: (token, postId) =>
    request(`/posts/${postId}/repost`, { method: "DELETE", headers: authHeaders(token) }),

  bookmark: (token, postId) =>
    request(`/posts/${postId}/bookmark`, { method: "POST", headers: authHeaders(token) }),

  unbookmark: (token, postId) =>
    request(`/posts/${postId}/bookmark`, { method: "DELETE", headers: authHeaders(token) }),

  listBookmarks: (token) => request("/bookmarks", { headers: authHeaders(token) }),

  listReplies: (postId) => request(`/posts/${postId}/replies`),

  createReply: (token, postId, text, parentReplyId) =>
    request(`/posts/${postId}/replies`, {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify({ text, parent_reply_id: parentReplyId || null }),
    }),

  likeReply: (token, replyId) =>
    request(`/replies/${replyId}/like`, { method: "POST", headers: authHeaders(token) }),

  unlikeReply: (token, replyId) =>
    request(`/replies/${replyId}/like`, { method: "DELETE", headers: authHeaders(token) }),

  block: (token, username) =>
    request(`/users/${encodeURIComponent(username)}/block`, {
      method: "POST",
      headers: authHeaders(token),
    }),

  unblock: (token, username) =>
    request(`/users/${encodeURIComponent(username)}/block`, {
      method: "DELETE",
      headers: authHeaders(token),
    }),

  mute: (token, username) =>
    request(`/users/${encodeURIComponent(username)}/mute`, {
      method: "POST",
      headers: authHeaders(token),
    }),

  unmute: (token, username) =>
    request(`/users/${encodeURIComponent(username)}/mute`, {
      method: "DELETE",
      headers: authHeaders(token),
    }),

  listMutes: (token) => request("/users/me/mutes", { headers: authHeaders(token) }),

  listBlocks: (token) => request("/users/me/blocks", { headers: authHeaders(token) }),

  report: (token, body) =>
    request("/reports", {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(body),
    }),

  hashtag: (tag, token) =>
    request(`/hashtags/${encodeURIComponent(tag)}`, { headers: authHeaders(token) }),
};

export const listsApi = {
  list: (token) => request("/lists", { headers: authHeaders(token) }),
  get: (token, id) => request(`/lists/${id}`, { headers: authHeaders(token) }),
  create: (token, body) =>
    request("/lists", {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(body),
    }),
  update: (token, id, body) =>
    request(`/lists/${id}`, {
      method: "PATCH",
      headers: authHeaders(token),
      body: JSON.stringify(body),
    }),
  remove: (token, id) =>
    request(`/lists/${id}`, { method: "DELETE", headers: authHeaders(token) }),
  members: (token, id) => request(`/lists/${id}/members`, { headers: authHeaders(token) }),
  addMember: (token, id, username) =>
    request(`/lists/${id}/members/${encodeURIComponent(username)}`, {
      method: "POST",
      headers: authHeaders(token),
    }),
  removeMember: (token, id, username) =>
    request(`/lists/${id}/members/${encodeURIComponent(username)}`, {
      method: "DELETE",
      headers: authHeaders(token),
    }),
  feed: (token, id) => request(`/lists/${id}/feed`, { headers: authHeaders(token) }),
};

export const communitiesApi = {
  list: (token) => request("/communities", { headers: authHeaders(token) }),
  get: (token, slug) =>
    request(`/communities/${encodeURIComponent(slug)}`, { headers: authHeaders(token) }),
  create: (token, body) =>
    request("/communities", {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(body),
    }),
  join: (token, slug) =>
    request(`/communities/${encodeURIComponent(slug)}/join`, {
      method: "POST",
      headers: authHeaders(token),
    }),
  leave: (token, slug) =>
    request(`/communities/${encodeURIComponent(slug)}/leave`, {
      method: "POST",
      headers: authHeaders(token),
    }),
  feed: (token, slug) =>
    request(`/communities/${encodeURIComponent(slug)}/feed`, { headers: authHeaders(token) }),
  post: (token, slug, text) =>
    request(`/communities/${encodeURIComponent(slug)}/posts`, {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify({ text }),
    }),
};

export const spacesApi = {
  list: (token, status = "open") =>
    request(`/spaces?status=${encodeURIComponent(status)}`, { headers: authHeaders(token) }),
  get: (token, id) => request(`/spaces/${id}`, { headers: authHeaders(token) }),
  create: (token, body) =>
    request("/spaces", {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(body),
    }),
  close: (token, id) =>
    request(`/spaces/${id}/close`, { method: "POST", headers: authHeaders(token) }),
  feed: (token, id) => request(`/spaces/${id}/feed`, { headers: authHeaders(token) }),
  post: (token, id, text) =>
    request(`/spaces/${id}/posts`, {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify({ text }),
    }),
};

export const messagesApi = {
  conversations: (token) => request("/messages", { headers: authHeaders(token) }),
  thread: (token, username) =>
    request(`/messages/${encodeURIComponent(username)}`, { headers: authHeaders(token) }),
  send: (token, username, text) =>
    request(`/messages/${encodeURIComponent(username)}`, {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify({ text }),
    }),
};

export const searchApi = {
  search: (q, token) =>
    request(`/search?q=${encodeURIComponent(q)}`, { headers: authHeaders(token) }),
};

export const notificationsApi = {
  list: (token) => request("/notifications", { headers: authHeaders(token) }),
  unreadCount: (token) =>
    request("/notifications/unread-count", { headers: authHeaders(token) }),
  markRead: (token) =>
    request("/notifications/read", { method: "POST", headers: authHeaders(token) }),
};

export const adminApi = {
  stats: (adminSecret) =>
    request("/admin/stats", { headers: { "X-Admin-Secret": adminSecret } }),
  users: (adminSecret, { limit = 50, offset = 0 } = {}) =>
    request(`/admin/users?limit=${limit}&offset=${offset}`, {
      headers: { "X-Admin-Secret": adminSecret },
    }),
  recentPosts: (adminSecret, { limit = 30, newUsersOnly = true, days = 7 } = {}) =>
    request(
      `/admin/recent-posts?limit=${limit}&new_users_only=${newUsersOnly ? "true" : "false"}&days=${days}`,
      { headers: { "X-Admin-Secret": adminSecret } }
    ),
  createPost: (adminSecret, body) =>
    request("/admin/posts", {
      method: "POST",
      headers: { "X-Admin-Secret": adminSecret },
      body: JSON.stringify(body),
    }),
  createReply: (adminSecret, body) =>
    request("/admin/replies", {
      method: "POST",
      headers: { "X-Admin-Secret": adminSecret },
      body: JSON.stringify(body),
    }),
};
