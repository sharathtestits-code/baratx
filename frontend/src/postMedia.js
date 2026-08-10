/** True when a post has an attached image (not avatar/cover, not blank). */
export function postHasAttachedMedia(post) {
  const u = String(post?.image_url || "").trim();
  if (!u || u === "null" || u === "undefined") return false;
  const low = u.toLowerCase();
  if (low.includes("/media/")) return true;
  if (low.startsWith("data:image/")) return true;
  if (low.startsWith("http://") || low.startsWith("https://")) {
    return /\.(png|jpe?g|gif|webp|avif)(\?|#|$)/i.test(low) || low.includes("/media/");
  }
  return /\.(png|jpe?g|gif|webp|avif)(\?|#|$)/i.test(low);
}
