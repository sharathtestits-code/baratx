import { useEffect, useState } from "react";

/**
 * Calls `onLoadMore` when the sentinel element enters the viewport.
 * Skips while `disabled` (loading / no more pages).
 */
export function useInfiniteScroll({ disabled, onLoadMore, rootMargin = "240px" }) {
  const [node, setNode] = useState(null);

  useEffect(() => {
    if (!node || disabled) return undefined;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries.some((e) => e.isIntersecting)) {
          onLoadMore?.();
        }
      },
      { root: null, rootMargin, threshold: 0 }
    );

    observer.observe(node);
    return () => observer.disconnect();
  }, [node, disabled, onLoadMore, rootMargin]);

  return setNode;
}
