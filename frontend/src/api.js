const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    const detail = Array.isArray(data.detail)
      ? data.detail.map((d) => d.msg).join(", ")
      : data.detail || "Something went wrong";
    throw new Error(detail);
  }

  return data;
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

  signupPhoneRequestOtp: (phone) =>
    request("/auth/signup/phone/request-otp", { method: "POST", body: JSON.stringify({ phone }) }),
  signupPhoneVerify: (body) =>
    request("/auth/signup/phone/verify", { method: "POST", body: JSON.stringify(body) }),

  loginPhoneRequestOtp: (phone) =>
    request("/auth/login/phone/request-otp", { method: "POST", body: JSON.stringify({ phone }) }),
  loginPhoneVerify: (body) =>
    request("/auth/login/phone/verify", { method: "POST", body: JSON.stringify(body) }),

  me: (token) => request("/users/me", { headers: authHeaders(token) }),

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
};

export const postsApi = {
  list: (token, { feed = "global", before } = {}) => {
    const params = new URLSearchParams();
    params.set("feed", feed);
    if (before) params.set("before", before);
    return request(`/posts?${params.toString()}`, { headers: authHeaders(token) });
  },

  get: (id, token) => request(`/posts/${id}`, { headers: authHeaders(token) }),

  create: async (token, { text, image }) => {
    const form = new FormData();
    form.append("text", text);
    if (image) form.append("image", image);

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

  listReplies: (postId) => request(`/posts/${postId}/replies`),

  createReply: (token, postId, text) =>
    request(`/posts/${postId}/replies`, {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify({ text }),
    }),

  likeReply: (token, replyId) =>
    request(`/replies/${replyId}/like`, { method: "POST", headers: authHeaders(token) }),

  unlikeReply: (token, replyId) =>
    request(`/replies/${replyId}/like`, { method: "DELETE", headers: authHeaders(token) }),
};

export const searchApi = {
  search: (q, token) =>
    request(`/search?q=${encodeURIComponent(q)}`, { headers: authHeaders(token) }),
};
